# backend/app/config.py
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
OAUTH_CALLBACK_PATH = os.getenv("OAUTH_CALLBACK_PATH", "/api/oauth/callback")

# URL final de retorno

REDIRECT_URI = f"{BASE_URL}{OAUTH_CALLBACK_PATH}"
MERCADO_LIBRE_APP_ID = os.getenv("MERCADO_LIBRE_APP_ID")
MERCADO_LIBRE_SECRET = os.getenv("MERCADO_LIBRE_SECRET")

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
    secret_key: str = "troque_por_uma_chave_secreta_em_producao"  # altere no .env para produção
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    ml_client_id: str = ""
    ml_client_secret: str = ""
    app_base_url: str = "http://localhost:8000"
    frontend_origin: str = "http://localhost:3000"
    env: str = "development"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"

settings = Settings()
