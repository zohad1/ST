# Step 1: Fix app/api/__init__.py
# Make this file COMPLETELY EMPTY - no imports at all

# Just create an empty file or put this comment only:
# This file intentionally left empty to avoid circular imports


# Step 2: Fix app/api/endpoints/__init__.py
# Replace the entire content with this:

from fastapi import APIRouter

# Create the main router
router = APIRouter()

# Import and include each router individually with error handling
def setup_routers():
    """Setup all routers with proper error handling"""
    
    # Import campaigns router
    try:
        from .campaigns import router as campaigns_router
        router.include_router(campaigns_router, prefix="/campaigns", tags=["Campaign Analytics"])
        print("✅ Campaigns router loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load campaigns router: {e}")
    
    # Import creators router
    try:
        from .creators import router as creators_router
        router.include_router(creators_router, prefix="/creators", tags=["Creator Analytics"])
        print("✅ Creators router loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load creators router: {e}")
    
    # Import dashboard router
    try:
        from .dashboard import router as dashboard_router
        router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
        print("✅ Dashboard router loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load dashboard router: {e}")
    
    # Import reports router
    try:
        from .reports import router as reports_router
        router.include_router(reports_router, prefix="/reports", tags=["Reports"])
        print("✅ Reports router loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load reports router: {e}")

# Setup routers when this module is imported
setup_routers()


