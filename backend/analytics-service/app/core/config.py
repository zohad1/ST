
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:5432/crm_campaigns_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    JWT_SECRET_KEY: str = "jwt-secret-key-for-development-change-in-production-minimum-32-chars"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Service Configuration
    SERVICE_NAME: str = "analytics-service"
    SERVICE_PORT: str = "8003"
    
    # External service URLs
    USER_SERVICE_URL: str = "http://user-service:8000"
    CAMPAIGN_SERVICE_URL: str = "http://campaign-service:8002"
    PAYMENT_SERVICE_URL: str = "http://payment-service:8004"
    INTEGRATION_SERVICE_URL: str = "http://integration-service:8005"
    
    # Analytics specific settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    MAX_DATE_RANGE_DAYS: int = 365
    DEFAULT_PAGINATION_LIMIT: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
