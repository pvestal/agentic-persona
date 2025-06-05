"""
Application configuration using Pydantic Settings
Supports environment variables and .env files
"""

import os
from typing import List, Optional, Dict, Any
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, PostgresDsn, validator, Field, SecretStr
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    APP_NAME: str = "Board of Directors AI System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field("development", regex="^(development|staging|production)$")
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3000
    
    # Security
    SECRET_KEY: SecretStr = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    
    # Database connection pooling
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    
    DATABASE_URL: Optional[PostgresDsn] = None
    ASYNC_DATABASE_URL: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD").get_secret_value() if values.get("POSTGRES_PASSWORD") else None,
            host=values.get("POSTGRES_SERVER"),
            port=str(values.get("POSTGRES_PORT")),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    @validator("ASYNC_DATABASE_URL", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        if values.get("DATABASE_URL"):
            return values.get("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")
        return None
    
    # Redis (for caching and rate limiting)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[SecretStr] = None
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour default
    
    # External APIs
    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Privacy Shield Settings
    PRIVACY_SHIELD_ENABLED: bool = True
    PII_DETECTION_CONFIDENCE: float = 0.8
    ALLOWED_EXTERNAL_APIS: List[str] = [
        "api.openai.com",
        "api.anthropic.com",
        "localhost",
        "127.0.0.1"
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    LOG_FILE: Optional[Path] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None
    
    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: AnyHttpUrl = "http://localhost:8000"
    
    # File Storage
    UPLOAD_DIR: Path = Path("/tmp/board_of_directors/uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Task Processing
    MAX_CONCURRENT_TASKS: int = 10
    TASK_TIMEOUT: int = 300  # 5 minutes
    TASK_RETRY_ATTEMPTS: int = 3
    
    # Board of Directors Settings
    ROTATION_INTERVAL: int = 10  # Rotate chairperson after N tasks
    MIN_QUALITY_SCORE: float = 0.6
    PERFORMANCE_HISTORY_LIMIT: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'
        
    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v: Path) -> Path:
        v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
        
    def get_redis_url(self) -> str:
        """Get Redis URL with password if configured"""
        if self.REDIS_PASSWORD:
            password = self.REDIS_PASSWORD.get_secret_value()
            return f"redis://:{password}@{self.REDIS_URL.split('://')[1]}"
        return self.REDIS_URL
        
    def get_database_uri(self, async_: bool = False) -> str:
        """Get database URI for migrations"""
        if async_:
            return str(self.ASYNC_DATABASE_URL)
        return str(self.DATABASE_URL)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()