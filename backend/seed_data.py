"""Seed data script for Municipal AI Insights database."""

from sqlalchemy.orm import Session
from db.models import DimGeo, DimTime, DimIndicator, FactMeasure
from db.session import owner_engine
from datetime import date
import decimal

def create_seed_data():
    """Create minimal seed data for testing."""
    
    # Create session using owner engine
    session = Session(owner_engine)
    
    try:
        # Check if data already exists
        if session.query(DimGeo).count() > 0:
            print("Seed data already exists, skipping...")
            return
        
        print("Creating seed data...")
        
        # Create geography data
        ranchi_district = DimGeo(
            state="Jharkhand",
            district="Ranchi",
            zone=None,
            ward=None,
            level="district"
        )
        session.add(ranchi_district)
        session.flush()  # Get the ID
        
        # Create time data for 2019-2021
        time_2019 = DimTime(date=date(2019, 12, 31), year=2019, quarter=4, month=12)
        time_2020 = DimTime(date=date(2020, 12, 31), year=2020, quarter=4, month=12)
        time_2021 = DimTime(date=date(2021, 12, 31), year=2021, quarter=4, month=12)
        
        session.add_all([time_2019, time_2020, time_2021])
        session.flush()
        
        # Create indicator data
        forest_cover = DimIndicator(
            slug="forest_cover_area",
            title="Forest Cover Area",
            unit="hectares",
            category="Environment",
            description="Total area covered by forests",
            default_agg="SUM"
        )
        
        fish_production = DimIndicator(
            slug="fish_production_tonnes",
            title="Fish Production",
            unit="tonnes",
            category="Agriculture", 
            description="Total fish production in tonnes",
            default_agg="SUM"
        )
        
        session.add_all([forest_cover, fish_production])
        session.flush()
        
        # Create fact measurements
        measurements = [
            # Forest cover data for Ranchi
            FactMeasure(
                indicator_id=forest_cover.id,
                geo_id=ranchi_district.id,
                time_id=time_2019.id,
                value=decimal.Decimal('15420.5'),
                quality_flag="verified"
            ),
            FactMeasure(
                indicator_id=forest_cover.id,
                geo_id=ranchi_district.id,
                time_id=time_2020.id,
                value=decimal.Decimal('15380.2'),
                quality_flag="verified"
            ),
            FactMeasure(
                indicator_id=forest_cover.id,
                geo_id=ranchi_district.id,
                time_id=time_2021.id,
                value=decimal.Decimal('15365.8'),
                quality_flag="verified"
            ),
            
            # Fish production data for Ranchi
            FactMeasure(
                indicator_id=fish_production.id,
                geo_id=ranchi_district.id,
                time_id=time_2019.id,
                value=decimal.Decimal('245.8'),
                quality_flag="verified"
            ),
            FactMeasure(
                indicator_id=fish_production.id,
                geo_id=ranchi_district.id,
                time_id=time_2020.id,
                value=decimal.Decimal('267.3'),
                quality_flag="verified"
            ),
            FactMeasure(
                indicator_id=fish_production.id,
                geo_id=ranchi_district.id,
                time_id=time_2021.id,
                value=decimal.Decimal('289.7'),
                quality_flag="verified"
            ),
        ]
        
        session.add_all(measurements)
        session.commit()
        
        print("Seed data created successfully!")
        print(f"- Created {session.query(DimGeo).count()} geography records")
        print(f"- Created {session.query(DimTime).count()} time records")
        print(f"- Created {session.query(DimIndicator).count()} indicator records")
        print(f"- Created {session.query(FactMeasure).count()} measurement records")
        
    except Exception as e:
        print(f"Error creating seed data: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_seed_data()
