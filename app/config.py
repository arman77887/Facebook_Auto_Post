import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Facebook Auto Post SaaS"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"

    POSTGRES_USER: str = "fb_saas_user"
    POSTGRES_PASSWORD: str = "SuperSecretPassword123!"
    POSTGRES_DB: str = "fb_saas_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = (
        "postgresql+asyncpg://fb_saas_user:SuperSecretPassword123!@postgres:5432/fb_saas_db"
    )

    REDIS_URL: str = "redis://redis:6379/0"

    TELEGRAM_BOT_TOKEN: str
    ADMIN_TELEGRAM_ID: int

    FACEBOOK_APP_ID: str
    FACEBOOK_APP_SECRET: str
    FACEBOOK_GRAPH_VERSION: str = "v20.0"
    FACEBOOK_VERIFY_TOKEN: str

    ENCRYPTION_KEY: str
    SECRET_KEY: str

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
