# scripts/check_endpoints.py
import requests
import json

BASE_URL = "http://localhost:8002"

def check_endpoints():
    """Check which endpoints are available"""
    
    print("🔍 Checking available endpoints...")
    print("=" * 60)
    
    # Check root endpoint
    response = requests.get(BASE_URL + "/")
    if response.status_code == 200:
        data = response.json()
        print("✅ Root endpoint working")
        print("\nAvailable endpoints:")
        if "available_endpoints" in data:
            print(json.dumps(data["available_endpoints"], indent=2))
        else:
            print(json.dumps(data, indent=2))
    else:
        print(f"❌ Root endpoint failed: {response.status_code}")
    
    # Check API docs
    print("\n📚 Checking API documentation...")
    response = requests.get(BASE_URL + "/api/docs")
    if response.status_code == 200:
        print("✅ API docs available at: http://localhost:8002/api/docs")
    else:
        print("❌ API docs not available")
    
    # Check specific endpoints
    endpoints_to_check = [
        ("/api/v1/campaigns", "GET"),
        ("/api/v1/dashboard/analytics", "GET"),
        ("/api/v1/applications", "GET"),
        ("/api/v1/deliverables", "GET"),
    ]
    
    print("\n🧪 Checking specific endpoints:")
    for endpoint, method in endpoints_to_check:
        response = requests.request(method, BASE_URL + endpoint)
        status = "✅" if response.status_code < 500 else "❌"
        print(f"{status} {method} {endpoint} - Status: {response.status_code}")

if __name__ == "__main__":
    check_endpoints()