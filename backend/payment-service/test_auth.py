#!/usr/bin/env python3
"""
Test authentication with proper JWT token
"""

import requests
import jwt
from datetime import datetime, timedelta

# Use the same secret key as the payment service
JWT_SECRET_KEY = "jwt-secret-key-for-development-change-in-production-minimum-32-chars"
ALGORITHM = "HS256"

CREATOR_EMAIL = "asamad.ls.asj@gmail.com"
CREATOR_PASSWORD = "@12Asamad"
AGENCY_EMAIL = "abdulsamadjunejo0@gmail.com"
AGENCY_PASSWORD = "@12Asamad"

USER_SERVICE_URL = "http://localhost:8000/api/v1/auth/login"


def login_and_get_token(email, password):
    """Log in to the user service and return the JWT token and user id"""
    data = {"email": email, "password": password}
    try:
        response = requests.post(USER_SERVICE_URL, json=data)
        print(f"🔐 Login response status: {response.status_code}")
        if response.status_code == 200:
            resp_json = response.json()
            token = resp_json["data"]["access_token"]
            user_id = resp_json["data"]["user"]["id"]
            print(f"✅ Got token for {email}: {token[:50]}...")
            print(f"   User ID: {user_id}")
            return token, user_id
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return None, None


def create_valid_token(user_id: str = "4923df90-0ecb-40e4-8114-0b2a97a280a3", role: str = "creator"):
    """Create a valid JWT token"""
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token

def test_earnings_endpoint():
    """Test the earnings endpoint with valid token"""
    
    # Create a valid token
    valid_token = create_valid_token()
    print(f"🔑 Created valid token: {valid_token[:50]}...")
    
    # Test the earnings endpoint
    url = "http://localhost:8004/api/v1/earnings/creator/4923df90-0ecb-40e4-8114-0b2a97a280a3/summary"
    headers = {"Authorization": f"Bearer {valid_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n📡 Earnings endpoint test:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Earnings endpoint working!")
        else:
            print("❌ Earnings endpoint failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_payments_endpoint():
    """Test the payments endpoint with valid token"""
    
    # Create a valid token
    valid_token = create_valid_token()
    
    # Test the payments endpoint
    url = "http://localhost:8004/api/v1/payments/history"
    headers = {"Authorization": f"Bearer {valid_token}"}
    params = {
        "creator_id": "4923df90-0ecb-40e4-8114-0b2a97a280a3",
        "page": "1",
        "limit": "20"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"\n📡 Payments endpoint test:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Payments endpoint working!")
        else:
            print("❌ Payments endpoint failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_auth_endpoint():
    """Test the auth test endpoint"""
    
    # Create a valid token
    valid_token = create_valid_token()
    
    # Test the auth test endpoint
    url = "http://localhost:8004/api/v1/test-auth"
    headers = {"Authorization": f"Bearer {valid_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n📡 Auth test endpoint:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Auth test endpoint working!")
        else:
            print("❌ Auth test endpoint failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_with_real_user():
    print("\n=== Testing with real creator user ===")
    token, user_id = login_and_get_token(CREATOR_EMAIL, CREATOR_PASSWORD)
    if not token:
        print("❌ Could not get token for creator user.")
        return
    # Test endpoints with this token
    headers = {"Authorization": f"Bearer {token}"}
    # Earnings summary
    url = f"http://localhost:8004/api/v1/earnings/creator/{user_id}/summary"
    response = requests.get(url, headers=headers)
    print(f"Earnings summary status: {response.status_code}")
    print(f"Earnings summary: {response.text}")
    # Payments history
    url = f"http://localhost:8004/api/v1/payments/history?creator_id={user_id}&page=1&limit=20"
    response = requests.get(url, headers=headers)
    print(f"Payments history status: {response.status_code}")
    print(f"Payments history: {response.text}")

if __name__ == "__main__":
    print("🧪 Testing Payment Service Authentication...")
    test_with_real_user() 