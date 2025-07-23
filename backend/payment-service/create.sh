#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if project name is provided
if [ -z "$1" ]; then
    print_error "Please provide a project name"
    echo "Usage: $0 <project-name>"
    echo "Example: $0 payment-service"
    exit 1
fi

PROJECT_NAME=$1

print_header "Creating Payment Service Project Structure"
print_status "Creating project: $PROJECT_NAME"

# Create main project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Create main app structure
print_status "Creating main application structure..."
mkdir -p app/{api/endpoints,core,models,schemas,crud,services,external,utils,workers}

# Create test structure
print_status "Creating test structure..."
mkdir -p tests/{api/test_endpoints,services,external,utils}

# Create other directories
print_status "Creating additional directories..."
mkdir -p {alembic/versions,scripts,docs,docker}

print_status "Creating Python __init__.py files..."

# Create __init__.py files
touch app/__init__.py
touch app/api/__init__.py
touch app/api/endpoints/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/crud/__init__.py
touch app/services/__init__.py
touch app/external/__init__.py
touch app/utils/__init__.py
touch app/workers/__init__.py

touch tests/__init__.py
touch tests/api/__init__.py
touch tests/api/test_endpoints/__init__.py
touch tests/services/__init__.py
touch tests/external/__init__.py
touch tests/utils/__init__.py

touch scripts/__init__.py

print_status "Creating main application files..."

# Create app/main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import earnings, payments, referrals, schedules, webhooks
from app.core.config import settings
from app.core.exceptions import add_exception_handlers

app = FastAPI(
    title="Launchpaid - Payment Service",
    version="1.0.0",
    description="API for managing creator earnings, payments, and financial operations.",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(earnings.router, prefix="/earnings", tags=["Earnings"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(referrals.router, prefix="/referrals", tags=["Referrals"])
app.include_router(schedules.router, prefix="/schedules", tags=["Payment Schedules"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/")
async def root():
    return {"message": "Payment Service is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}
EOF

# Create app/core/config.py
cat > app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/payment_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    FANBASIS_API_KEY: str = ""
    FANBASIS_WEBHOOK_SECRET: str = ""
    
    # Service URLs
    USER_SERVICE_URL: str = "http://localhost:8001"
    CAMPAIGN_SERVICE_URL: str = "http://localhost:8000"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Payment Settings
    MINIMUM_PAYOUT_AMOUNT: float = 10.00
    DEFAULT_PAYMENT_DELAY_DAYS: int = 3
    
    # Redis/Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create app/core/database.py
cat > app/core/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# Create app/core/security.py
cat > app/core/security.py << 'EOF'
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token_data: dict = Depends(verify_token)):
    return token_data

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
EOF

# Create app/core/exceptions.py
cat > app/core/exceptions.py << 'EOF'
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class PaymentServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class PaymentProcessingError(PaymentServiceException):
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(message, 402)

class InsufficientFundsError(PaymentServiceException):
    def __init__(self, message: str = "Insufficient funds for payout"):
        super().__init__(message, 402)

class InvalidPaymentMethodError(PaymentServiceException):
    def __init__(self, message: str = "Invalid payment method"):
        super().__init__(message, 400)

def add_exception_handlers(app):
    @app.exception_handler(PaymentServiceException)
    async def payment_service_exception_handler(request: Request, exc: PaymentServiceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors()}
        )
EOF

# Create models
print_status "Creating model files..."

cat > app/models/base.py << 'EOF'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
import datetime

Base = declarative_base()

def update_updated_at_column():
    return datetime.datetime.now(datetime.timezone.utc)
EOF

cat > app/models/payment_enums.py << 'EOF'
import enum

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"

class PaymentType(str, enum.Enum):
    base_payout = "base_payout"
    gmv_commission = "gmv_commission"
    bonus = "bonus"
    leaderboard_bonus = "leaderboard_bonus"
    referral_bonus = "referral_bonus"
    manual_adjustment = "manual_adjustment"

class PayoutMethod(str, enum.Enum):
    stripe = "stripe"
    fanbasis = "fanbasis"
    manual = "manual"
    bank_transfer = "bank_transfer"
EOF

# Create placeholder files for other models
touch app/models/creator_earnings.py
touch app/models/payment.py
touch app/models/payment_schedule.py
touch app/models/referral.py

# Create schema files
print_status "Creating schema files..."
touch app/schemas/creator_earnings.py
touch app/schemas/payment.py
touch app/schemas/payment_schedule.py
touch app/schemas/referral.py
touch app/schemas/webhook.py

# Create CRUD files
print_status "Creating CRUD files..."
touch app/crud/creator_earnings.py
touch app/crud/payment.py
touch app/crud/payment_schedule.py
touch app/crud/referral.py

# Create service files
print_status "Creating service files..."
touch app/services/earnings_service.py
touch app/services/payment_service.py
touch app/services/referral_service.py
touch app/services/schedule_service.py
touch app/services/webhook_service.py

# Create external client files
print_status "Creating external client files..."
touch app/external/stripe_client.py
touch app/external/fanbasis_client.py
touch app/external/user_service_client.py
touch app/external/campaign_service_client.py

# Create utility files
print_status "Creating utility files..."

cat > app/utils/calculations.py << 'EOF'
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List

def calculate_gmv_commission(gmv_amount: float, commission_rate: float) -> float:
    """Calculate GMV commission based on rate"""
    return round(gmv_amount * (commission_rate / 100), 2)

def calculate_bonus_tier_amount(gmv: float, bonus_tiers: List[Dict]) -> float:
    """Calculate bonus amount based on GMV and tier structure"""
    # TODO: Implement bonus tier calculation logic
    return 0.0

def calculate_leaderboard_bonus(position: int, leaderboard_config: Dict) -> float:
    """Calculate leaderboard bonus based on position"""
    # TODO: Implement leaderboard bonus calculation logic
    return 0.0

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string"""
    return f"${amount:.2f}"

def round_currency(amount: float) -> float:
    """Round amount to 2 decimal places"""
    return round(amount, 2)
EOF

touch app/utils/validators.py
touch app/utils/formatters.py
touch app/utils/notifications.py

# Create worker files
print_status "Creating worker files..."
touch app/workers/payment_processor.py
touch app/workers/earnings_calculator.py
touch app/workers/webhook_handler.py

# Create API endpoint files
print_status "Creating API endpoint files..."

cat > app/api/deps.py << 'EOF'
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role

# Re-export common dependencies
__all__ = ["get_db", "get_current_user", "require_role"]
EOF

# Create placeholder endpoint files
cat > app/api/endpoints/earnings.py << 'EOF'
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role

router = APIRouter()

@router.get("/")
async def get_earnings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return {"message": "Earnings endpoint"}

@router.get("/creator/{creator_id}")
async def get_creator_earnings(
    creator_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return {"message": f"Creator {creator_id} earnings"}
EOF

cat > app/api/endpoints/payments.py << 'EOF'
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role

router = APIRouter()

@router.get("/")
async def get_payments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return {"message": "Payments endpoint"}

@router.post("/")
async def create_payment(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["agency", "admin"]))
):
    return {"message": "Create payment"}
EOF

cat > app/api/endpoints/referrals.py << 'EOF'
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_referrals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return {"message": "Referrals endpoint"}
EOF

cat > app/api/endpoints/schedules.py << 'EOF'
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role

router = APIRouter()

@router.get("/")
async def get_payment_schedules(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["agency", "admin"]))
):
    return {"message": "Payment schedules endpoint"}
EOF

cat > app/api/endpoints/webhooks.py << 'EOF'
from fastapi import APIRouter, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    return {"message": "Stripe webhook received"}

@router.post("/fanbasis")
async def fanbasis_webhook(request: Request):
    return {"message": "Fanbasis webhook received"}
EOF

# Create test files
print_status "Creating test files..."

cat > tests/conftest.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
EOF

cat > tests/test_main.py << 'EOF'
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Payment Service is running!"}

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "payment-service"}
EOF

# Create placeholder test files
touch tests/api/test_endpoints/test_earnings.py
touch tests/api/test_endpoints/test_payments.py
touch tests/api/test_endpoints/test_referrals.py
touch tests/api/test_endpoints/test_webhooks.py
touch tests/services/test_earnings_service.py
touch tests/services/test_payment_service.py
touch tests/services/test_referral_service.py
touch tests/services/test_webhook_service.py
touch tests/external/test_stripe_client.py
touch tests/external/test_fanbasis_client.py
touch tests/utils/test_calculations.py
touch tests/utils/test_validators.py

# Create configuration files
print_status "Creating configuration files..."

cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2
celery==5.3.4
redis==5.0.1
stripe==7.8.0
python-dotenv==1.0.0
EOF

cat > requirements-dev.txt << 'EOF'
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
EOF

cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/payment_db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
FANBASIS_API_KEY=your_fanbasis_api_key
FANBASIS_WEBHOOK_SECRET=your_fanbasis_webhook_secret

# Service URLs
USER_SERVICE_URL=http://localhost:8001
CAMPAIGN_SERVICE_URL=http://localhost:8000

# Payment Settings
MINIMUM_PAYOUT_AMOUNT=10.00
DEFAULT_PAYMENT_DELAY_DAYS=3

# Redis/Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EOF

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# FastAPI
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Logs
*.log

# Docker
.dockerignore

# OS
.DS_Store
Thumbs.db

# Alembic
alembic/versions/*.py
!alembic/versions/__init__.py
EOF

cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
asyncio_mode = auto
EOF

cat > alembic.ini << 'EOF'
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:password@localhost:5432/payment_db

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# Create Docker files
print_status "Creating Docker configuration..."

cat > docker/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
EOF

cat > docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  payment-service:
    build: 
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/payment_db
      - SECRET_KEY=your-secret-key
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ..:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: payment_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"

  worker:
    build: 
      context: ..
      dockerfile: docker/Dockerfile
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/payment_db
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ..:/app

volumes:
  postgres_data:
EOF

cat > docker/docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  payment-service:
    build: 
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/payment_db
      - SECRET_KEY=dev-secret-key
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ..:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: payment_db
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"

volumes:
  postgres_data_dev:
EOF

# Create scripts
print_status "Creating utility scripts..."

cat > scripts/create_db.py << 'EOF'
#!/usr/bin/env python3
"""
Script to create database tables
"""
from app.core.database import engine
from app.models.base import Base
from app.models import *  # Import all models

def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
EOF

cat > scripts/seed_data.py << 'EOF'
#!/usr/bin/env python3
"""
Script to seed sample data
"""
from app.core.database import SessionLocal
from app.models import *  # Import all models

def seed_data():
    db = SessionLocal()
    try:
        print("Seeding sample data...")
        # Add sample data here
        print("Sample data seeded successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
EOF

chmod +x scripts/create_db.py
chmod +x scripts/seed_data.py

# Create documentation
print_status "Creating documentation..."

cat > docs/api.md << 'EOF'
# Payment Service API Documentation

## Overview
This document describes the REST API endpoints for the Payment Service.

## Authentication
All endpoints require JWT token authentication.

## Endpoints

### Earnings
- `GET /earnings/` - Get earnings summary
- `GET /earnings/creator/{creator_id}` - Get creator earnings

### Payments
- `GET /payments/` - List payments
- `POST /payments/` - Create payment
- `GET /payments/{payment_id}` - Get payment details

### Referrals
- `GET /referrals/` - List referrals
- `POST /referrals/` - Create referral

### Payment Schedules
- `GET /schedules/` - List payment schedules
- `POST /schedules/` - Create payment schedule

### Webhooks
- `POST /webhooks/stripe` - Stripe webhook endpoint
- `POST /webhooks/fanbasis` - Fanbasis webhook endpoint
EOF

cat > docs/business_logic.md << 'EOF'
# Payment Service Business Logic

## Earnings Calculation

### Base Earnings
- Fixed amount per deliverable completion
- Configured at campaign level

### GMV Commission
- Percentage of Gross Merchandise Value
- Applied to TikTok Shop sales

### Bonus Calculations
- Tier-based bonuses for GMV milestones
- Leaderboard bonuses for top performers

## Payment Processing

### Automated Payouts
- Triggered by deliverable completion
- Scheduled payments (weekly, bi-weekly, monthly)
- Minimum payout thresholds

### Manual Payouts
- Agency-initiated payments
- Bonus adjustments
- Dispute resolutions

## Referral System
- Commission for referred creators
- Bonus payments for successful referrals
EOF

cat > docs/integration.md << 'EOF'
# External Service Integration

## Stripe Integration
- Payment processing
- Webhook handling
- Failed payment retry

## Fanbasis Integration
- Alternative payment processor
- Performance-based payouts

## Service Communication
- User Service: User validation
- Campaign Service: Campaign data
EOF

cat > docs/deployment.md << 'EOF'
# Deployment Instructions

## Development
```bash
# Using Docker Compose
docker-compose -f docker/docker-compose.dev.yml up -d

# Local development
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8002
```

## Production
```bash
# Build and deploy
docker-compose -f docker/docker-compose.yml up -d

# Environment variables
cp .env.example .env
# Edit .env with production values
```

## Database Migration
```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```
EOF

# Create README.md
cat > README.md << 'EOF'
# Payment Service

## Overview
Payment service for TikTok Shop Creator CRM platform handling creator earnings, payouts, and financial operations.

## Features
- Creator earnings calculation
- Automated payment processing
- Stripe and Fanbasis integration
- Referral bonus system
- Payment scheduling and automation
- Webhook handling for payment status updates

## Quick Start
1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose -f docker/docker-compose.dev.yml up -d`
4. Access API at `http://localhost:8002`

## API Documentation
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Development

### Installation
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running locally
```bash
uvicorn app.main:app --reload --port 8002
```

### Testing
```bash
pytest
pytest --cov=app tests/
```

### Code Quality
```bash
black .
flake8
mypy .
```

## Database Setup
```bash
# Create tables
python scripts/create_db.py

# Seed sample data
python scripts/seed_data.py

# Database migrations
alembic upgrade head
```

## Docker Development
```bash
# Start all services
docker-compose -f docker/docker-compose.dev.yml up -d

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f payment-service

# Stop services
docker-compose -f docker/docker-compose.dev.yml down
```

## Environment Variables
See `.env.example` for required environment variables.

## Project Structure
```
payment-service/
├── app/                 # Main application code
├── tests/              # Test files
├── alembic/            # Database migrations
├── scripts/            # Utility scripts
├── docs/               # Documentation
├── docker/             # Docker configuration
└── requirements.txt    # Dependencies
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests and linting
5. Submit a pull request

## License
MIT License
EOF

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "payment-service"
version = "1.0.0"
description = "Payment service for TikTok Shop Creator CRM"
authors = [{name = "Your Team", email = "team@yourcompany.com"}]
license = {text = "MIT"}
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "alembic>=1.12.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.0",
    "python-multipart>=0.0.6",
    "httpx>=0.25.0",
    "celery>=5.3.0",
    "redis>=5.0.0",
    "stripe>=7.8.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "flake8>=6.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
]

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --tb=short"
asyncio_mode = "auto"
EOF

print_header "Project Structure Created Successfully!"
print_status "Project '$PROJECT_NAME' has been created with the following structure:"
echo ""
tree -a -I '__pycache__|*.pyc|.git' "$PROJECT_NAME" 2>/dev/null || find "$PROJECT_NAME" -type f | head -20

print_status "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. cp .env.example .env"
echo "3. Edit .env with your configuration"
echo "4. pip install -r requirements.txt"
echo "5. pip install -r requirements-dev.txt"
echo "6. Run: uvicorn app.main:app --reload --port 8002"
echo ""
print_status "Or use Docker:"
echo "1. cd $PROJECT_NAME"
echo "2. docker-compose -f docker/docker-compose.dev.yml up -d"
echo ""
print_warning "Remember to implement the model files, services, and business logic!"
print_header "Happy coding! 🚀"
EOF