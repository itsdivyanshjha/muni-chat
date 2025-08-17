"""Configuration management for the Municipal AI Insights backend."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter API Configuration
    openrouter_api_key: str
    model_slug: str = "openai/gpt-4"
    
    # Database Configuration
    database_url: str
    runtime_db_url: str
    
    # Government Data Portal API Key
    government_api_key: str
    
    # Application Configuration
    app_env: str = "dev"
    debug: bool = True
    
    # Query Configuration
    query_timeout_seconds: int = 10
    max_rows_returned: int = 5000
    max_preview_rows: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
