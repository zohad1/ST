
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:admin@localhost:5432/crm_campaigns_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    jwt_secret_key: str = "jwt-secret-key-for-development-change-in-production-minimum-32-chars"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # External service URLs
    user_service_url: str = "http://user-service:8000"
    campaign_service_url: str = "http://campaign-service:8003"
    payment_service_url: str = "http://payment-service:8004"
    integration_service_url: str = "http://integration-service:8005"
    
    # Analytics specific settings
    cache_ttl_seconds: int = 300  # 5 minutes
    max_date_range_days: int = 365
    default_pagination_limit: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
