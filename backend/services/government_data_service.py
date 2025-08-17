"""Service layer for government datasets integration."""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
import json

from db.models_extended import (
    DatasetRegistry, DatasetIndicator, DataSource, 
    GeographicHierarchy, ExtendedFactMeasure, DataQualityLog
)
from db.session import get_owner_session
from core.config import settings

logger = logging.getLogger(__name__)


class GovernmentDataService:
    """Service for managing government datasets."""
    
    def __init__(self):
        self.engine = create_engine(settings.database_url)
    
    def get_all_datasets(self) -> List[Dict[str, Any]]:
        """Get all registered datasets with metadata."""
        with Session(self.engine) as session:
            datasets = session.query(DatasetRegistry).filter_by(is_active=True).all()
            
            result = []
            for dataset in datasets:
                # Get indicators count
                indicators_count = session.query(DatasetIndicator).filter_by(
                    dataset_id=dataset.id
                ).count()
                
                dataset_data = {
                    "id": dataset.id,
                    "slug": dataset.slug,
                    "title": dataset.title,
                    "description": dataset.description,
                    "category": dataset.category,
                    "subcategory": dataset.subcategory,
                    "geographic_level": dataset.geographic_level,
                    "time_granularity": dataset.time_granularity,
                    "update_frequency": dataset.update_frequency,
                    "source_department": dataset.source_department,
                    "last_updated": dataset.last_updated.isoformat() if dataset.last_updated else None,
                    "is_active": dataset.is_active,
                    "indicators_count": indicators_count,
                    "supported_formats": dataset.supported_formats
                }
                result.append(dataset_data)
            
            return result
    
    def get_dataset_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get specific dataset by slug."""
        with Session(self.engine) as session:
            dataset = session.query(DatasetRegistry).filter_by(slug=slug, is_active=True).first()
            
            if not dataset:
                return None
            
            # Get indicators
            indicators = session.query(DatasetIndicator).filter_by(dataset_id=dataset.id).all()
            indicators_data = []
            for indicator in indicators:
                indicators_data.append({
                    "id": indicator.id,
                    "field_name": indicator.field_name,
                    "display_name": indicator.display_name,
                    "data_type": indicator.data_type,
                    "unit": indicator.unit,
                    "description": indicator.description,
                    "is_filterable": indicator.is_filterable,
                    "is_measure": indicator.is_measure
                })
            
            # Get data sources
            sources = session.query(DataSource).filter_by(dataset_id=dataset.id).all()
            sources_data = []
            for source in sources:
                sources_data.append({
                    "id": source.id,
                    "source_type": source.source_type,
                    "source_url": source.source_url,
                    "last_sync": source.last_sync.isoformat() if source.last_sync else None,
                    "sync_status": source.sync_status,
                    "records_count": source.records_count
                })
            
            return {
                "id": dataset.id,
                "slug": dataset.slug,
                "title": dataset.title,
                "description": dataset.description,
                "category": dataset.category,
                "subcategory": dataset.subcategory,
                "api_endpoint": dataset.api_endpoint,
                "geographic_level": dataset.geographic_level,
                "time_granularity": dataset.time_granularity,
                "update_frequency": dataset.update_frequency,
                "source_department": dataset.source_department,
                "last_updated": dataset.last_updated.isoformat() if dataset.last_updated else None,
                "indicators": indicators_data,
                "data_sources": sources_data
            }
    
    def get_dataset_data(self, slug: str, filters: Dict[str, Any] = None, 
                         limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get actual data for a specific dataset with filters."""
        with Session(self.engine) as session:
            dataset = session.query(DatasetRegistry).filter_by(slug=slug, is_active=True).first()
            
            if not dataset:
                return None
            
            # Build query for extended fact measures
            query = session.query(ExtendedFactMeasure).filter_by(dataset_id=dataset.id)
            
            # Apply filters if provided
            if filters:
                if 'geo_id' in filters:
                    query = query.filter(ExtendedFactMeasure.geo_id == filters['geo_id'])
                if 'time_id' in filters:
                    query = query.filter(ExtendedFactMeasure.time_id == filters['time_id'])
                if 'indicator_id' in filters:
                    query = query.filter(ExtendedFactMeasure.indicator_id == filters['indicator_id'])
            
            # Apply limit
            query = query.limit(limit)
            
            # Execute query
            measures = query.all()
            
            # Transform to readable format
            data = []
            for measure in measures:
                # Get related information
                indicator = session.query(DatasetIndicator).filter_by(id=measure.indicator_id).first()
                geography = session.query(text("name")).select_from(text("dim_geo")).filter_by(id=measure.geo_id).first()
                time_period = session.query(text("year")).select_from(text("dim_time")).filter_by(id=measure.time_id).first()
                
                # Determine value based on data type
                if measure.numeric_value is not None:
                    value = float(measure.numeric_value)
                elif measure.string_value is not None:
                    value = measure.string_value
                elif measure.boolean_value is not None:
                    value = measure.boolean_value
                elif measure.date_value is not None:
                    value = measure.date_value.isoformat()
                else:
                    value = None
                
                data.append({
                    "indicator": indicator.display_name if indicator else "Unknown",
                    "geography": geography[0] if geography else "Unknown",
                    "time_period": time_period[0] if time_period else "Unknown",
                    "value": value,
                    "unit": indicator.unit if indicator else None,
                    "source_record_id": measure.source_record_id,
                    "quality_flag": measure.quality_flag
                })
            
            return {
                "dataset": {
                    "slug": dataset.slug,
                    "title": dataset.title,
                    "category": dataset.category
                },
                "total_records": len(data),
                "data": data,
                "filters_applied": filters or {}
            }
    
    def get_available_categories(self) -> List[str]:
        """Get all available dataset categories."""
        with Session(self.engine) as session:
            categories = session.query(DatasetRegistry.category).distinct().all()
            return [cat[0] for cat in categories]
    
    def get_datasets_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get datasets filtered by category."""
        with Session(self.engine) as session:
            datasets = session.query(DatasetRegistry).filter_by(
                category=category, is_active=True
            ).all()
            
            result = []
            for dataset in datasets:
                # Get indicators count
                indicators_count = session.query(DatasetIndicator).filter_by(
                    dataset_id=dataset.id
                ).count()
                
                result.append({
                    "id": dataset.id,
                    "slug": dataset.slug,
                    "title": dataset.title,
                    "subcategory": dataset.subcategory,
                    "geographic_level": dataset.geographic_level,
                    "time_granularity": dataset.time_granularity,
                    "indicators_count": indicators_count
                })
            
            return result
    
    def get_geographic_coverage(self, slug: str) -> List[Dict[str, Any]]:
        """Get geographic coverage for a specific dataset."""
        with Session(self.engine) as session:
            dataset = session.query(DatasetRegistry).filter_by(slug=slug, is_active=True).first()
            
            if not dataset:
                return []
            
            # Get unique geographic entities for this dataset
            geo_query = session.query(ExtendedFactMeasure.geo_id).filter_by(
                dataset_id=dataset.id
            ).distinct()
            
            geo_ids = [row[0] for row in geo_query.all()]
            
            # Get geographic details
            coverage = []
            for geo_id in geo_ids:
                geo = session.query(text("name, type")).select_from(text("dim_geo")).filter_by(id=geo_id).first()
                if geo:
                    coverage.append({
                        "geo_id": geo_id,
                        "name": geo[0],
                        "type": geo[1]
                    })
            
            return coverage
    
    def get_time_coverage(self, slug: str) -> List[Dict[str, Any]]:
        """Get time coverage for a specific dataset."""
        with Session(self.engine) as session:
            dataset = session.query(DatasetRegistry).filter_by(slug=slug, is_active=True).first()
            
            if not dataset:
                return []
            
            # Get unique time periods for this dataset
            time_query = session.query(ExtendedFactMeasure.time_id).filter_by(
                dataset_id=dataset.id
            ).distinct()
            
            time_ids = [row[0] for row in time_query.all()]
            
            # Get time details
            coverage = []
            for time_id in time_ids:
                time_period = session.query(text("year, quarter, month")).select_from(text("dim_time")).filter_by(id=time_id).first()
                if time_period:
                    coverage.append({
                        "time_id": time_id,
                        "year": time_period[0],
                        "quarter": time_period[1],
                        "month": time_period[2]
                    })
            
            return coverage
    
    def get_dataset_statistics(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive statistics for a dataset."""
        with Session(self.engine) as session:
            dataset = session.query(DatasetRegistry).filter_by(slug=slug, is_active=True).first()
            
            if not dataset:
                return None
            
            # Count total records
            total_records = session.query(ExtendedFactMeasure).filter_by(dataset_id=dataset.id).count()
            
            # Count by indicator
            indicator_counts = session.query(
                ExtendedFactMeasure.indicator_id,
                text("COUNT(*) as count")
            ).filter_by(dataset_id=dataset.id).group_by(
                ExtendedFactMeasure.indicator_id
            ).all()
            
            # Count by geography
            geo_counts = session.query(
                ExtendedFactMeasure.geo_id,
                text("COUNT(*) as count")
            ).filter_by(dataset_id=dataset.id).group_by(
                ExtendedFactMeasure.geo_id
            ).all()
            
            # Count by time
            time_counts = session.query(
                ExtendedFactMeasure.time_id,
                text("COUNT(*) as count")
            ).filter_by(dataset_id=dataset.id).group_by(
                ExtendedFactMeasure.time_id
            ).all()
            
            return {
                "dataset": {
                    "slug": dataset.slug,
                    "title": dataset.title,
                    "category": dataset.category
                },
                "total_records": total_records,
                "indicators_count": len(indicator_counts),
                "geographic_coverage": len(geo_counts),
                "time_coverage": len(time_counts),
                "last_updated": dataset.last_updated.isoformat() if dataset.last_updated else None,
                "data_quality": {
                    "total_processed": total_records,
                    "quality_score": 95.0  # Placeholder - would calculate from DataQualityLog
                }
            }
    
    def search_datasets(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search datasets by title, description, or category."""
        with Session(self.engine) as session:
            search_query = session.query(DatasetRegistry).filter_by(is_active=True)
            
            if category:
                search_query = search_query.filter(DatasetRegistry.category == category)
            
            if query:
                search_query = search_query.filter(
                    DatasetRegistry.title.ilike(f"%{query}%") |
                    DatasetRegistry.description.ilike(f"%{query}%") |
                    DatasetRegistry.subcategory.ilike(f"%{query}%")
                )
            
            datasets = search_query.all()
            
            result = []
            for dataset in datasets:
                # Get indicators count
                indicators_count = session.query(DatasetIndicator).filter_by(
                    dataset_id=dataset.id
                ).count()
                
                result.append({
                    "id": dataset.id,
                    "slug": dataset.slug,
                    "title": dataset.title,
                    "category": dataset.category,
                    "subcategory": dataset.subcategory,
                    "geographic_level": dataset.geographic_level,
                    "time_granularity": dataset.time_granularity,
                    "indicators_count": indicators_count
                })
            
            return result


# Global instance
government_data_service = GovernmentDataService()
