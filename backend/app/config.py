from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
    ml_client_id: str = ""
    ml_client_secret: str = ""
    app_base_url: str = "http://localhost:8000"
    frontend_origin: str = "http://localhost:3000"
    env: str = "development"

    # JWT configs direto na classe principal
    secret_key: str = "sua_chave_secreta_muito_segura_aqui"  # Gere uma chave forte para produção!
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"

settings = Settings()
