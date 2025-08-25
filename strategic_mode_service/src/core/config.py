from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Basic settings
    APP_NAME: str = "Strategic Mode Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8017
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/16"
    
    # External services
    ACOS_SERVICE_URL: str = "http://acos_service:8016"
    CAMPAIGN_SERVICE_URL: str = "http://campaign_automation_service:8014"
    DISCOUNT_SERVICE_URL: str = "http://discount_campaign_scheduler:8015"
    AI_PREDICTIVE_URL: str = "http://ai_predictive:8005"
    ROI_PREDICTION_URL: str = "http://roi_prediction:8013"
    
    # Security
    SECRET_KEY: str = "strategic-mode-secret-key-change-in-production"
    
    # Automation settings
    AUTO_APPLY_CHANGES: bool = True
    SIMULATION_MODE: bool = False
    MAX_BUDGET_INCREASE: int = 200
    MIN_MARGIN_THRESHOLD: int = 15
    
    # Alert settings
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    TEAMS_WEBHOOK_URL: Optional[str] = None
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://redis:6379/16"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/16"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()