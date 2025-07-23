from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import earnings, payments, referrals, schedules, webhooks
from app.core.config import settings
from app.core.exceptions import add_exception_handlers
from app.core.security import get_current_user
from fastapi import Depends

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

# API version prefix
API_PREFIX = "/api/v1"

# Include routers
app.include_router(earnings.router, prefix=f"{API_PREFIX}/earnings", tags=["Earnings"])
app.include_router(payments.router, prefix=f"{API_PREFIX}/payments", tags=["Payments"])
app.include_router(referrals.router, prefix=f"{API_PREFIX}/referrals", tags=["Referrals"])
app.include_router(schedules.router, prefix=f"{API_PREFIX}/schedules", tags=["Payment Schedules"])
app.include_router(webhooks.router, prefix=f"{API_PREFIX}/webhooks", tags=["Webhooks"])

@app.get("/")
async def root():
    return {"message": "Payment Service is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

@app.get("/api/v1/test-auth")
async def test_auth(current_user: dict = Depends(get_current_user)):
    """Test endpoint to verify authentication is working"""
    return {
        "message": "Authentication successful",
        "user_id": current_user.get("sub"),
        "role": current_user.get("role"),
        "token_type": current_user.get("type")
    }
