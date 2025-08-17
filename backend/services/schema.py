"""Schema service for providing sanitized database schema information."""

from typing import Dict, List, Any
from core.logging import get_logger

logger = get_logger(__name__)


class SchemaService:
    """Service for providing sanitized database schema information to the LLM."""
    
    @staticmethod
    def get_sanitized_schema() -> Dict[str, Any]:
        """Return a sanitized view of the analytical schema."""
        
        schema = {
            "tables": [
                {
                    "name": "fact_measure",
                    "description": "Main fact table containing all measurements",
                    "columns": [
                        {"name": "id", "type": "bigint", "description": "Primary key"},
                        {"name": "indicator_id", "type": "int", "description": "Foreign key to dim_indicator"},
                        {"name": "geo_id", "type": "int", "description": "Foreign key to dim_geo"},
                        {"name": "time_id", "type": "int", "description": "Foreign key to dim_time"},
                        {"name": "value", "type": "numeric", "description": "The measured value"},
                        {"name": "quality_flag", "type": "text", "description": "Data quality indicator"}
                    ]
                },
                {
                    "name": "extended_fact_measure",
                    "description": "Extended fact table containing government dataset measurements",
                    "columns": [
                        {"name": "id", "type": "bigint", "description": "Primary key"},
                        {"name": "dataset_id", "type": "int", "description": "Foreign key to dataset_registry"},
                        {"name": "indicator_id", "type": "int", "description": "Foreign key to dataset_indicator"},
                        {"name": "geo_id", "type": "int", "description": "Geographic location reference"},
                        {"name": "time_id", "type": "int", "description": "Time period reference"},
                        {"name": "numeric_value", "type": "numeric", "description": "Numeric measurement value"},
                        {"name": "text_value", "type": "text", "description": "Text measurement value"},
                        {"name": "quality_flag", "type": "text", "description": "Data quality indicator"},
                        {"name": "ingestion_timestamp", "type": "date", "description": "When data was ingested"}
                    ]
                },
                {
                    "name": "dataset_registry",
                    "description": "Registry of all available government datasets",
                    "columns": [
                        {"name": "id", "type": "int", "description": "Primary key"},
                        {"name": "slug", "type": "text", "description": "Unique dataset identifier"},
                        {"name": "title", "type": "text", "description": "Dataset title"},
                        {"name": "category", "type": "text", "description": "Dataset category (Economic, Infrastructure, Social, Environmental)"},
                        {"name": "geographic_level", "type": "text", "description": "Geographic scope (National, State, District)"},
                        {"name": "time_granularity", "type": "text", "description": "Time granularity (Annual, Monthly, Quarterly)"},
                        {"name": "source_department", "type": "text", "description": "Source government department"}
                    ]
                },
                {
                    "name": "dataset_indicator",
                    "description": "Indicators/fields available in each dataset",
                    "columns": [
                        {"name": "id", "type": "int", "description": "Primary key"},
                        {"name": "dataset_id", "type": "int", "description": "Foreign key to dataset_registry"},
                        {"name": "field_name", "type": "text", "description": "Original field name in dataset"},
                        {"name": "display_name", "type": "text", "description": "Human-readable display name"},
                        {"name": "data_type", "type": "text", "description": "Data type (numeric, text, date)"},
                        {"name": "unit", "type": "text", "description": "Unit of measurement"},
                        {"name": "description", "type": "text", "description": "Field description"},
                        {"name": "is_measure", "type": "boolean", "description": "Whether this is a measurable value"}
                    ]
                },
                {
                    "name": "dim_time",
                    "description": "Time dimension table",
                    "columns": [
                        {"name": "id", "type": "int", "description": "Primary key"},
                        {"name": "date", "type": "date", "description": "Full date"},
                        {"name": "year", "type": "int", "description": "Year"},
                        {"name": "quarter", "type": "int", "description": "Quarter (1-4)"},
                        {"name": "month", "type": "int", "description": "Month (1-12)"}
                    ]
                },
                {
                    "name": "dim_geo",
                    "description": "Geography dimension table",
                    "columns": [
                        {"name": "id", "type": "int", "description": "Primary key"},
                        {"name": "state", "type": "text", "description": "State name"},
                        {"name": "district", "type": "text", "description": "District name"},
                        {"name": "zone", "type": "text", "description": "Zone name"},
                        {"name": "ward", "type": "text", "description": "Ward name"},
                        {"name": "level", "type": "text", "description": "Geographic level (state/district/zone/ward)"}
                    ]
                },
                {
                    "name": "dim_indicator",
                    "description": "Indicator dimension table",
                    "columns": [
                        {"name": "id", "type": "int", "description": "Primary key"},
                        {"name": "slug", "type": "text", "description": "Unique identifier slug"},
                        {"name": "title", "type": "text", "description": "Human-readable title"},
                        {"name": "unit", "type": "text", "description": "Unit of measurement"},
                        {"name": "category", "type": "text", "description": "Indicator category"},
                        {"name": "description", "type": "text", "description": "Detailed description"},
                        {"name": "default_agg", "type": "text", "description": "Default aggregation (SUM/AVG/MAX/MIN)"}
                    ]
                }
            ],
            "joins": [
                {
                    "from": "fact_measure.indicator_id",
                    "to": "dim_indicator.id",
                    "description": "Link measurements to indicators"
                },
                {
                    "from": "fact_measure.time_id",
                    "to": "dim_time.id",
                    "description": "Link measurements to time periods"
                },
                {
                    "from": "fact_measure.geo_id",
                    "to": "dim_geo.id",
                    "description": "Link measurements to geographic locations"
                },
                {
                    "from": "extended_fact_measure.dataset_id",
                    "to": "dataset_registry.id",
                    "description": "Link government dataset measurements to datasets"
                },
                {
                    "from": "extended_fact_measure.indicator_id",
                    "to": "dataset_indicator.id",
                    "description": "Link government dataset measurements to indicators"
                },
                {
                    "from": "dataset_indicator.dataset_id",
                    "to": "dataset_registry.id",
                    "description": "Link indicators to their datasets"
                }
            ],
            "sample_queries": [
                {
                    "description": "Get all forest cover data for a specific district",
                    "sql": """
                    SELECT 
                        i.title as indicator,
                        g.district,
                        t.year,
                        f.value,
                        i.unit
                    FROM fact_measure f
                    JOIN dim_indicator i ON f.indicator_id = i.id
                    JOIN dim_geo g ON f.geo_id = g.id
                    JOIN dim_time t ON f.time_id = t.id
                    WHERE i.slug = 'forest_cover_area'
                    AND g.district = 'Ranchi'
                    ORDER BY t.year
                    """
                },
                {
                    "description": "Get GDP data from government datasets",
                    "sql": """
                    SELECT 
                        dr.title as dataset,
                        di.display_name as indicator,
                        efm.numeric_value as value,
                        di.unit,
                        efm.ingestion_timestamp
                    FROM extended_fact_measure efm
                    JOIN dataset_registry dr ON efm.dataset_id = dr.id
                    JOIN dataset_indicator di ON efm.indicator_id = di.id
                    WHERE dr.category = 'Economic'
                    AND di.display_name ILIKE '%GDP%'
                    ORDER BY efm.ingestion_timestamp DESC
                    LIMIT 50
                    """
                },
                {
                    "description": "List all available government datasets",
                    "sql": """
                    SELECT 
                        dr.title,
                        dr.category,
                        dr.geographic_level,
                        dr.time_granularity,
                        dr.source_department,
                        COUNT(DISTINCT di.id) as indicator_count
                    FROM dataset_registry dr
                    LEFT JOIN dataset_indicator di ON dr.id = di.dataset_id
                    WHERE dr.is_active = true
                    GROUP BY dr.id, dr.title, dr.category, dr.geographic_level, dr.time_granularity, dr.source_department
                    ORDER BY dr.category, dr.title
                    LIMIT 50
                    """
                }
            ]
        }
        
        return schema
