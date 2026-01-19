"""
Application configuration settings.
Manages all environment variables and application settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str = "GitHub Code Collaboration Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/code_agent"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL: int = 3600

    # GitHub OAuth Settings
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_secret: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8080/api/v1/github/callback"
    GITHUB_SCOPES: str = "repo,user"

    # JWT Settings
    JWT_secret_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # LLM Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.7

    # Local LLM Settings (optional)
    LOCAL_LLM_URL: Optional[str] = None
    LOCAL_LLM_MODEL: Optional[str] = None

    # File Storage Settings
    STORAGE_PATH: str = "/tmp/code_agent"
    MAX_REPO_SIZE_MB: int = 500

    # Security Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
