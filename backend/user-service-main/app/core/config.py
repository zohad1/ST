# app/core/config.py - User Service Configuration
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import field_validator
import json


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "LaunchPAID User Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Service Configuration
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8000
    SERVICE_HOST: str = "0.0.0.0"

    # Database - Single source of truth
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@postgres:5432/launchpaid_db"
    
    # Security
    SECRET_KEY: str = "super-secret-key-for-development-change-in-production-minimum-32-chars"
    JWT_SECRET_KEY: str = "jwt-secret-key-for-development-change-in-production-minimum-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REMEMBER_ME_DAYS: int = 30

    # CORS - Properly formatted
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001"
    ]

    

    # Email Configuration
    MAIL_ENABLED: bool = True
    MAIL_FROM: str = "launchpaid@bytecraftsoft.com"
    MAIL_FROM_NAME: str = "LaunchPAID"

    # SMTP Settings (all required if email enabled)
    SMTP_HOST: str = "mail.bytecraftsoft.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "launchpaid@bytecraftsoft.com"
    SMTP_PASSWORD: str = "0E%*)t(6[!A,84g^"
    SMTP_TLS: bool = True




    # Mailgun Configuration (preferred over SMTP)
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Redis (Optional)
    REDIS_URL: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    LOGIN_RATE_LIMIT: str = "10/minute"
    SIGNUP_RATE_LIMIT: str = "3/hour"
    PASSWORD_RESET_RATE_LIMIT: str = "3/hour"
    VERIFY_EMAIL_RATE_LIMIT: str = "10/hour"
    GLOBAL_RATE_LIMIT: str = "100/minute"

    # Microservice URLs (for inter-service communication)
    CAMPAIGN_SERVICE_URL: str = "http://localhost:8002"
    ANALYTICS_SERVICE_URL: str = "http://localhost:8003"
    PAYMENT_SERVICE_URL: str = "http://localhost:8004"
    INTEGRATION_SERVICE_URL: str = "http://localhost:8005"

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
        if not (v.startswith("postgresql://") or v.startswith("postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string (postgresql:// or postgresql+asyncpg://)")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
    
    # Add these lines to your existing app/core/config.py file
    # Just add this at the end of your Settings class:

    # Service information (add these if missing)
    SERVICE_NAME: str = "user-service"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8000

    # Add cors_origins property if you want to use it later
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from environment"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            try:
                import json
                return json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS


# Instantiate settings
settings = Settings()


