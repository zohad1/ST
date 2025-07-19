# check_imports.py - Run this to diagnose import issues
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python Path:")
for path in sys.path[:3]:
    print(f"  - {path}")
print()

def test_import(module_path, item_name=None):
    try:
        if item_name:
            exec(f"from {module_path} import {item_name}")
            print(f"✓ from {module_path} import {item_name}")
        else:
            exec(f"import {module_path}")
            print(f"✓ import {module_path}")
    except Exception as e:
        print(f"✗ {module_path}{f'.{item_name}' if item_name else ''}: {type(e).__name__}: {str(e)}")

print("Testing Core Imports:")
test_import("app.core.config", "settings")
test_import("app.core.dependencies", "get_current_shop")

print("\nTesting Model Imports:")
test_import("app.models.database", "Base")
test_import("app.models.database", "get_db")
test_import("app.models.schemas", "TokenResponse")
test_import("app.models.tiktok_models", "TikTokShop")
test_import("app.models.tiktok_models", "TikTokOrder")
test_import("app.models.tiktok_models", "TikTokProduct")
test_import("app.models.tiktok_models", "SyncOperation")
test_import("app.models.tiktok_models", "WebhookEvent")

print("\nTesting Service Imports:")
test_import("app.services.auth_service", "AuthService")
test_import("app.services.order_service", "OrderService")
test_import("app.services.product_service", "ProductService")
test_import("app.services.webhook_service", "WebhookService")
test_import("app.services.tiktok_client", "TikTokShopClient")

print("\nTesting API Endpoint Imports:")
test_import("app.api.v1.endpoints.auth", "router")
test_import("app.api.v1.endpoints.products", "router")
test_import("app.api.v1.endpoints.orders", "router")
test_import("app.api.v1.endpoints.shops", "router")
test_import("app.api.v1.endpoints.webhooks", "router")

print("\nTesting Main API Router:")
test_import("app.api.v1.api", "api_router")

print("\nChecking file existence:")
files_to_check = [
    "app/__init__.py",
    "app/core/__init__.py",
    "app/models/__init__.py",
    "app/services/__init__.py",
    "app/api/__init__.py",
    "app/api/v1/__init__.py",
    "app/api/v1/endpoints/__init__.py",
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✓ {file_path} exists")
    else:
        print(f"✗ {file_path} MISSING!")

print("\nDone!")