# app/main.py - Version without rate limiting
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.v1.api import api_router
from app.core.config import settings
from app.middleware.error_handler import error_handler_middleware
from app.core.cache import cache_manager
from app.models.database import engine, Base
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background tasks
background_tasks = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting TikTok Shop Integration Service...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    # Connect to cache
    await cache_manager.connect()
    logger.info("Cache service connected")
    
    # Start token refresh scheduler
    try:
        from app.utils.token_refresh_scheduler import TokenRefreshScheduler
        token_scheduler = TokenRefreshScheduler()
        refresh_task = asyncio.create_task(token_scheduler.start())
        background_tasks.append(refresh_task)
        logger.info("Token refresh scheduler started")
    except Exception as e:
        logger.error(f"Failed to start token refresh scheduler: {e}")
    
    # Start webhook retry worker
    try:
        from app.services.webhook_retry_worker import WebhookRetryWorker
        retry_worker = WebhookRetryWorker()
        retry_task = asyncio.create_task(retry_worker.start())
        background_tasks.append(retry_task)
        logger.info("Webhook retry worker started")
    except Exception as e:
        logger.error(f"Failed to start webhook retry worker: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TikTok Shop Integration Service...")
    
    # Cancel background tasks
    for task in background_tasks:
        task.cancel()
    
    await asyncio.gather(*background_tasks, return_exceptions=True)
    logger.info("Background tasks stopped")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this properly in production
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"]
)

# Add custom error handler
app.middleware("http")(error_handler_middleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "documentation": "/docs",
        "health_check": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {}
    }
    
    # Check database
    try:
        from sqlalchemy import text
        from app.models.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check cache
    health_status["services"]["cache"] = "healthy" if cache_manager else "unavailable"
    
    return health_status

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.DEBUG:
        error_detail = str(exc)
    else:
        error_detail = "An internal error occurred"
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": error_detail,
            "type": "internal_server_error"
        }
    )