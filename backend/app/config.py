from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
    ml_client_id: str = ""
    ml_client_secret: str = ""
    app_base_url: str = "http://localhost:8000"
    frontend_origin: str = "http://localhost:3000"
    env: str = "development"

    # JWT
    secret_key: str = "replace-me-with-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    class Config:
        env_file = "../.env"

settings = Settings()
