# quick_api_test.py - Simple API test without Unicode issues
#!/usr/bin/env python3
"""
Simple API Test Script for Payment Service
Tests the FastAPI endpoints once the service is running
"""
import requests
import json

BASE_URL = "http://localhost:8002"
TEST_CREATOR_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_CAMPAIGN_ID = "770e8400-e29b-41d4-a716-446655440000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_earnings_calculation():
    """Test earnings calculation endpoint"""
    payload = {
        "creator_id": TEST_CREATOR_ID,
        "campaign_id": TEST_CAMPAIGN_ID,
        "application_id": "880e8400-e29b-41d4-a716-446655440000",
        "deliverables_completed": 3,
        "gmv_generated": 2500.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/earnings/calculate",
            json=payload,
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"Earnings Calculation: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   Total Earnings: ${data.get('total_earnings', 0):.2f}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Earnings test failed: {e}")
        return False

def test_payment_creation():
    """Test payment creation endpoint"""
    payload = {
        "creator_id": TEST_CREATOR_ID,
        "amount": 150.0,
        "payment_type": "base_payout",
        "payment_method": "stripe",
        "description": "API test payment"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/payments/",
            json=payload,
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"Payment Creation: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   Payment ID: {data.get('id', 'Unknown')}")
            print(f"   Amount: ${data.get('amount', 0):.2f}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Payment test failed: {e}")
        return False

def run_api_tests():
    """Run all API tests"""
    print("Testing Payment Service API Endpoints")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Earnings Calculation", test_earnings_calculation), 
        ("Payment Creation", test_payment_creation)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        results.append(test_func())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("All API tests passed!")
    else:
        print("Some tests failed - check if service is running")
        print("Start service with: uvicorn app.main:app --reload --port 8002")

if __name__ == "__main__":
    run_api_tests()

