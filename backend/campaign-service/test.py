# Save this as test_imports.py in your campaign-service directory and run it

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

print("Testing imports...\n")

# Test 1: Import Campaign models
try:
    from app.models.campaign import Campaign, CampaignApplication
    print("✅ Campaign models imported successfully")
except Exception as e:
    print(f"❌ Failed to import campaign models: {e}")

# Test 2: Import Campaign schemas
try:
    from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignListResponse
    print("✅ Campaign schemas imported successfully")
    print(f"   - CampaignListResponse is defined: {CampaignListResponse is not None}")
except Exception as e:
    print(f"❌ Failed to import campaign schemas: {e}")

# Test 3: Import Campaign service
try:
    from app.services.campaign_service import CampaignService
    print("✅ Campaign service imported successfully")
except Exception as e:
    print(f"❌ Failed to import campaign service: {e}")

# Test 4: Import Campaign endpoints
try:
    from app.api.endpoints import campaigns
    print("✅ Campaign endpoints imported successfully")
    print(f"   - Router exists: {hasattr(campaigns, 'router')}")
    if hasattr(campaigns, 'router'):
        print(f"   - Number of routes: {len(campaigns.router.routes)}")
        for route in campaigns.router.routes:
            if hasattr(route, 'path'):
                print(f"     - {route.path}")
except Exception as e:
    print(f"❌ Failed to import campaign endpoints: {e}")
    import traceback
    traceback.print_exc()

print("\nDiagnostic complete!")