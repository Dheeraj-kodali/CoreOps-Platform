from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_REDIS_URL: str = "redis://localhost:6379/0"


class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    PROJECT_NAME: str = "Sri Kalki Seva Alayam - Visitor Management System"
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"
    SECRET_KEY: str = "temple-secret-key-change-in-production-2026"
    JWT_SECRET: str = "temple-jwt-secret-change-in-production-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 Hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database Configuration (Neon PostgreSQL or SQLite local fallback)
    DATABASE_URL: str = "sqlite+aiosqlite:///./temple.db"
    SYNC_DATABASE_URL: str = "sqlite:///./temple.db"

    # Redis & Celery
    REDIS_URL: str = DEFAULT_REDIS_URL
    CELERY_BROKER_URL: str = DEFAULT_REDIS_URL
    CELERY_RESULT_BACKEND: str = DEFAULT_REDIS_URL

    # Messaging
    SMS_GATEWAY_URL: str = "https://api.sms-provider.com/v1/send"
    SMS_API_KEY: str = "mock_sms_api_key"
    WHATSAPP_GATEWAY_URL: str = "https://graph.facebook.com/v18.0/me/messages"
    WHATSAPP_ACCESS_TOKEN: str = "mock_whatsapp_token"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://bejewelled-kitsune-115083.netlify.app",
        "https://admin-web-kalki.vercel.app",
        "*",
    ]

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            raise ValueError(
                "CRITICAL STARTUP FAILURE: DATABASE_URL environment variable is missing or empty. "
                "Please configure DATABASE_URL in backend/.env file (e.g. Neon PostgreSQL or SQLite)."
            )
        return v.strip()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
