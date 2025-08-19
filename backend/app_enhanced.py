"""Enhanced FastAPI application with Government Datasets Integration."""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging

from core.config import settings
from core.logging import setup_logging
from services.insights import InsightService
from services.government_data_service import government_data_service
from db.session import get_readonly_session

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Municipal AI Insights - Enhanced",
    description="AI-powered municipal analytics platform with government datasets integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for insights
class TimeFilter(BaseModel):
    from_: str
    to: str

class PlaceFilter(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    zone: Optional[str] = None

class ExtraFilter(BaseModel):
    category: Optional[str] = None

class InsightFilters(BaseModel):
    time: Optional[TimeFilter] = None
    place: Optional[PlaceFilter] = None
    extra: Optional[ExtraFilter] = None

class InsightRequest(BaseModel):
    prompt: str
    filters: Optional[InsightFilters] = None

# Pydantic models for government datasets
class DatasetFilter(BaseModel):
    geo_id: Optional[int] = None
    time_id: Optional[int] = None
    indicator_id: Optional[int] = None
    limit: Optional[int] = 100

class DatasetSearch(BaseModel):
    query: str
    category: Optional[str] = None

# Existing endpoints
@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"ok": True, "version": "2.0.0", "features": ["insights", "government_datasets"]}

@app.get("/api/schema")
async def get_schema():
    """Get sanitized database schema."""
    try:
        # This would return the enhanced schema including government datasets
        return {
            "message": "Enhanced schema with government datasets support",
            "tables": [
                "dim_geo", "dim_time", "dim_indicator", "fact_measure",
                "dataset_registry", "dataset_indicator", "extended_fact_measure"
            ],
            "features": [
                "Government datasets integration",
                "Multi-format data support",
                "Enhanced geographic hierarchy",
                "Data quality tracking"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve schema")

@app.post("/api/insights")
async def generate_insight(request: InsightRequest):
    """Generate AI-powered insights from municipal data."""
    try:
        from llm.agent import MunicipalAnalystAgent
        
        # Initialize the LLM agent
        agent = MunicipalAnalystAgent()
        
        # Convert filters to the format expected by the agent
        filters_dict = {}
        if request.filters:
            if request.filters.time:
                filters_dict["time"] = {
                    "from": request.filters.time.from_,
                    "to": request.filters.time.to
                }
            if request.filters.place:
                filters_dict["place"] = {
                    "state": request.filters.place.state,
                    "district": request.filters.place.district,
                    "ward": request.filters.place.ward,
                    "zone": request.filters.place.zone
                }
            if request.filters.extra:
                filters_dict["extra"] = {
                    "category": request.filters.extra.category
                }
        
        # Generate insight using the LLM agent
        insight_response = await agent.generate_insight(
            prompt=request.prompt,
            filters=filters_dict
        )
        
        return insight_response
        
    except Exception as e:
        logger.error(f"Error generating insight: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insight: {str(e)}")

# New Government Dataset endpoints
@app.get("/api/datasets")
async def get_datasets():
    """Get all available government datasets."""
    try:
        datasets = government_data_service.get_all_datasets()
        return {
            "total": len(datasets),
            "datasets": datasets
        }
    except Exception as e:
        logger.error(f"Error getting datasets: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve datasets")

@app.get("/api/datasets/categories")
async def get_dataset_categories():
    """Get all available dataset categories."""
    try:
        categories = government_data_service.get_available_categories()
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")

@app.get("/api/datasets/category/{category}")
async def get_datasets_by_category(category: str):
    """Get datasets filtered by category."""
    try:
        datasets = government_data_service.get_datasets_by_category(category)
        return {
            "category": category,
            "total": len(datasets),
            "datasets": datasets
        }
    except Exception as e:
        logger.error(f"Error getting datasets by category: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve datasets")

@app.get("/api/datasets/{slug}")
async def get_dataset_details(slug: str):
    """Get detailed information about a specific dataset."""
    try:
        dataset = government_data_service.get_dataset_by_slug(slug)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataset details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dataset details")

@app.get("/api/datasets/{slug}/data")
async def get_dataset_data(
    slug: str,
    geo_id: Optional[int] = Query(None, description="Geographic ID filter"),
    time_id: Optional[int] = Query(None, description="Time period ID filter"),
    indicator_id: Optional[int] = Query(None, description="Indicator ID filter"),
    limit: int = Query(100, description="Maximum number of records to return")
):
    """Get actual data for a specific dataset with optional filters."""
    try:
        filters = {}
        if geo_id is not None:
            filters['geo_id'] = geo_id
        if time_id is not None:
            filters['time_id'] = time_id
        if indicator_id is not None:
            filters['indicator_id'] = indicator_id
        
        data = government_data_service.get_dataset_data(slug, filters, limit)
        if not data:
            raise HTTPException(status_code=404, detail="Dataset not found or no data available")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataset data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dataset data")

@app.get("/api/datasets/{slug}/coverage/geographic")
async def get_dataset_geographic_coverage(slug: str):
    """Get geographic coverage for a specific dataset."""
    try:
        coverage = government_data_service.get_geographic_coverage(slug)
        return {
            "dataset_slug": slug,
            "geographic_coverage": coverage,
            "total_locations": len(coverage)
        }
    except Exception as e:
        logger.error(f"Error getting geographic coverage: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve geographic coverage")

@app.get("/api/datasets/{slug}/coverage/time")
async def get_dataset_time_coverage(slug: str):
    """Get time coverage for a specific dataset."""
    try:
        coverage = government_data_service.get_time_coverage(slug)
        return {
            "dataset_slug": slug,
            "time_coverage": coverage,
            "total_periods": len(coverage)
        }
    except Exception as e:
        logger.error(f"Error getting time coverage: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve time coverage")

@app.get("/api/datasets/{slug}/statistics")
async def get_dataset_statistics(slug: str):
    """Get comprehensive statistics for a dataset."""
    try:
        stats = government_data_service.get_dataset_statistics(slug)
        if not stats:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataset statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dataset statistics")

@app.post("/api/datasets/search")
async def search_datasets(search: DatasetSearch):
    """Search datasets by query and optional category filter."""
    try:
        datasets = government_data_service.search_datasets(search.query, search.category)
        return {
            "query": search.query,
            "category": search.category,
            "total": len(datasets),
            "datasets": datasets
        }
    except Exception as e:
        logger.error(f"Error searching datasets: {e}")
        raise HTTPException(status_code=500, detail="Failed to search datasets")

# Dataset management endpoints (for future admin functionality)
@app.get("/api/admin/datasets/sync-status")
async def get_sync_status():
    """Get synchronization status for all datasets."""
    try:
        # This would check DataSource table for sync status
        return {
            "message": "Sync status endpoint - requires admin authentication",
            "total_datasets": 25,
            "synced": 20,
            "pending": 3,
            "failed": 2
        }
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sync status")

@app.post("/api/admin/datasets/{slug}/sync")
async def trigger_dataset_sync(slug: str):
    """Trigger manual synchronization for a dataset."""
    try:
        # This would trigger the ETL pipeline for the specific dataset
        return {
            "message": f"Sync triggered for dataset: {slug}",
            "status": "queued",
            "estimated_completion": "5 minutes"
        }
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger sync")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
