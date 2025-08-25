import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration"""
    
    # Application settings
    app_name: str = "Discount Campaign Scheduler"
    debug: bool = False
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./discount_campaigns.db")
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/15")
    
    # Celery settings
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/15")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/15")
    
    # Mercado Libre API settings
    ml_api_url: str = os.getenv("ML_API_URL", "https://api.mercadolibre.com")
    ml_client_id: str = os.getenv("ML_CLIENT_ID", "")
    ml_client_secret: str = os.getenv("ML_CLIENT_SECRET", "")
    
    # Authentication settings
    secret_key: str = os.getenv("SECRET_KEY", "discount-campaign-scheduler-secret-key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External services
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    simulator_service_url: str = os.getenv("SIMULATOR_SERVICE_URL", "http://localhost:8001")
    optimizer_ai_url: str = os.getenv("OPTIMIZER_AI_URL", "http://localhost:8003")
    
    # Grafana settings
    grafana_url: str = os.getenv("GRAFANA_URL", "http://localhost:3001")
    grafana_api_key: Optional[str] = os.getenv("GRAFANA_API_KEY")
    
    # Scheduling settings
    schedule_check_interval_minutes: int = int(os.getenv("SCHEDULE_CHECK_INTERVAL_MINUTES", "5"))
    metrics_collection_interval_hours: int = int(os.getenv("METRICS_COLLECTION_INTERVAL_HOURS", "1"))
    
    # Prediction settings
    prediction_model_version: str = "v1.0"
    prediction_confidence_threshold: float = 0.7
    
    # Suggestions settings
    max_suggestions: int = 5
    suggestion_refresh_hours: int = 6
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()