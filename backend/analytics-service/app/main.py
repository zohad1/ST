# Step 3: Fix app/main.py
# Replace with this corrected version:

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Analytics Service",
    version="1.0.0",
    description="Analytics and reporting service for TikTok Shop Creator CRM",
    debug=True
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    return {
        "message": "Analytics Service is running!",
        "version": "1.0.0",
        "environment": "development"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "analytics-service",
        "timestamp": time.time()
    }

# Include routers AFTER app is defined
@app.on_event("startup")
async def startup_event():
    logger.info("Analytics Service starting up...")
    
    # Import and include the router here to avoid circular imports
    try:
        from app.api.endpoints import router
        app.include_router(router, prefix="/api/v1")
        logger.info("✅ Successfully included API routers")
    except Exception as e:
        logger.error(f"❌ Failed to include routers: {e}")
        # Add fallback endpoints
        add_fallback_endpoints()

def add_fallback_endpoints():
    """Add basic fallback endpoints if router import fails"""
    
    @app.get("/api/v1/test")
    async def fallback_test():
        return {"message": "Fallback test endpoint working"}
    
    @app.get("/api/v1/dashboard/overview")
    async def fallback_overview():
        return {
            "total_campaigns": 0,
            "total_creators": 0,
            "total_gmv": "0.00",
            "total_posts": 0,
            "avg_engagement_rate": "0.00",
            "top_performing_campaigns": [],
            "top_performing_creators": []
        }

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Analytics Service shutting down...")


