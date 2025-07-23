# app/main.py
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import logging
import traceback
from typing import Dict, Any
import uuid
from datetime import datetime

# Import database
from app.core.database import init_db, get_database_status, get_db, create_schemas_async
from app.core.security import get_current_user, create_access_token

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LaunchPAID Campaign Service",
    version="1.0.0",
    description="TikTok Influencer Marketing Platform - Campaign Service",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://localhost:3000",
    "https://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Create API router
api_router = APIRouter()

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    errors = []
    for error in exc.errors():
        field_name = " -> ".join(str(x) for x in error['loc'][1:])
        errors.append({
            "field": field_name,
            "message": error['msg'],
            "type": error['type'],
            "input": str(error.get('input', 'N/A'))
        })
    
    logger.error(f"Validation error: {errors}")
    body = await request.body()
    logger.error(f"Request body: {body}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": errors,
            "body_received": body.decode() if body else "Empty body"
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {str(exc)}")
    logger.error(f"Error type: {type(exc).__name__}")
    logger.error(traceback.format_exc())
    
    error_message = "Database operation failed"
    if "duplicate key" in str(exc).lower():
        error_message = "This record already exists"
    elif "foreign key" in str(exc).lower():
        error_message = "Related record not found"
    elif "not null" in str(exc).lower():
        error_message = "Required field is missing"
    elif "jsonb" in str(exc).lower():
        error_message = "Invalid JSON data format"
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": error_message,
            "error_type": type(exc).__name__,
            "technical_detail": str(exc)[:500]
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "path": str(request.url)
        }
    )

# Include routers - Dashboard first (if exists)
try:
    from app.api.endpoints import dashboard
    api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
    logger.info("✅ Dashboard routes loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Dashboard routes not available: {e}")

# Include Campaigns router
try:
    from app.api.endpoints import campaigns
    api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
    logger.info("✅ Campaign routes loaded successfully")
    
    # Log campaign routes
    logger.info("Campaign routes:")
    for route in campaigns.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"  - {route.methods} /api/v1/campaigns{route.path}")
except Exception as e:
    logger.error(f"❌ Failed to load campaign routes: {e}")
    logger.error(traceback.format_exc())

# Include Applications router - CRITICAL SECTION
try:
    from app.api.endpoints import applications
    api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
    logger.info("✅ Application routes loaded successfully")
    
    # Log application routes for debugging
    logger.info("Application routes:")
    for route in applications.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"  - {route.methods} /api/v1/applications{route.path}")
except Exception as e:
    logger.error(f"❌ Failed to load application routes: {e}")
    logger.error(traceback.format_exc())

# Include Deliverables router
try:
    from app.api.endpoints import deliverables
    api_router.include_router(deliverables.router, prefix="/deliverables", tags=["Deliverables"])
    logger.info("✅ Deliverable routes loaded successfully")
    
    # Log deliverable routes for debugging
    logger.info("Deliverable routes:")
    for route in deliverables.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"  - {route.methods} /api/v1/deliverables{route.path}")
except Exception as e:
    logger.error(f"❌ Failed to load deliverable routes: {e}")
    logger.error(traceback.format_exc())

# Include Leaderboard router
try:
    from app.api.endpoints import leaderboard
    api_router.include_router(leaderboard.router, tags=["Leaderboard"])
    logger.info("✅ Leaderboard routes loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load leaderboard routes: {e}")
    logger.error(traceback.format_exc())

# Include Analytics router
try:
    from app.api.endpoints import analytics
    api_router.include_router(analytics.router, tags=["Analytics"])
    logger.info("✅ Analytics routes loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load analytics routes: {e}")
    logger.error(traceback.format_exc())

# Test endpoints
@api_router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    db_status = await get_database_status()
    return {
        "message": "API is working!",
        "service": "campaign-service",
        "status": "success",
        "database_connected": db_status["connection"],
        "endpoints_working": True,
        "version": "1.0.0",
        "cors_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = await get_database_status()
    return {
        "status": "healthy" if db_status["connection"] else "unhealthy",
        "service": "campaign-service",
        "database": db_status,
        "cors_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

# Mount the API router with /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    db_status = await get_database_status()
    return {
        "message": "Welcome to LaunchPAID Campaign Service",
        "version": "1.0.0",
        "description": "TikTok Influencer Marketing Platform - Campaign Service",
        "docs": "/api/docs",
        "status": "active",
        "port": 8002,
        "database": db_status,
        "cors_enabled": True,
        "allowed_origins": origins,
        "endpoints": {
            "health": "/health",
            "api_health": "/api/v1/health",
            "api_test": "/api/v1/test",
            "documentation": "/api/docs",
            "openapi": "/api/openapi.json"
        }
    }

# Health check endpoint at root level
@app.get("/health")
async def root_health_check():
    db_status = await get_database_status()
    return {
        "status": "healthy" if db_status["connection"] else "unhealthy",
        "service": "campaign-service",
        "version": "1.0.0",
        "database": db_status,
        "cors_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("🚀 LaunchPAID Campaign Service starting...")
    logger.info("=" * 50)
    logger.info(f"📍 Port: 8002")
    logger.info(f"🔧 Environment: Development")
    logger.info(f"🌐 CORS enabled for origins: {origins}")
    logger.info(f"⏰ Startup Time: {datetime.now().isoformat()}")
    
    # Initialize database
    logger.info("\n🗄️  Initializing database...")
    try:
        db_init_success = await init_db()
        
        if db_init_success:
            logger.info("✅ Database initialized successfully")
            await create_schemas_async()
            db_status = await get_database_status()
            logger.info(f"📊 Database status: {db_status}")
        else:
            logger.error("❌ Database initialization failed")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        logger.error(traceback.format_exc())
    
    # Log all registered routes
    logger.info("\n📍 ALL REGISTERED ROUTES:")
    route_count = 0
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            # Skip OPTIONS routes for clarity
            if route.methods != {'OPTIONS'}:
                logger.info(f"   {route.methods} -> {route.path}")
                route_count += 1
    logger.info(f"Total routes: {route_count}")
    
    # Specifically check for application routes
    logger.info("\n🔍 APPLICATION-SPECIFIC ROUTES:")
    app_route_count = 0
    for route in app.routes:
        if hasattr(route, 'path') and 'application' in str(route.path).lower():
            logger.info(f"   {route.methods if hasattr(route, 'methods') else 'N/A'} -> {route.path}")
            app_route_count += 1
    logger.info(f"Application routes found: {app_route_count}")
    
    logger.info("=" * 50)
    logger.info("✅ Service ready!")
    logger.info("📝 API Documentation: http://localhost:8002/api/docs")
    logger.info("=" * 50)

# Shutdown event  
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Campaign Service shutting down...")
    try:
        from app.core.database import close_db
        await close_db()
        logger.info("🗄️  Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    logger.info("👋 Goodbye!")

# Add OPTIONS handler for preflight requests
@app.options("/{full_path:path}")
async def options_handler(request: Request):
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Run with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="debug"
    )