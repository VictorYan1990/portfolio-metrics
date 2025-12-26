from pydantic_settings import BaseSettings
from typing import List
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
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    # EXTERNAL API settings
    class InstrumentAPI_Settings(BaseSettings):
        name: str = "Alpha_Vantage"
        url: str = "https://www.alphavantage.co/query"
        api_key: str = " 1JUOTRNVQ6GKTMRT"


# Create settings instance
settings = Settings()
