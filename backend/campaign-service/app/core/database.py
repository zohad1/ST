# app/core/database.py - Async Database Configuration
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
import logging
from typing import AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database engine configuration
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": settings.DEBUG,
}

# Handle different database configurations
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration (for testing) - convert to async
    DATABASE_URL = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
else:
    # PostgreSQL configuration (production) - should already use asyncpg
    DATABASE_URL = settings.DATABASE_URL
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
    })

# Create async engine
try:
    engine = create_async_engine(DATABASE_URL, **engine_kwargs)
    logger.info("Async database engine created successfully")
    DATABASE_CONFIGURED = True
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    DATABASE_CONFIGURED = False
    # Create a dummy engine for fallback
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", **engine_kwargs)

# Create AsyncSessionLocal class
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create Base class for models
Base = declarative_base()

# Async schema creation utility (replaces sync listener)
async def create_schemas_async():
    """Create PostgreSQL schemas asynchronously (call during startup)."""
    if settings.DATABASE_URL.startswith("sqlite"):
        return  # No schemas for SQLite
    try:
        async with engine.begin() as conn:
            schemas = ['users', 'campaigns', 'analytics', 'payments', 'integrations']
            for schema in schemas:
                await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        logger.info("✅ Schemas created/verified")
    except Exception as e:
        logger.error(f"❌ Failed to create schemas: {e}")

# Database dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database dependency for FastAPI endpoints.
    Yields an async database session and ensures it's closed after use.
    """
    if not DATABASE_CONFIGURED:
        logger.error("Database not configured properly")
        raise Exception("Database connection not available")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

# Database status check function
async def get_database_status() -> dict:
    """
    Check database connectivity and return status information.
    """
    if not DATABASE_CONFIGURED:
        return {
            "status": "error",
            "message": "Database engine not configured",
            "connection": False
        }
    
    try:
        async with engine.begin() as connection:
            # Test connection with simple query
            result = await connection.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get database info
            if settings.DATABASE_URL.startswith("postgresql"):
                db_type = "PostgreSQL"
                version_result = await connection.execute(text("SELECT version()"))
                version_row = version_result.fetchone()
                version = version_row[0]
            else:
                db_type = "SQLite"
                version = "Unknown"
            
            return {
                "status": "healthy",
                "connection": True,
                "database_type": db_type,
                "version": version,
                "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local"
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "connection": False,
            "message": str(e)
        }

# Database initialization function
async def init_db():
    """
    Initialize database tables.
    Should be called on application startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

# Database cleanup function
async def close_db():
    """
    Close database connections.
    Should be called on application shutdown.
    """
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

# Utility function for running raw SQL
async def execute_sql(sql: str, params: dict = None) -> any:
    """
    Execute raw SQL query.
    Use with caution and prefer SQLAlchemy ORM when possible.
    """
    try:
        async with engine.begin() as connection:
            result = await connection.execute(text(sql), params or {})
            return result
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        raise

# Health check function specifically for FastAPI
async def check_database_health():
    """
    Async database health check for FastAPI health endpoints.
    """
    try:
        status = await get_database_status()
        if status["connection"]:
            return {"database": "healthy", "details": status}
        else:
            return {"database": "unhealthy", "details": status}
    except Exception as e:
        return {"database": "error", "message": str(e)}