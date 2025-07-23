#!/usr/bin/env python3
"""
Debug script to test payment service endpoints and see detailed error messages
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8004"
USER_SERVICE_URL = "http://localhost:8000"

def login_user():
    """Login and get token"""
    login_data = {
        "email": "asamad.ls.asj@gmail.com",
        "password": "@12Asamad"
    }
    
    try:
        response = requests.post(f"{USER_SERVICE_URL}/api/v1/auth/login", json=login_data)
        print(f"🔐 Login status: {response.status_code}")
        print(f"Raw response: {response.text}")
        try:
            data = response.json()
            print(f"Parsed JSON: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"❌ Could not parse JSON: {e}")
            return None
        
        if response.status_code == 200:
            # Try to extract token from possible structures
            token = data.get("access_token")
            if not token and "data" in data:
                token = data["data"].get("access_token")
            print(f"✅ Got token: {token[:50]}..." if token else "❌ No token found in response")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_earnings_summary(token, creator_id):
    """Test earnings summary endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/v1/earnings/creator/{creator_id}/summary"
    
    try:
        print(f"\n📊 Testing earnings summary: {url}")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error - check server logs")
        
    except Exception as e:
        print(f"❌ Request error: {e}")

def test_payment_history(token):
    """Test payment history endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/v1/payments/history"
    
    try:
        print(f"\n💰 Testing payment history: {url}")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error - check server logs")
        
    except Exception as e:
        print(f"❌ Request error: {e}")

def test_payment_overview(token):
    """Test payment overview endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/v1/payments/overview"
    
    try:
        print(f"\n📈 Testing payment overview: {url}")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error - check server logs")
        
    except Exception as e:
        print(f"❌ Request error: {e}")

def main():
    print("🔍 Debugging Payment Service Endpoints...")
    
    # Login
    token = login_user()
    if not token:
        print("❌ Failed to get token")
        return
    
    creator_id = "4923df90-0ecb-40e4-8114-0b2a97a280a3"
    
    # Test endpoints
    test_earnings_summary(token, creator_id)
    test_payment_history(token)
    test_payment_overview(token)
    
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    main() 