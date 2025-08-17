"""Configuration management for Campaign Automation Service."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic app settings
    app_name: str = "Campaign Automation Service"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8014
    
    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
    )
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/14")
    
    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # External services
    simulator_service_url: str = os.getenv("SIMULATOR_SERVICE_URL", "http://simulator_service:8001")
    optimizer_ai_url: str = os.getenv("OPTIMIZER_AI_URL", "http://optimizer_ai:8003")
    learning_service_url: str = os.getenv("LEARNING_SERVICE_URL", "http://learning_service:8002")
    
    # Celery settings
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/14")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/14")
    
    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()