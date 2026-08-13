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
    N8N_WHATSAPP_WEBHOOK_URL: str = "https://n8n.kalkiseva.org/webhook/whatsapp-send"
    N8N_API_KEY: str = "n8n_mock_api_key"

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

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://bejewelled-kitsune-115083.netlify.app",
            "*",
        ]

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            return "sqlite+aiosqlite:///./temple.db"
        url = v.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        if "postgresql+asyncpg://" in url:
            url = url.replace("sslmode=require", "ssl=require").replace("sslmode=prefer", "ssl=prefer").replace("sslmode=disable", "ssl=disable")
            url = url.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
