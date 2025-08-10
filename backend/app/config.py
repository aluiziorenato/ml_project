from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
    secret_key: str = "troque_por_uma_chave_segura_em_producao"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    frontend_origin: str = "http://localhost:3000"
    env: str = "development"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"

settings = Settings()
