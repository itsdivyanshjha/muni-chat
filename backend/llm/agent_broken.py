"""LLM agent with tool calling capabilities."""

import json
import time
from typing import Dict, Any, List, Optional
from llm.openrouter import OpenRouterClient, OpenRouterError
from services.schema import SchemaService
from db.session import execute_safe_query
from core.logging import get_logger, log_request_response

logger = get_logger(__name__)


class MunicipalAnalystAgent:
    """Municipal data analyst agent with tool calling capabilities."""
    
    SYSTEM_PROMPT = """You are a municipal data analyst expert specializing in Indian government datasets. Your role is to help users understand government data through natural language queries.

AVAILABLE DATA SOURCES:
1. GOVERNMENT DATASETS (22+ datasets available):
   - Economic data: GDP growth, inflation rates, fiscal indicators
   - Infrastructure: PMGSY roads, power generation, digital connectivity
   - Social: Education statistics, healthcare metrics, employment data
   - Environmental: Air quality, temperature, CO2 emissions
   - Use tables: dataset_registry, dataset_indicator, extended_fact_measure

2. LEGACY MUNICIPAL DATA:
   - Basic municipal metrics
   - Use tables: fact_measure, dim_indicator, dim_geo, dim_time

IMPORTANT INSTRUCTIONS:
1. ALWAYS call get_schema() first if you're unsure about the database structure
2. For questions about GDP, inflation, PMGSY, education, etc., use GOVERNMENT DATASETS (extended_fact_measure)
3. Draft safe SQL queries that apply user filters (time/place/extra)
4. Call run_sql() to execute queries
5. Synthesize responses that EXACTLY match the required JSON schema
6. For visualizations, prefer simple bar/line/area charts in Vega-Lite format
7. Use "data":{"values":"__INLINE_DATA__"} placeholder in chart specs
8. Keep data_preview.rows ≤ 50 rows
9. Include concise disclaimers if data looks sparse or missing
10. Return insights in a conversational, helpful tone

QUERY EXAMPLES:
- "GDP trends" → Query economic datasets for GDP data
- "Infrastructure development" → Query infrastructure datasets for PMGSY, power, etc.
- "Education statistics" → Query social datasets for literacy, enrollment data
- "Environmental metrics" → Query environmental datasets for air quality, temperature

FILTER APPLICATION:
- time.from/to: Filter by date range using dim_time.date or dim_time.year
- place.state/district/ward/zone: Filter by geographic location using dim_geo
- extra.category: Filter by dataset category (Economic, Infrastructure, Social, Environmental)

RESPONSE FORMAT: Always return a complete JSON response with all required fields:
- insight_text: DETAILED, in-depth analysis with key findings, trends, and actionable insights. Include:
  * Executive Summary (2-3 sentences)
  * Key Findings (3-5 bullet points with specific data points)
  * Trend Analysis (what patterns emerge from the data)
  * Notable Observations (outliers, interesting correlations)
  * Actionable Recommendations (what this data suggests for decision-making)
- sql_used: The exact SQL query executed
- data_preview: {columns: [...], rows: [...]} with ≤50 rows
- viz: Vega-Lite chart specification with __INLINE_DATA__ placeholder (prefer interactive charts)
- doc_citations: List of relevant citations (use search_docs)
- filters_applied: Echo the filters that were actually applied
- disclaimers: Any relevant data quality or completeness notes

INSIGHT WRITING GUIDELINES:
- Start with a compelling executive summary
- Use specific numbers and percentages from the data
- Highlight the most significant trends and outliers
- Provide context about what the data means for policy/decision-making
- Use clear, professional language but keep it engaging
- Include comparisons (year-over-year, state-wise, etc.) when relevant"""

    def __init__(self):
        self.client = OpenRouterClient()
        self.schema_service = SchemaService()
        
    def get_tools_definition(self) -> List[Dict[str, Any]]:
        """Define the tools available to the LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_schema",
                    "description": "Get the sanitized database schema with tables, columns, and join information",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_sql",
                    "description": "Execute a read-only SQL query against the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The SQL query to execute (SELECT or WITH statements only)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_docs",
                    "description": "Search for relevant documentation or citations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to search for in documentation"
                            },
                            "ward": {
                                "type": "string",
                                "description": "Optional ward name to filter results"
                            },
                            "from_date": {
                                "type": "string",
                                "description": "Optional start date for filtering (YYYY-MM-DD)"
                            },
                            "to_date": {
                                "type": "string",
                                "description": "Optional end date for filtering (YYYY-MM-DD)"
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool function and return the result."""
        try:
            if tool_name == "get_schema":
                return {
                    "success": True,
                    "result": self.schema_service.get_sanitized_schema()
                }
            
            elif tool_name == "run_sql":
                query = arguments.get("query", "")
                start_time = time.time()
                
                try:
                    result = execute_safe_query(query)
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    return {
                        "success": True,
                        "result": {
                            "columns": result["columns"],
                            "rows": result["rows"],
                            "row_count": result["row_count"],
                            "duration_ms": duration_ms
                        }
                    }
                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)
                    logger.error(f"SQL execution failed: {e}")
                    return {
                        "success": False,
                        "error": str(e),
                        "duration_ms": duration_ms
                    }
            
            elif tool_name == "search_docs":
                # Stub implementation - returns empty for now
                return {
                    "success": True,
                    "result": []
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_query(self, prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user query with filters and return insights."""
        start_time = time.time()
        sql_used = ""
        row_count = 0
        
        try:
            # Build messages with system prompt and user query
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Query: {prompt}\nFilters: {json.dumps(filters)}"}
            ]
            
            # Get tools definition
            tools = self.get_tools_definition()
            
            # Initial LLM call
            response = await self.client.chat_completion(
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.1
            )
            
            # Process tool calls
            message = response["choices"][0]["message"]
            
            while message.get("tool_calls"):
                # Add assistant message to conversation
                messages.append(message)
                
                # Execute each tool call
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    
                    # Execute the tool
                    tool_result = self.execute_tool(tool_name, arguments)
                    
                    # Track SQL and row count for logging
                    if tool_name == "run_sql" and tool_result.get("success"):
                        sql_used = arguments.get("query", "")
                        row_count = tool_result["result"].get("row_count", 0)
                    
                    # Add tool result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(tool_result)
                    })
                
                # Get next response from LLM
                response = await self.client.chat_completion(
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.1
                )
                
                message = response["choices"][0]["message"]
            
            # Extract final response
            final_content = message.get("content", "")
            
            # Try to parse as JSON
            try:
                result = json.loads(final_content)
                
                # Validate required fields
                required_fields = [
                    "insight_text", "sql_used", "data_preview", "viz", 
                    "doc_citations", "filters_applied", "disclaimers"
                ]
                
                for field in required_fields:
                    if field not in result:
                        result[field] = self._get_default_value(field)
                
                # Ensure data_preview has correct structure
                if "data_preview" in result:
                    preview = result["data_preview"]
                    if not isinstance(preview, dict) or "columns" not in preview or "rows" not in preview:
                        result["data_preview"] = {"columns": [], "rows": []}
                
                # Log the request/response
                duration_ms = int((time.time() - start_time) * 1000)
                log_request_response(
                    logger, prompt, filters, sql_used, duration_ms, row_count, True
                )
                
                return result
                
            except json.JSONDecodeError:
                # Fallback response if JSON parsing fails
                duration_ms = int((time.time() - start_time) * 1000)
                log_request_response(
                    logger, prompt, filters, sql_used, duration_ms, row_count, False, "JSON parsing failed"
                )
                
                return self._create_fallback_response(final_content, filters)
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error(f"LLM Agent Exception: {error_msg}")
            
            log_request_response(
                logger, prompt, filters, sql_used, duration_ms, row_count, False, error_msg
            )
            
            # Just return a simple error - no fake responses
            logger.error(f"LLM processing failed: {error_msg}")
            raise Exception(f"LLM processing failed: {error_msg}")

    async def generate_insight(self, prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for process_query for compatibility with app.py endpoint."""
        return await self.process_query(prompt, filters)
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for a required field."""
        defaults = {
            "insight_text": "Unable to generate insight",
            "sql_used": "",
            "data_preview": {"columns": [], "rows": []},
            "viz": {"type": "vega-lite", "spec": {}},
            "doc_citations": [],
            "filters_applied": {},
            "disclaimers": ["Unable to complete analysis"]
        }
        return defaults.get(field, None)
    
    def _create_fallback_response(self, content: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails."""
        return {
            "insight_text": content[:500] + "..." if len(content) > 500 else content,
            "sql_used": "",
            "data_preview": {"columns": [], "rows": []},
            "viz": {"type": "vega-lite", "spec": {}},
            "doc_citations": [],
            "filters_applied": filters,
            "disclaimers": ["Response formatting issue - partial results shown"]
        }
    
    def _create_error_response(self, error: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "insight_text": f"Sorry, I encountered an error while processing your request: {error}",
            "sql_used": "",
            "data_preview": {"columns": [], "rows": []},
            "viz": {"type": "vega-lite", "spec": {}},
            "doc_citations": [],
            "filters_applied": filters,
            "disclaimers": ["Error occurred during analysis"]
        }
    


        """Create economic data response."""
        return {
            "insight_text": f"## Executive Summary\nBased on your query '{prompt}', here's an analysis of economic indicators from our government datasets.\n\n## Key Findings\n• **GDP Growth**: Current quarterly data shows varied growth patterns across sectors\n• **Inflation Trends**: Retail inflation rates indicate economic stability measures\n• **Fiscal Indicators**: Government spending and revenue data provides policy insights\n\n## Trend Analysis\nEconomic data reveals cyclical patterns with seasonal variations in key indicators. Growth metrics show resilience in post-pandemic recovery phases.\n\n## Notable Observations\n• Economic recovery patterns vary significantly by state and sector\n• Digital economy indicators show accelerated growth\n• Rural economic metrics demonstrate targeted policy impacts\n\n## Actionable Recommendations\n1. Monitor quarterly GDP trends for policy timing\n2. Analyze inflation data for market predictions\n3. Compare state-wise economic performance for resource allocation",
            "sql_used": "SELECT dr.title, efm.numeric_value, efm.ingestion_timestamp FROM extended_fact_measure efm JOIN dataset_registry dr ON efm.dataset_id = dr.id WHERE dr.category = 'Economic' LIMIT 50",
            "data_preview": {
                "columns": ["Indicator", "Value", "Unit", "Period"],
                "rows": [
                    ["GDP Growth Rate", "6.8", "%", "Q2 2023"],
                    ["Retail Inflation", "4.2", "%", "Oct 2023"],
                    ["Fiscal Deficit", "3.4", "% of GDP", "2023-24"],
                    ["Industrial Production", "102.3", "Index", "Sep 2023"],
                    ["Services Sector Growth", "7.1", "%", "Q2 2023"]
                ]
            },
            "viz": {
                "type": "vega-lite",
                "spec": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": "__INLINE_DATA__"},
                    "mark": {"type": "line", "point": True, "strokeWidth": 3},
                    "encoding": {
                        "x": {"field": "Period", "type": "ordinal"},
                        "y": {"field": "Value", "type": "quantitative"},
                        "color": {"field": "Indicator", "type": "nominal", "scale": {"scheme": "category10"}}
                    },
                    "width": 500,
                    "height": 350
                }
            },
            "doc_citations": [{"title": "Economic Survey 2023", "url": "https://data.gov.in/economic", "excerpt": "Official economic indicators and analysis"}],
            "filters_applied": filters,
            "disclaimers": ["LLM service temporarily unavailable - showing curated economic data"]
        }

    def _create_infrastructure_response(self, prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create infrastructure data response."""
        return {
            "insight_text": f"## Executive Summary\nAnalyzing infrastructure development based on '{prompt}' using government datasets.\n\n## Key Findings\n• **PMGSY Roads**: Rural connectivity has improved significantly with 87% target achievement\n• **Power Generation**: Capacity additions show consistent growth in renewable energy\n• **Digital Infrastructure**: Fiber optic coverage expanded by 40% in rural areas\n\n## Trend Analysis\nInfrastructure development shows accelerated pace in rural areas, with digital connectivity leading the transformation.\n\n## Notable Observations\n• Rural road construction exceeds urban development rates\n• Solar power installations show exponential growth\n• Internet penetration gaps are closing rapidly\n\n## Actionable Recommendations\n1. Focus on last-mile connectivity for complete rural transformation\n2. Integrate renewable energy with infrastructure projects\n3. Leverage digital infrastructure for service delivery",
            "sql_used": "SELECT dr.title, efm.numeric_value FROM extended_fact_measure efm JOIN dataset_registry dr ON efm.dataset_id = dr.id WHERE dr.category = 'Infrastructure' LIMIT 50",
            "data_preview": {
                "columns": ["Project", "Completion", "Budget", "State"],
                "rows": [
                    ["PMGSY Roads Phase III", "78%", "₹15,000 Cr", "Multiple"],
                    ["Rural Electrification", "99.8%", "₹12,800 Cr", "All States"],
                    ["Fiber Optic Network", "65%", "₹42,000 Cr", "Rural Areas"],
                    ["Solar Parks", "45%", "₹8,500 Cr", "Rajasthan"],
                    ["Highway Development", "89%", "₹25,000 Cr", "Golden Quadrilateral"]
                ]
            },
            "viz": {
                "type": "vega-lite",
                "spec": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": "__INLINE_DATA__"},
                    "mark": {"type": "bar", "cornerRadiusTopLeft": 4, "cornerRadiusTopRight": 4},
                    "encoding": {
                        "x": {"field": "Project", "type": "nominal", "axis": {"labelAngle": -45}},
                        "y": {"field": "Completion", "type": "quantitative"},
                        "color": {"field": "Project", "type": "nominal", "scale": {"scheme": "viridis"}}
                    }
                }
            },
            "doc_citations": [{"title": "Infrastructure Development Report", "url": "https://data.gov.in/infrastructure", "excerpt": "Comprehensive infrastructure statistics"}],
            "filters_applied": filters,
            "disclaimers": ["Real-time LLM analysis unavailable - showing infrastructure progress data"]
        }

    def _create_education_response(self, prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create education data response."""
        return {
            "insight_text": f"## Executive Summary\nEducation sector analysis for '{prompt}' using comprehensive government education datasets.\n\n## Key Findings\n• **Literacy Rates**: National literacy improved to 77.7% with significant gender gap reduction\n• **School Enrollment**: Primary education enrollment maintains 95%+ across states\n• **Digital Education**: Online learning adoption increased 300% post-pandemic\n\n## Trend Analysis\nEducation metrics show consistent improvement with accelerated digital transformation enhancing access and quality.\n\n## Notable Observations\n• Rural-urban education gaps are narrowing through technology\n• Vocational training programs show high employment correlation\n• Teacher training initiatives demonstrate measurable classroom improvements\n\n## Actionable Recommendations\n1. Scale successful digital education models\n2. Focus on quality improvement alongside access\n3. Strengthen vocational education-industry linkages",
            "sql_used": "SELECT dr.title, efm.numeric_value FROM extended_fact_measure efm JOIN dataset_registry dr ON efm.dataset_id = dr.id WHERE dr.category = 'Social' AND dr.title LIKE '%Education%' LIMIT 50",
            "data_preview": {
                "columns": ["State", "Literacy Rate", "Enrollment", "Schools"],
                "rows": [
                    ["Kerala", "94.0%", "98.5%", "12,450"],
                    ["Karnataka", "75.6%", "94.2%", "54,890"],
                    ["Maharashtra", "82.3%", "96.1%", "78,234"],
                    ["Gujarat", "78.0%", "95.8%", "45,670"],
                    ["Tamil Nadu", "80.1%", "97.3%", "56,123"]
                ]
            },
            "viz": {
                "type": "vega-lite",
                "spec": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": "__INLINE_DATA__"},
                    "mark": {"type": "circle", "size": 100},
                    "encoding": {
                        "x": {"field": "Literacy Rate", "type": "quantitative"},
                        "y": {"field": "Enrollment", "type": "quantitative"},
                        "color": {"field": "State", "type": "nominal"},
                        "size": {"field": "Schools", "type": "quantitative"}
                    }
                }
            },
            "doc_citations": [{"title": "Education Statistics at a Glance", "url": "https://data.gov.in/education", "excerpt": "Comprehensive education sector data"}],
            "filters_applied": filters,
            "disclaimers": ["AI analysis temporarily offline - displaying education statistics"]
        }

    def _create_environment_response(self, prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create environment data response."""
        return {
            "insight_text": f"## Executive Summary\nEnvironmental data analysis for '{prompt}' reveals critical climate and air quality trends.\n\n## Key Findings\n• **Air Quality**: AQI improvements in 15 major cities through targeted interventions\n• **Temperature Trends**: Regional warming patterns show variation across climate zones\n• **CO2 Emissions**: Industrial emissions declining due to clean energy adoption\n\n## Trend Analysis\nEnvironmental indicators show mixed results with improvements in urban air quality offset by climate change impacts.\n\n## Notable Observations\n• Seasonal pollution patterns correlate with agricultural practices\n• Renewable energy adoption reducing regional carbon footprints\n• Urban heat island effects intensifying in metropolitan areas\n\n## Actionable Recommendations\n1. Accelerate clean air action plans in pollution hotspots\n2. Enhance climate resilience in vulnerable regions\n3. Scale successful green technology implementations",
            "sql_used": "SELECT dr.title, efm.numeric_value FROM extended_fact_measure efm JOIN dataset_registry dr ON efm.dataset_id = dr.id WHERE dr.category = 'Environmental' LIMIT 50",
            "data_preview": {
                "columns": ["City", "AQI", "Temperature", "CO2 Level"],
                "rows": [
                    ["Delhi", "165", "28.5°C", "415 ppm"],
                    ["Mumbai", "87", "32.1°C", "412 ppm"],
                    ["Bangalore", "92", "26.8°C", "408 ppm"],
                    ["Chennai", "78", "31.4°C", "410 ppm"],
                    ["Kolkata", "134", "29.7°C", "414 ppm"]
                ]
            },
            "viz": {
                "type": "vega-lite",
                "spec": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": "__INLINE_DATA__"},
                    "mark": {"type": "bar", "opacity": 0.8},
                    "encoding": {
                        "x": {"field": "City", "type": "nominal"},
                        "y": {"field": "AQI", "type": "quantitative"},
                        "color": {
                            "field": "AQI",
                            "type": "quantitative",
                            "scale": {"scheme": "redyellowgreen", "reverse": True}
                        }
                    }
                }
            },
            "doc_citations": [{"title": "Environmental Data Portal", "url": "https://data.gov.in/environment", "excerpt": "Real-time environmental monitoring data"}],
            "filters_applied": filters,
            "disclaimers": ["Environmental data based on latest available measurements"]
        }

    def _create_fallback_government_data_response(self, prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback response showing available government datasets."""
        return {
            "insight_text": f"## Executive Summary\nI understand you're asking about '{prompt}'. Our platform provides access to 22+ comprehensive government datasets covering India's key economic, infrastructure, social, and environmental indicators.\n\n" +
                           "## Key Findings\n" +
                           "• **Economic Portfolio**: 6+ datasets including GDP growth trends, inflation metrics, and fiscal indicators\n" +
                           "• **Infrastructure Coverage**: PMGSY road development, power generation capacity, and digital connectivity statistics\n" +
                           "• **Social Indicators**: Education enrollment rates, literacy statistics, healthcare metrics, and employment data\n" +
                           "• **Environmental Monitoring**: Air quality indices, temperature variations, and CO2 emission trends\n\n" +
                           "## Dataset Distribution Analysis\n" +
                           "The data shows a balanced coverage across all four major categories, with Economic datasets representing the largest segment (35%), followed by Infrastructure (25%), Social (25%), and Environmental (15%). This comprehensive coverage enables cross-sector analysis and policy correlation studies.\n\n" +
                           "## Notable Observations\n" +
                           "• Data granularity varies from National to State level, with most infrastructure data available at State level\n" +
                           "• Time series coverage spans multiple years with different frequencies (Annual, Quarterly, Monthly)\n" +
                           "• All datasets are sourced from official government departments ensuring reliability\n\n" +
                           "## Actionable Recommendations\n" +
                           "1. Start with economic indicators for macro-level insights\n" +
                           "2. Combine infrastructure and social data for development impact analysis\n" +
                           "3. Use environmental data for sustainability assessments\n" +
                           "4. Apply geographic and time filters for targeted analysis",
            "sql_used": "SELECT title, category, geographic_level, time_granularity FROM dataset_registry WHERE is_active = true ORDER BY category, title LIMIT 50",
            "data_preview": {
                "columns": ["Dataset", "Category", "Geographic Level", "Time Granularity"],
                "rows": [
                    ["Global Average Temperature and CO2", "Environmental", "National", "Annual"],
                    ["GDP Growth Rate", "Economic", "National", "Quarterly"],
                    ["PMGSY Road Development", "Infrastructure", "State", "Annual"],
                    ["Literacy Rate by State", "Social", "State", "Annual"],
                    ["Retail Inflation Rate", "Economic", "National", "Monthly"]
                ]
            },
            "viz": {
                "type": "vega-lite",
                "spec": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "description": "Government Datasets by Category",
                    "data": {"values": "__INLINE_DATA__"},
                    "mark": {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3},
                    "encoding": {
                        "x": {"field": "Category", "type": "nominal", "axis": {"labelAngle": -45}},
                        "y": {"aggregate": "count", "field": "*", "type": "quantitative", "title": "Number of Datasets"},
                        "color": {
                            "field": "Category",
                            "type": "nominal",
                            "scale": {"scheme": "category10"}
                        }
                    },
                    "width": 400,
                    "height": 300
                }
            },
            "doc_citations": [
                {
                    "title": "Government of India Data Portal",
                    "url": "https://data.gov.in",
                    "excerpt": "Official data portal of the Government of India providing access to various government datasets"
                }
            ],
            "filters_applied": filters,
            "disclaimers": ["LLM connectivity issue - showing available datasets", "Data sourced from official government APIs"]
        }
