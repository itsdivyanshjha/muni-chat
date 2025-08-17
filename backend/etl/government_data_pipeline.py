"""Government Data ETL Pipeline for Municipal AI Insights."""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import pandas as pd

from db.models_extended import (
    DatasetRegistry, DatasetIndicator, DataSource, 
    GeographicHierarchy, ExtendedFactMeasure, DataQualityLog
)
from db.session import get_owner_session
from core.config import settings

logger = logging.getLogger(__name__)


class GovernmentDataConnector:
    """Connector for government data portal APIs."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.data.gov.in"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_dataset(self, resource_id: str, format: str = "json", 
                           limit: int = 1000, offset: int = 0, 
                           filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch data from government portal API."""
        
        url = f"{self.base_url}/resource/{resource_id}"
        params = {
            "api-key": self.api_key,
            "format": format,
            "limit": limit,
            "offset": offset
        }
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    params[f"filters[{key}]"] = value
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    if format == "json":
                        return await response.json()
                    elif format == "csv":
                        return await response.text()
                    else:
                        return await response.text()
                else:
                    logger.error(f"API request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None


class DataProcessor:
    """Processes and transforms government data."""
    
    @staticmethod
    def detect_schema(data_sample: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Auto-detect schema from data sample."""
        if not data_sample:
            return {}
        
        schema = {}
        for field_name, value in data_sample[0].items():
            field_info = {
                "data_type": DataProcessor._infer_data_type(value),
                "is_filterable": True,  # Most fields can be filtered
                "is_measure": DataProcessor._is_measure_field(field_name, value)
            }
            
            # Add units for common fields
            if "percentage" in field_name.lower() or "%" in str(value):
                field_info["unit"] = "percentage"
            elif "crore" in field_name.lower() or "lakh" in field_name.lower():
                field_info["unit"] = "crores"
            elif "km" in field_name.lower():
                field_info["unit"] = "kilometers"
            
            schema[field_name] = field_info
        
        return schema
    
    @staticmethod
    def _infer_data_type(value: Any) -> str:
        """Infer data type from value."""
        if isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, str):
            # Try to parse as date
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return "date"
            except ValueError:
                try:
                    datetime.strptime(value, "%Y")
                    return "date"
                except ValueError:
                    return "string"
        else:
            return "string"
    
    @staticmethod
    def _is_measure_field(field_name: str, value: Any) -> bool:
        """Determine if field is a measurable value."""
        measure_indicators = [
            "value", "amount", "cost", "length", "area", "population",
            "percentage", "rate", "index", "number", "count", "quantity"
        ]
        
        field_lower = field_name.lower()
        return any(indicator in field_lower for indicator in measure_indicators)
    
    @staticmethod
    def normalize_geographic_names(name: str) -> str:
        """Normalize geographic names for consistency."""
        # Common variations and abbreviations
        variations = {
            "andhra pradesh": "Andhra Pradesh",
            "arunachal pradesh": "Arunachal Pradesh",
            "madhya pradesh": "Madhya Pradesh",
            "uttar pradesh": "Uttar Pradesh",
            "west bengal": "West Bengal",
            "tamil nadu": "Tamil Nadu",
            "jammu & kashmir": "Jammu and Kashmir",
            "j&k": "Jammu and Kashmir",
            "delhi": "Delhi",
            "nct of delhi": "Delhi",
            "jharkhand": "Jharkhand"
        }
        
        normalized = name.strip().lower()
        return variations.get(normalized, name.title())


class GovernmentDataETL:
    """Main ETL pipeline for government datasets."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.connector = None
        self.processor = DataProcessor()
        
        # Dataset definitions based on your list
        self.dataset_definitions = self._get_dataset_definitions()
    
    def _get_dataset_definitions(self) -> List[Dict[str, Any]]:
        """Define all available datasets with metadata."""
        return [
            {
                "resource_id": "58287031-8137-473d-bc65-5043b657a3fb",
                "slug": "global_temperature_co2",
                "title": "Global Average Temperature and Atmosphere concentration of Carbon Dioxide",
                "category": "Environmental",
                "subcategory": "Climate Change",
                "geographic_level": "national",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Environment"
            },
            {
                "resource_id": "0cde42d3-5f49-4d2a-996c-4dfc4b2e2596",
                "slug": "state_tax_shares",
                "title": "State-wise Share of Union Taxes and Duties released to State Governments",
                "category": "Economic",
                "subcategory": "Fiscal Policy",
                "geographic_level": "state",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Finance"
            },
            {
                "resource_id": "352b3616-9d3d-42e5-80af-7d21a2a53fab",
                "slug": "retail_inflation_cpi",
                "title": "Year-wise Retail Inflation Rate based on CPI-C",
                "category": "Economic",
                "subcategory": "Inflation",
                "geographic_level": "national",
                "time_granularity": "annual",
                "update_frequency": "monthly",
                "source_department": "Ministry of Statistics"
            },
            {
                "resource_id": "4f7ec454-6b2f-4adc-a98d-6681ece6f764",
                "slug": "msme_credit_guarantee",
                "title": "State/UTs-wise details of Credit Guarantee Scheme for Micro and Small Enterprises",
                "category": "Economic",
                "subcategory": "MSME",
                "geographic_level": "state",
                "time_granularity": "annual",
                "update_frequency": "quarterly",
                "source_department": "Ministry of MSME"
            },
            {
                "resource_id": "a56b86d1-f00e-4ee4-ab08-5b5367b3fab2",
                "slug": "gdp_quarterly_estimates",
                "title": "Quarterly Estimates of GDP at Constant (2011-12) Prices",
                "category": "Economic",
                "subcategory": "GDP",
                "geographic_level": "national",
                "time_granularity": "quarterly",
                "update_frequency": "quarterly",
                "source_department": "Ministry of Statistics"
            },
            {
                "resource_id": "8ab58913-a047-42bc-a1a7-38fc542ee7f6",
                "slug": "jss_training_data",
                "title": "State/UT-wise Training Data under Jan Shikshan Sansthan (JSS)",
                "category": "Social",
                "subcategory": "Education",
                "geographic_level": "state",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Education"
            },
            {
                "resource_id": "1b2be8c0-53ba-4e7c-8a7b-ff2f72e79eb8",
                "slug": "water_supply_schemes",
                "title": "Details of various Water supply Distribution/Improvement schemes in ULBs",
                "category": "Infrastructure",
                "subcategory": "Water Supply",
                "geographic_level": "district",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Housing and Urban Affairs"
            },
            {
                "resource_id": "a2b1ef7d-259c-4ef0-92d0-11c1ed77ae14",
                "slug": "csc_service_centres",
                "title": "Details of CSC Service Centre Agencies (SCA) and its Centres/Counters",
                "category": "Infrastructure",
                "subcategory": "Digital Services",
                "geographic_level": "district",
                "time_granularity": "annual",
                "update_frequency": "quarterly",
                "source_department": "Ministry of Electronics and IT"
            },
            {
                "resource_id": "41fb8750-5afa-4395-a895-19d3f5015c27",
                "slug": "state_cpi_rural_urban",
                "title": "State Level Consumer Price Index (Rural/Urban) upto May-2021",
                "category": "Economic",
                "subcategory": "Inflation",
                "geographic_level": "state",
                "time_granularity": "monthly",
                "update_frequency": "monthly",
                "source_department": "Ministry of Statistics"
            },
            {
                "resource_id": "08ae564d-cad3-42a0-b100-a6f56c37b4b9",
                "slug": "national_highways_length",
                "title": "Length of National Highways in India-State-wise",
                "category": "Infrastructure",
                "subcategory": "Transportation",
                "geographic_level": "state",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Road Transport"
            },
            {
                "resource_id": "88348278-0099-4b9c-87ca-253e195d72b9",
                "slug": "principal_commodity_imports",
                "title": "Principal Commodity wise Import for the year 2022-23",
                "category": "Economic",
                "subcategory": "Trade",
                "geographic_level": "national",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Commerce"
            },
            {
                "resource_id": "e3d59565-6bd0-4871-8600-cda68383018b",
                "slug": "state_crime_ipc",
                "title": "State/UT & Crime Head-wise IPC Crimes during 2018",
                "category": "Social",
                "subcategory": "Crime",
                "geographic_level": "state",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Home Affairs"
            },
            {
                "resource_id": "1471b575-da71-48f5-b635-f376195e3e86",
                "slug": "literacy_rate_india",
                "title": "Literacy Rate In India (NSSO And RGI)",
                "category": "Social",
                "subcategory": "Education",
                "geographic_level": "state",
                "time_granularity": "decadal",
                "update_frequency": "decadal",
                "source_department": "Ministry of Education"
            },
            {
                "resource_id": "3e07efd9-3ced-4c65-909c-6ca792daab83",
                "slug": "land_utilization_pattern",
                "title": "Pattern of Land Utilisation",
                "category": "Environmental",
                "subcategory": "Land Use",
                "geographic_level": "national",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Agriculture"
            },
            {
                "resource_id": "09a191c9-3b2a-44ac-8d25-02475f83e723",
                "slug": "state_cpi_april_2023",
                "title": "State Level Consumer Price Index (Rural/Urban) upto April 2023",
                "category": "Economic",
                "subcategory": "Inflation",
                "geographic_level": "state",
                "time_granularity": "monthly",
                "update_frequency": "monthly",
                "source_department": "Ministry of Statistics"
            },
            {
                "resource_id": "31452ba8-e573-4e3e-9799-e20431030eb8",
                "slug": "petrochemical_imports",
                "title": "Imports of Major Petrochemical - Product wise / Group wise",
                "category": "Economic",
                "subcategory": "Trade",
                "geographic_level": "national",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Chemicals"
            },
            {
                "resource_id": "6b0af3dd-3aa5-47aa-b83c-b4d68d89a9b4",
                "slug": "petrochemical_exports",
                "title": "Exports of Major Petrochemical - Product wise / Group wise",
                "category": "Economic",
                "subcategory": "Trade",
                "geographic_level": "national",
                "time_granularity": "annual",
                "update_frequency": "annual",
                "source_department": "Ministry of Chemicals"
            },
            {
                "resource_id": "829137af-5e90-4400-bffe-5d65b66e5956",
                "slug": "steel_production_consumption",
                "title": "Production, Consumption, Import and Export Data of Steel",
                "category": "Economic",
                "subcategory": "Industry",
                "geographic_level": "national",
                "time_granularity": "monthly",
                "update_frequency": "monthly",
                "source_department": "Ministry of Steel"
            },
            {
                "resource_id": "8b68ae56-84cf-4728-a0a6-1be11028dea7",
                "slug": "msme_udyam_registrations",
                "title": "List of MSME Registered Units under UDYAM",
                "category": "Economic",
                "subcategory": "MSME",
                "geographic_level": "district",
                "time_granularity": "annual",
                "update_frequency": "monthly",
                "source_department": "Ministry of MSME"
            },
            {
                "resource_id": "f29cc023-499c-44f2-8521-aaf21108f334",
                "slug": "quarterly_employment_survey",
                "title": "Sector wise Estimated Number of Workers under Quarterly Employment Survey",
                "category": "Social",
                "subcategory": "Employment",
                "geographic_level": "national",
                "time_granularity": "quarterly",
                "update_frequency": "quarterly",
                "source_department": "Ministry of Labour"
            },
            {
                "resource_id": "d4361151-6d41-43c7-98cd-9a6cd90b5ca4",
                "slug": "pmgsy_progress",
                "title": "Physical & Financial Progress of Pradhan Mantri Gram Sadak Yojna (PMGSY)",
                "category": "Infrastructure",
                "subcategory": "Rural Roads",
                "geographic_level": "district",
                "time_granularity": "annual",
                "update_frequency": "monthly",
                "source_department": "Ministry of Rural Development"
            },
            {
                "resource_id": "ee03643a-ee4c-48c2-ac30-9f2ff26ab722",
                "slug": "mgnrega_district_data",
                "title": "District-wise MGNREGA Data at a Glance",
                "category": "Social",
                "subcategory": "Employment",
                "geographic_level": "district",
                "time_granularity": "annual",
                "update_frequency": "monthly",
                "source_department": "Ministry of Rural Development"
            }
        ]
    
    async def initialize_datasets(self):
        """Initialize dataset registry in database."""
        async with GovernmentDataConnector(self.api_key) as connector:
            self.connector = connector
            
            # Get database session
            engine = create_engine(settings.database_url)
            with Session(engine) as session:
                for dataset_def in self.dataset_definitions:
                    # Check if dataset already exists
                    existing = session.query(DatasetRegistry).filter_by(
                        resource_id=dataset_def["resource_id"]
                    ).first()
                    
                    if not existing:
                        # Create new dataset
                        dataset = DatasetRegistry(
                            resource_id=dataset_def["resource_id"],
                            slug=dataset_def["slug"],
                            title=dataset_def["title"],
                            category=dataset_def["category"],
                            subcategory=dataset_def["subcategory"],
                            api_endpoint=f"/resource/{dataset_def['resource_id']}",
                            api_key_required=True,
                            supported_formats=["json", "xml", "csv"],
                            geographic_level=dataset_def["geographic_level"],
                            time_granularity=dataset_def["time_granularity"],
                            update_frequency=dataset_def["update_frequency"],
                            source_department=dataset_def["source_department"],
                            is_active=True
                        )
                        
                        session.add(dataset)
                        session.commit()
                        logger.info(f"Registered dataset: {dataset_def['title']}")
                    else:
                        logger.info(f"Dataset already exists: {dataset_def['title']}")
    
    async def ingest_dataset(self, resource_id: str, limit: int = 1000):
        """Ingest data for a specific dataset."""
        if not self.connector:
            async with GovernmentDataConnector(self.api_key) as connector:
                self.connector = connector
        
        # Fetch data
        data = await self.connector.fetch_dataset(resource_id, format="json", limit=limit)
        if not data:
            logger.error(f"Failed to fetch data for resource: {resource_id}")
            return
        
        # Process data
        records = data.get("records", [])
        if not records:
            logger.warning(f"No records found for resource: {resource_id}")
            return
        
        # Detect schema
        schema = self.processor.detect_schema(records[:10])  # Sample for schema detection
        
        # Process records
        processed_records = []
        for record in records:
            processed_record = self._process_record(record, schema)
            if processed_record:
                processed_records.append(processed_record)
        
        # Store in database
        await self._store_processed_data(resource_id, processed_records, schema)
        
        logger.info(f"Successfully processed {len(processed_records)} records for resource: {resource_id}")
    
    def _process_record(self, record: Dict[str, Any], schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual record according to schema."""
        try:
            processed = {}
            for field_name, field_info in schema.items():
                value = record.get(field_name)
                if value is not None:
                    processed[field_name] = {
                        "value": value,
                        "data_type": field_info["data_type"],
                        "unit": field_info.get("unit"),
                        "is_measure": field_info["is_measure"]
                    }
            
            return processed
        except Exception as e:
            logger.error(f"Error processing record: {e}")
            return None
    
    async def _store_processed_data(self, resource_id: str, records: List[Dict[str, Any]], 
                                   schema: Dict[str, Any]):
        """Store processed data in the warehouse."""
        # This would integrate with your existing warehouse structure
        # For now, we'll log the processed data
        logger.info(f"Would store {len(records)} records for {resource_id}")
        logger.info(f"Schema detected: {json.dumps(schema, indent=2)}")


async def main():
    """Main function to run the ETL pipeline."""
    api_key = "579b464db66ec23bdd00000106337f18059d41867b7729cfd2ea081f"
    
    etl = GovernmentDataETL(api_key)
    
    # Initialize datasets
    await etl.initialize_datasets()
    
    # Ingest a sample dataset
    await etl.ingest_dataset("a56b86d1-f00e-4ee4-ab08-5b5367b3fab2", limit=100)


if __name__ == "__main__":
    asyncio.run(main())
