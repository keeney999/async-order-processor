"""Application configuration management."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "Async Order Processor"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str
    RABBITMQ_URL: str
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
