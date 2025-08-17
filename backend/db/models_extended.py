"""Extended SQLAlchemy models for Government Datasets Integration."""

from sqlalchemy import Column, Integer, String, Text, Numeric, Date, ForeignKey, Index, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DatasetRegistry(Base):
    """Registry for all available datasets from government sources."""
    __tablename__ = "dataset_registry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Text, unique=True, nullable=False)  # Government portal resource ID
    slug = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Text, nullable=False)  # Economic, Infrastructure, Social, etc.
    subcategory = Column(Text, nullable=True)  # GDP, Inflation, Roads, etc.
    
    # API Configuration
    api_endpoint = Column(Text, nullable=False)
    api_key_required = Column(Boolean, default=True)
    supported_formats = Column(JSON)  # ['json', 'xml', 'csv']
    
    # Data Characteristics
    geographic_level = Column(Text, nullable=False)  # 'national', 'state', 'district', 'tehsil'
    time_granularity = Column(Text, nullable=False)  # 'annual', 'quarterly', 'monthly', 'daily'
    update_frequency = Column(Text, nullable=True)  # 'daily', 'weekly', 'monthly', 'quarterly'
    
    # Metadata
    source_department = Column(Text, nullable=True)
    last_updated = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)


class DatasetIndicator(Base):
    """Indicators available in each dataset."""
    __tablename__ = "dataset_indicator"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("dataset_registry.id"), nullable=False)
    field_name = Column(Text, nullable=False)  # Original field name from API
    display_name = Column(Text, nullable=False)  # Human-readable name
    data_type = Column(Text, nullable=False)  # 'number', 'string', 'date', 'boolean'
    unit = Column(Text, nullable=True)  # 'percentage', 'crores', 'km', etc.
    description = Column(Text, nullable=True)
    is_filterable = Column(Boolean, default=False)  # Can be used as filter
    is_measure = Column(Boolean, default=True)  # Is this a measurable value


class DataSource(Base):
    """Tracks data ingestion sources and lineage."""
    __tablename__ = "data_source"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("dataset_registry.id"), nullable=False)
    source_type = Column(Text, nullable=False)  # 'api', 'file_download', 'manual'
    source_url = Column(Text, nullable=True)
    last_sync = Column(Date, nullable=True)
    sync_status = Column(Text, default='pending')  # 'pending', 'success', 'failed'
    error_message = Column(Text, nullable=True)
    records_count = Column(Integer, nullable=True)


class GeographicHierarchy(Base):
    """Extended geographic hierarchy for different administrative levels."""
    __tablename__ = "geographic_hierarchy"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    geo_id = Column(Integer, nullable=False)  # Reference to dim_geo.id
    parent_geo_id = Column(Integer, nullable=True)  # Reference to dim_geo.id
    hierarchy_level = Column(Integer, nullable=False)  # 1=state, 2=district, 3=tehsil, etc.
    census_code = Column(Text, nullable=True)  # Official census codes
    official_name = Column(Text, nullable=True)  # Official government name
    alternate_names = Column(JSON, nullable=True)  # Common variations
    is_active = Column(Boolean, default=True)


class ExtendedFactMeasure(Base):
    """Extended fact table for government datasets with flexible structure."""
    __tablename__ = "extended_fact_measure"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("dataset_registry.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("dataset_indicator.id"), nullable=False)
    geo_id = Column(Integer, nullable=False)  # Reference to dim_geo.id
    time_id = Column(Integer, nullable=False)  # Reference to dim_time.id
    
    # Flexible value storage
    numeric_value = Column(Numeric, nullable=True)
    string_value = Column(Text, nullable=True)
    boolean_value = Column(Boolean, nullable=True)
    date_value = Column(Date, nullable=True)
    
    # Metadata
    source_record_id = Column(Text, nullable=True)  # Original record ID from source
    quality_flag = Column(Text, nullable=True)
    ingestion_timestamp = Column(Date, default=datetime.utcnow)


class DataQualityLog(Base):
    """Logs data quality issues and validation results."""
    __tablename__ = "data_quality_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("dataset_registry.id"), nullable=False)
    sync_timestamp = Column(Date, default=datetime.utcnow)
    records_processed = Column(Integer, nullable=False)
    records_valid = Column(Integer, nullable=False)
    records_invalid = Column(Integer, nullable=False)
    validation_errors = Column(JSON, nullable=True)  # Detailed error information
    quality_score = Column(Numeric, nullable=True)  # 0-100 quality score
    notes = Column(Text, nullable=True)


# Create indexes for performance
Index("idx_extended_fact_dataset", ExtendedFactMeasure.dataset_id)
Index("idx_extended_fact_indicator", ExtendedFactMeasure.indicator_id)
Index("idx_extended_fact_geo", ExtendedFactMeasure.geo_id)
Index("idx_extended_fact_time", ExtendedFactMeasure.time_id)
Index("idx_geo_hierarchy_level", GeographicHierarchy.hierarchy_level)
Index("idx_dataset_category", DatasetRegistry.category)
Index("idx_dataset_geo_level", DatasetRegistry.geographic_level)
