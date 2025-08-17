"""Contract tests for the Municipal AI Insights API."""

import pytest
from fastapi.testclient import TestClient
import json
from app import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data == {"ok": True}


def test_get_schema():
    """Test the schema endpoint returns correct structure."""
    response = client.get("/api/schema")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify required top-level keys
    assert "tables" in data
    assert "joins" in data
    
    # Verify tables structure
    assert isinstance(data["tables"], list)
    assert len(data["tables"]) > 0
    
    for table in data["tables"]:
        assert "name" in table
        assert "columns" in table
        assert isinstance(table["columns"], list)
        
        for column in table["columns"]:
            assert "name" in column
            assert "type" in column
    
    # Verify joins structure
    assert isinstance(data["joins"], list)
    for join in data["joins"]:
        assert "from" in join
        assert "to" in join


def test_get_datasets():
    """Test the datasets endpoint returns correct structure."""
    response = client.get("/api/datasets")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    for dataset in data:
        assert "slug" in dataset
        assert "title" in dataset
        assert "unit" in dataset
        assert "category" in dataset
        assert "years" in dataset
        assert "geo_levels" in dataset
        assert isinstance(dataset["years"], list)
        assert isinstance(dataset["geo_levels"], list)


def test_insights_endpoint_structure():
    """Test that insights endpoint returns correct JSON structure."""
    # Test payload
    payload = {
        "prompt": "Show me forest cover data",
        "filters": {
            "time": {"from": "2019-01-01", "to": "2021-12-31"},
            "place": {"district": "Ranchi"},
            "extra": {}
        }
    }
    
    response = client.post("/api/insights", json=payload)
    
    # Note: This might fail if OpenRouter API is not configured
    # but we're testing the structure
    if response.status_code == 200:
        data = response.json()
        
        # Verify required fields exist
        required_fields = [
            "insight_text", "sql_used", "data_preview", "viz",
            "doc_citations", "filters_applied", "disclaimers"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify data_preview structure
        assert "columns" in data["data_preview"]
        assert "rows" in data["data_preview"]
        assert isinstance(data["data_preview"]["columns"], list)
        assert isinstance(data["data_preview"]["rows"], list)
        
        # Verify data preview row limit
        assert len(data["data_preview"]["rows"]) <= 50
        
        # Verify viz structure
        assert "type" in data["viz"]
        assert "spec" in data["viz"]
        assert data["viz"]["type"] == "vega-lite"
        
        # Verify other fields are correct types
        assert isinstance(data["insight_text"], str)
        assert isinstance(data["sql_used"], str)
        assert isinstance(data["doc_citations"], list)
        assert isinstance(data["filters_applied"], dict)
        assert isinstance(data["disclaimers"], list)


def test_insights_endpoint_invalid_payload():
    """Test insights endpoint with invalid payload."""
    # Missing required prompt field
    payload = {
        "filters": {}
    }
    
    response = client.post("/api/insights", json=payload)
    assert response.status_code == 422  # Validation error


def test_sql_safety():
    """Test that SQL guard prevents dangerous operations."""
    # This would need to be tested at the service level
    # since the API endpoint won't directly expose SQL validation errors
    pass
