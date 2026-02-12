"""
Application configuration settings.

Loads environment variables using Pydantic BaseSettings for type-safe configuration management.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses Pydantic BaseSettings to automatically load from .env file and validate types.
    """

    # Database settings
    database_url: str

    # Application settings
    environment: str = "development"
    debug: bool = True

    # Authentication settings
    better_auth_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_delta: int = 1440  # 24 hours in minutes

    # CORS settings
    allowed_origins: str = "http://localhost:3000"

    # Server settings
    port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
