"""
Configuration module for loading environment variables and app settings.
Uses Pydantic for validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    API_TITLE: str = "Data Quality Validation Framework"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_POOL_RECYCLE: int = 3600

    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    # Feature Flags
    ENABLE_ASYNC_TASKS: bool = True
    ENABLE_CACHING: bool = True

    # Redis Caching Settings
    REDIS_ENABLED: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_VALIDATION_TTL: int = 1800  # 30 minutes
    REDIS_METRICS_TTL: int = 3600  # 1 hour
    REDIS_DATASET_TTL: int = 7200  # 2 hours
    REDIS_ANOMALY_TTL: int = 1800  # 30 minutes
    REDIS_SESSION_TTL: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = True


# Load settings once
settings = Settings()
