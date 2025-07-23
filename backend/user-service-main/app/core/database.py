# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text, inspect
from typing import AsyncGenerator, Generator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create ASYNC engine for AsyncPG
engine = create_async_engine(
    settings.DATABASE_URL,  # Keep postgresql+asyncpg://...
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,  # Log SQL in debug mode
    # Removed connect_args - AsyncPG doesn't support "options"
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create Base class
Base = declarative_base()

# ASYNC Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency function that yields database sessions.
    Ensures proper cleanup after request completion.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Set schema search path for AsyncPG
            await session.execute(text("SET search_path TO users, public"))
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Legacy SYNC function for backward compatibility with your existing endpoints
def get_db_sync() -> Generator:
    """
    LEGACY: Synchronous database session for backward compatibility.
    This creates a sync session from the async engine - not ideal but works.
    Gradually migrate your endpoints to use async get_db() instead.
    """
    # Import sync sessionmaker
    from sqlalchemy.orm import sessionmaker
    
    # Create a sync engine for legacy support
    # We'll keep this for backward compatibility
    from sqlalchemy import create_engine
    
    # Create sync engine without the problematic options
    sync_engine = create_engine(
        settings.DATABASE_URL.replace('+asyncpg', ''),  # Remove asyncpg for sync
        pool_pre_ping=True,
        pool_size=5,  # Smaller pool for legacy
        max_overflow=10,
        echo=settings.DEBUG,
        # Remove the problematic connect_args
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    
    db = SessionLocal()
    try:
        # Set schema for this session
        db.execute(text("SET search_path TO users, public"))
        yield db
    finally:
        db.close()

# ASYNC Database initialization function
async def init_db():
    """Initialize database with required schemas and extensions"""
    async with engine.begin() as conn:
        # Create schemas
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS users"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS campaigns"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS payments"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS integrations"))
        
        # Create extensions
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
        
        # Create enum types ONLY if they don't exist
        await conn.execute(text("""
            DO $$ 
            BEGIN
                -- Only create if not exists
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'users')) THEN
                    CREATE TYPE users.user_role AS ENUM ('agency', 'creator', 'brand', 'admin');
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'users')) THEN
                    CREATE TYPE users.gender_type AS ENUM ('male', 'female', 'non_binary', 'prefer_not_to_say');
                END IF;
            END $$;
        """))
        
        logger.info("Database schemas and types initialized successfully")
        
        # Create tables if they don't exist
        logger.info("Ensuring database tables exist...")
        try:
            # Import models to ensure they're registered
            from app.models import user  # This registers the models
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.warning(f"Could not create tables via metadata: {e}")
            # Fallback: ensure essential columns exist
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users.users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    role users.user_role NOT NULL DEFAULT 'creator',
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    is_active BOOLEAN DEFAULT true,
                    email_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))

# SYNC version for backward compatibility
def init_db_sync():
    """LEGACY: Sync version of init_db for startup compatibility"""
    import asyncio
    try:
        # Run the async version
        asyncio.run(init_db())
    except RuntimeError:
        # If we're already in an async context, use ensure_future
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, schedule the task
            task = asyncio.create_task(init_db())
            return task
        else:
            # We can run normally
            asyncio.run(init_db())

# ASYNC Function to verify database setup
async def verify_db_setup():
    """Verify that all required schemas and types exist"""
    async with engine.begin() as conn:
        # Check schemas
        result = await conn.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('users', 'campaigns', 'analytics', 'payments', 'integrations')
        """))
        schemas = [row[0] for row in result]
        
        logger.info(f"Found schemas: {schemas}")
        
        # Check if users table exists and has role column
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'users' 
            AND table_name = 'users'
            AND column_name = 'role'
        """))
        
        rows = result.fetchall()
        if not rows:
            logger.warning("Role column missing - will be created by migrations")
        else:
            logger.info("Role column exists")
        
        # Check enum types and their values
        result = await conn.execute(text("""
            SELECT 
                t.typname,
                array_agg(e.enumlabel ORDER BY e.enumsortorder) as enum_values
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typname IN ('user_role', 'gender_type')
            AND n.nspname = 'users'
            GROUP BY t.typname
        """))
        
        for row in result:
            logger.info(f"Enum {row[0]} has values: {row[1]}")
        
        logger.info("Database setup verified successfully")

# Add connection check function
async def check_db_connection():
    """Check if database connection is working"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# DANGER ZONE - Development functions (keeping your existing ones)
async def recreate_tables():
    """Drop and recreate all tables - USE WITH CAUTION!"""
    response = input("⚠️  WARNING: This will DELETE all data. Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        logger.info("Operation cancelled")
        return
    
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("All tables dropped")
        
        # Recreate all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created")

async def fix_enum_types():
    """Fix enum types if they have wrong values - DO NOT USE IN PRODUCTION"""
    logger.warning("This function should not be used in production as it drops tables!")
    response = input("⚠️  WARNING: This may DELETE data. Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        logger.info("Operation cancelled")
        return
    
    async with engine.begin() as conn:
        try:
            # Check current enum values
            result = await conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum e 
                JOIN pg_type t ON e.enumtypid = t.oid 
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE t.typname = 'user_role' AND n.nspname = 'users'
            """))
            
            values = [row[0] for row in result]
            logger.info(f"Current user_role values: {values}")
            
            # If values are uppercase, we need to recreate the type
            if any(v.isupper() for v in values):
                logger.info("Found uppercase values, recreating enum types...")
                
                # First, drop the tables that use these types
                await conn.execute(text("DROP TABLE IF EXISTS users.creator_badges CASCADE"))
                await conn.execute(text("DROP TABLE IF EXISTS users.creator_audience_demographics CASCADE"))
                await conn.execute(text("DROP TABLE IF EXISTS users.user_tokens CASCADE"))
                await conn.execute(text("DROP TABLE IF EXISTS users.users CASCADE"))
                
                # Now drop and recreate the types
                await conn.execute(text("DROP TYPE IF EXISTS users.user_role CASCADE"))
                await conn.execute(text("DROP TYPE IF EXISTS users.gender_type CASCADE"))
                
                # Recreate with lowercase values
                await conn.execute(text("CREATE TYPE users.user_role AS ENUM ('agency', 'creator', 'brand', 'admin')"))
                await conn.execute(text("CREATE TYPE users.gender_type AS ENUM ('male', 'female', 'non_binary', 'prefer_not_to_say')"))
                
                logger.info("Enum types recreated with lowercase values")
                
                # Now recreate the tables
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Tables recreated")
                
        except Exception as e:
            logger.error(f"Error fixing enum types: {str(e)}")
            raise

# Backward compatibility aliases
get_db_legacy = get_db_sync  # Alias for your existing code