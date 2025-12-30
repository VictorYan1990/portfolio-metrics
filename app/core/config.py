from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Project information
    PROJECT_NAME: str = "Portfolio Metrics API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "A FastAPI application for portfolio metrics and analysis"
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database settings (for future use)
    DATABASE_URL: str = "sqlite:///./portfolio_metrics.db"
    
    # Security settings (REQUIRED - must be set via environment)
    SECRET_KEY: str  # No default - must be provided
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

        case_sensitive = True


# Create settings instances
settings = Settings()
