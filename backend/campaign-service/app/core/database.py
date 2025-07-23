# app/core/database.py - Fixed Database Configuration
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

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
    # SQLite configuration (for testing)
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
else:
    # PostgreSQL configuration (production)
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
    })

# Create engine
try:
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    logger.info("Database engine created successfully")
    DATABASE_CONFIGURED = True
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    DATABASE_CONFIGURED = False
    # Create a dummy engine for fallback
    engine = create_engine("sqlite:///:memory:", **engine_kwargs)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Event listeners for PostgreSQL schema creation
@event.listens_for(engine, "connect")
def create_schemas(dbapi_connection, connection_record):
    """Create schemas if they don't exist"""
    if not settings.DATABASE_URL.startswith("sqlite"):
        try:
            with dbapi_connection.cursor() as cursor:
                # Create schemas for microservices
                schemas = ['users', 'campaigns', 'analytics', 'payments', 'integrations']
                for schema in schemas:
                    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                dbapi_connection.commit()
                logger.info(f"Schemas created/verified: {schemas}")
        except Exception as e:
            logger.error(f"Failed to create schemas: {e}")

# Database dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI endpoints.
    Yields a database session and ensures it's closed after use.
    """
    if not DATABASE_CONFIGURED:
        logger.error("Database not configured properly")
        raise Exception("Database connection not available")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Database status check function
def get_database_status() -> dict:
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
        with engine.connect() as connection:
            # Test connection with simple query
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get database info
            if settings.DATABASE_URL.startswith("postgresql"):
                db_type = "PostgreSQL"
                version_result = connection.execute(text("SELECT version()"))
                version = version_result.fetchone()[0]
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
def init_db():
    """
    Initialize database tables.
    Should be called on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

# Database cleanup function
def close_db():
    """
    Close database connections.
    Should be called on application shutdown.
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

# Utility function for running raw SQL
def execute_sql(sql: str, params: dict = None) -> any:
    """
    Execute raw SQL query.
    Use with caution and prefer SQLAlchemy ORM when possible.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql), params or {})
            connection.commit()
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
        status = get_database_status()
        if status["connection"]:
            return {"database": "healthy", "details": status}
        else:
            return {"database": "unhealthy", "details": status}
    except Exception as e:
        return {"database": "error", "message": str(e)}