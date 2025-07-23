# app/core/config.py - Fixed Campaign Service Configuration
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import json


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "LaunchPAID Campaign Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Service Configuration
    SERVICE_NAME: str = "campaign-service"
    SERVICE_PORT: int = 8002
    SERVICE_HOST: str = "0.0.0.0"

    # Database - Single source of truth
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/crm_campaigns_db"
    
    # Security (FIXED: Use consistent field names)
    SECRET_KEY: str = "super-secret-key-for-campaign-service-change-in-production-32-chars"
    JWT_SECRET_KEY: str = "jwt-secret-key-for-campaign-service-change-in-production-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    @property
    def SECRET_KEY(self) -> str:
        return self.JWT_SECRET_KEY

    # CORS - Service specific
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001"
    ]

    # Redis Configuration
    REDIS_URL: Optional[str] = None

    # External Services
    TIKTOK_SHOP_API_URL: str = "https://api.tiktokshop.com"
    DISCORD_BOT_TOKEN: Optional[str] = None
    SENDBLUE_API_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    FANBASIS_API_KEY: Optional[str] = None

    # Microservice URLs (for inter-service communication)
    USER_SERVICE_URL: str = "http://localhost:8000"
    ANALYTICS_SERVICE_URL: str = "http://localhost:8003"
    PAYMENT_SERVICE_URL: str = "http://localhost:8004"
    INTEGRATION_SERVICE_URL: str = "http://localhost:8005"

    # Rate Limiting (service specific)
    RATE_LIMIT_ENABLED: bool = True
    GLOBAL_RATE_LIMIT: str = "200/minute"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [v.strip("[]").strip('"').strip()]
            elif "," in v:
                return [i.strip() for i in v.split(",")]
            else:
                return [v.strip()]
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Add this to ignore extra fields instead of failing
        extra = "ignore"


# Instantiate settings
settings = Settings()