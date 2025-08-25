"""Configuration settings for ACOS Service."""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Server configuration
    port: int = 8016
    host: str = "0.0.0.0"
    debug: bool = False
    
    # Database configuration
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
    
    # Redis configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Authentication
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # ACOS specific settings
    default_acos_threshold: float = 25.0
    max_evaluation_period_hours: int = 168  # 7 days
    min_spend_threshold: float = 10.0
    
    # Integration URLs
    campaign_service_url: str = "http://localhost:8014"
    ai_service_url: str = "http://localhost:8005"
    
    # Background task settings
    evaluation_interval_minutes: int = 60
    alert_cooldown_hours: int = 4
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()