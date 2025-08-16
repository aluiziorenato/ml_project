import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="sqlite:///./test.db", alias="DATABASE_URL")
    
    # Mercado Libre API
    ml_client_id: str = Field(default="", alias="ML_CLIENT_ID")
    ml_client_secret: str = Field(default="", alias="ML_CLIENT_SECRET")
    ml_redirect_uri: str = Field(default="", alias="ML_REDIRECT_URI")
    
    # JWT Configuration
    secret_key: str = Field(default="change-this-secret-key-in-production", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS Configuration
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")
    
    # Application
    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")
    env: str = Field(default="development", alias="ENV")
    
    # Sentry Configuration
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    sentry_environment: str = Field(default="development", alias="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(default=0.1, alias="SENTRY_TRACES_SAMPLE_RATE")
    
    # Admin User
    admin_email: str = Field(default="admin@example.com", alias="ADMIN_EMAIL")
    admin_password: Optional[str] = Field(default=None, alias="ADMIN_PASSWORD")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Create a global settings instance
settings = Settings()