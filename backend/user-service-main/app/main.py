# app/main.py - FIXED VERSION using async database functions

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
import asyncio
from datetime import datetime

# FIXED: Import async functions from your database.py
from app.core.config import settings
from app.core.database import (
    get_db,  # This is async and returns AsyncSession
    init_db_sync as init_db,  # Use sync wrapper for startup
    verify_db_setup,  # This is async
    engine, 
    check_db_connection  # This is async
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    logger.info(f"📋 Service: {settings.SERVICE_NAME}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 Host: {settings.SERVICE_HOST}:{settings.SERVICE_PORT}")
    logger.info(f"📚 Docs: http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/api/docs")
    logger.info("=" * 60)
    
    # Check database connection first
    try:
        # Use async version with await
        if await check_db_connection():
            logger.info("✅ Database connection successful")
            
            # Initialize database - use sync wrapper
            init_db()
            logger.info("✅ Database initialized successfully")
            
            # Verify database setup - use async version
            await verify_db_setup()
            logger.info("✅ Database setup verified")
            
        else:
            logger.error("❌ Database connection failed")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        # Continue startup anyway for development
    
    # Log available endpoints
    logger.info("📍 Available endpoints:")
    logger.info("   🔐 Auth: /api/v1/auth/* (login, register, etc.)")
    logger.info("   👥 Users: /api/v1/users/* (profile, etc.)")
    logger.info("   ⚕️  Health: /health")
    logger.info("   🗺️  Routes: /api/routes")
    
    yield
    
    # Shutdown
    logger.info(f"🛑 {settings.SERVICE_NAME} shutting down...")
    await engine.dispose()  # This is async
    logger.info("👋 Goodbye!")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Mount static directory for profile images and other uploads
static_dir_path = os.path.join(os.getcwd(), "static")
os.makedirs(static_dir_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir_path), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# INCLUDE ROUTERS FIRST
# ==========================================
try:
    from app.api.v1.auth import router as auth_router
    from app.api.v1.users import router as users_router
    
    # Include the routers BEFORE any other endpoints
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    
    logger.info("✅ API routers included successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import API routers: {e}")
    logger.warning("Running without JWT authentication")

# ==========================================
# UTILITY ENDPOINTS ONLY
# ==========================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Welcome to LaunchPAID User Service API",
        "version": settings.APP_VERSION,
        "service": settings.SERVICE_NAME,
        "docs": "/api/docs",
        "status": "running",
        "endpoints": {
            "auth": "/api/v1/auth/*",
            "users": "/api/v1/users/*",
            "health": "/health",
            "routes": "/api/routes"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with better error handling"""
    health_status = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "unknown",
        "timestamp": datetime.now().isoformat()
    }
    
    # Check database connection with timeout
    try:
        if await check_db_connection():  # This is async
            health_status["database"] = "connected"
        else:
            health_status["database"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["database"] = f"error: {str(e)[:100]}"
        health_status["status"] = "degraded"
    
    # Return appropriate HTTP status
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )

# Simple health check that always works (for debugging)
@app.get("/health/simple")
async def simple_health_check():
    """Simple health check that doesn't check database"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "message": "Service is running"
    }

@app.get("/health/db")
async def db_health_check():
    """Database-specific health check"""
    try:
        if await check_db_connection():  # This is async
            return {
                "status": "healthy",
                "database": "connected"
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "database": "disconnected"
                }
            )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
        )

@app.get("/api/routes")
async def list_routes():
    """Debug endpoint to see all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method != "HEAD":
                    routes.append({
                        "method": method,
                        "path": route.path,
                        "name": getattr(route, 'name', 'N/A'),
                        "tags": getattr(route, 'tags', [])
                    })
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path']),
        "auth_endpoints": [r for r in routes if r['path'].startswith('/api/v1/auth')],
        "user_endpoints": [r for r in routes if r['path'].startswith('/api/v1/users')]
    }

# ==========================================
# EXCEPTION HANDLERS
# ==========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Global exception handler caught: {exc}")
    logger.error(f"Request: {request.method} {request.url}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "success": False,
            "service": settings.SERVICE_NAME,
            "error_type": type(exc).__name__
        }
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Endpoint not found: {request.method} {request.url.path}",
            "success": False,
            "service": settings.SERVICE_NAME,
            "available_endpoints": "/api/routes"
        }
    )

# ==========================================
# DEV SERVER
# ==========================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🔧 Starting development server...")
    logger.info(f"📡 Server will be available at: http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}")
    logger.info(f"📖 API docs at: http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/api/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )