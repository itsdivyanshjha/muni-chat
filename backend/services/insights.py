"""Insights service for orchestrating LLM analysis and response assembly."""

from typing import Dict, Any
from llm.agent import MunicipalAnalystAgent
from core.logging import get_logger
from core.config import settings

logger = get_logger(__name__)


class InsightsService:
    """Service for generating insights from user queries."""
    
    def __init__(self):
        self.agent = MunicipalAnalystAgent()
    
    async def generate_insights(self, prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from a user prompt and filters."""
        try:
            # Validate filters
            validated_filters = self._validate_filters(filters)
            
            # Process the query through the LLM agent
            result = await self.agent.process_query(prompt, validated_filters)
            
            # Post-process the result
            result = self._post_process_result(result, validated_filters)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return self._create_error_response(str(e), filters)
    
    def _validate_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the filters."""
        validated = {
            "time": {
                "from": None,
                "to": None
            },
            "place": {
                "state": None,
                "district": None,
                "ward": None,
                "zone": None
            },
            "extra": {}
        }
        
        # Validate time filters
        if "time" in filters and isinstance(filters["time"], dict):
            time_filter = filters["time"]
            if "from" in time_filter and time_filter["from"]:
                validated["time"]["from"] = str(time_filter["from"])
            if "to" in time_filter and time_filter["to"]:
                validated["time"]["to"] = str(time_filter["to"])
        
        # Validate place filters
        if "place" in filters and isinstance(filters["place"], dict):
            place_filter = filters["place"]
            for key in ["state", "district", "ward", "zone"]:
                if key in place_filter and place_filter[key]:
                    validated["place"][key] = str(place_filter[key])
        
        # Validate extra filters
        if "extra" in filters and isinstance(filters["extra"], dict):
            validated["extra"] = {k: str(v) for k, v in filters["extra"].items() if v}
        
        return validated
    
    def _post_process_result(self, result: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process the LLM result to ensure compliance with API contract."""
        
        # Ensure all required fields are present
        required_fields = {
            "insight_text": "",
            "sql_used": "",
            "data_preview": {"columns": [], "rows": []},
            "viz": {"type": "vega-lite", "spec": {}},
            "doc_citations": [],
            "filters_applied": filters,
            "disclaimers": []
        }
        
        for field, default_value in required_fields.items():
            if field not in result:
                result[field] = default_value
        
        # Ensure data_preview has correct structure
        if not isinstance(result.get("data_preview"), dict):
            result["data_preview"] = {"columns": [], "rows": []}
        
        preview = result["data_preview"]
        if "columns" not in preview:
            preview["columns"] = []
        if "rows" not in preview:
            preview["rows"] = []
        
        # Limit preview rows to max allowed
        if len(preview["rows"]) > settings.max_preview_rows:
            preview["rows"] = preview["rows"][:settings.max_preview_rows]
            if "disclaimers" not in result:
                result["disclaimers"] = []
            result["disclaimers"].append(
                f"Data preview limited to {settings.max_preview_rows} rows"
            )
        
        # Ensure viz has correct structure
        if not isinstance(result.get("viz"), dict):
            result["viz"] = {"type": "vega-lite", "spec": {}}
        
        viz = result["viz"]
        if "type" not in viz:
            viz["type"] = "vega-lite"
        if "spec" not in viz:
            viz["spec"] = {}
        
        # Ensure doc_citations is a list
        if not isinstance(result.get("doc_citations"), list):
            result["doc_citations"] = []
        
        # Ensure disclaimers is a list
        if not isinstance(result.get("disclaimers"), list):
            result["disclaimers"] = []
        
        # Set filters_applied to the validated filters
        result["filters_applied"] = filters
        
        return result
    
    def _create_error_response(self, error: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "insight_text": f"I apologize, but I encountered an error while processing your request: {error}",
            "sql_used": "",
            "data_preview": {"columns": [], "rows": []},
            "viz": {"type": "vega-lite", "spec": {}},
            "doc_citations": [],
            "filters_applied": filters,
            "disclaimers": ["An error occurred during analysis. Please try again with a different query."]
        }
