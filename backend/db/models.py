"""SQLAlchemy models for the Municipal AI Insights database."""

from sqlalchemy import Column, Integer, String, Text, Numeric, Date, ForeignKey, Index, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DimGeo(Base):
    """Geography dimension table."""
    __tablename__ = "dim_geo"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(Text, nullable=True)
    district = Column(Text, nullable=True)
    zone = Column(Text, nullable=True)
    ward = Column(Text, nullable=True)
    level = Column(Text, nullable=False)
    # Optional PostGIS geometry column (commented for MVP)
    # geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True)
    
    __table_args__ = (
        CheckConstraint("level IN ('state', 'district', 'zone', 'ward')", name="check_geo_level"),
    )
    
    # Relationships
    measures = relationship("FactMeasure", back_populates="geography")


class DimTime(Base):
    """Time dimension table."""
    __tablename__ = "dim_time"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=True)
    year = Column(Integer, nullable=True)
    quarter = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)
    
    # Relationships
    measures = relationship("FactMeasure", back_populates="time")


class DimIndicator(Base):
    """Indicator dimension table."""
    __tablename__ = "dim_indicator"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    unit = Column(Text, nullable=False)
    category = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    default_agg = Column(Text, nullable=False)
    
    __table_args__ = (
        CheckConstraint("default_agg IN ('SUM', 'AVG', 'MAX', 'MIN')", name="check_default_agg"),
    )
    
    # Relationships
    measures = relationship("FactMeasure", back_populates="indicator")


class FactMeasure(Base):
    """Main fact table for all measurements."""
    __tablename__ = "fact_measure"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(Integer, ForeignKey("dim_indicator.id"), nullable=False)
    geo_id = Column(Integer, ForeignKey("dim_geo.id"), nullable=False)
    time_id = Column(Integer, ForeignKey("dim_time.id"), nullable=False)
    value = Column(Numeric, nullable=True)
    quality_flag = Column(Text, nullable=True)
    
    # Relationships
    indicator = relationship("DimIndicator", back_populates="measures")
    geography = relationship("DimGeo", back_populates="measures")
    time = relationship("DimTime", back_populates="measures")
    
    __table_args__ = (
        Index("idx_fact_keys", "indicator_id", "geo_id", "time_id"),
        Index("idx_time_year", "time_id"),
    )


# Create indexes separately for better control
Index("idx_time_year_quarter_month", DimTime.year, DimTime.quarter, DimTime.month)
