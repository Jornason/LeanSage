"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "LeanProve AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/leanprove"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:3000/api/auth/github/callback"

    # AI APIs
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Modal
    MODAL_TOKEN_ID: str = ""
    MODAL_TOKEN_SECRET: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
