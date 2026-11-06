from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "EVnesia PRO API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "evnesia-super-secret-key-change-this-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 Hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30         # 30 Days

    DATABASE_URL: str = "sqlite:///./autodrive.db"
    # Production connection pool settings (for PostgreSQL / MySQL)
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # Recycle every 30 mins

    # Physical File Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/svg+xml",
        "image/gif",
        "application/pdf"
    ]

    # Amazon S3 / Cloudflare R2 Cloud Storage Settings
    S3_ENDPOINT_URL: Optional[str] = None       # e.g. https://<account_id>.r2.cloudflarestorage.com
    S3_ACCESS_KEY_ID: Optional[str] = None      # Cloud Access Key ID
    S3_SECRET_ACCESS_KEY: Optional[str] = None  # Cloud Secret Access Key
    S3_BUCKET_NAME: Optional[str] = None        # Name of bucket (e.g. evhub-media)
    S3_REGION_NAME: str = "ap-southeast-1"      # e.g. ap-southeast-1 or auto
    S3_PUBLIC_DOMAIN: Optional[str] = None      # e.g. https://cdn.evhub.id or https://pub-xxx.r2.dev

    # Inova CMS Open API Configuration (HMAC-SHA256 Server-to-Server)
    CMS_BASE_URL: str = "https://api-cms.bukin.id/openapi/v1"
    CMS_ACCESS_KEY: Optional[str] = None        # oak_...
    CMS_SECRET: Optional[str] = None            # osk_...
    CMS_PORTAL_ID: Optional[str] = None         # UUID portal Indosatu / Inova CMS
    CMS_SYNC_INTERVAL_MINUTES: int = 15

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:4321",
        "http://127.0.0.1:4321",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
