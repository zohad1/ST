#!/usr/bin/env python3
"""
Debug script to test JWT token validation between user service and payment service
"""

import jwt
import requests
from datetime import datetime, timedelta

# Test JWT secret key (should match user service)
JWT_SECRET_KEY = "jwt-secret-key-for-development-change-in-production-minimum-32-chars"
ALGORITHM = "HS256"

def create_test_token(user_id: str = "test-user-123", role: str = "creator"):
    """Create a test JWT token similar to user service"""
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token

def test_token_validation():
    """Test if the payment service can validate tokens"""
    
    # Create a test token
    test_token = create_test_token()
    print(f"🔑 Created test token: {test_token[:50]}...")
    
    # Test the payment service endpoint
    url = "http://localhost:8004/api/v1/test-auth"
    headers = {"Authorization": f"Bearer {test_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_user_service_token():
    """Test with a real token from user service"""
    
    # First, try to get a token from user service
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"🔐 Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data", {}).get("access_token"):
                token = data["data"]["access_token"]
                print(f"🔑 Got real token: {token[:50]}...")
                
                # Test with payment service
                payment_url = "http://localhost:8004/api/v1/test-auth"
                headers = {"Authorization": f"Bearer {token}"}
                
                payment_response = requests.get(payment_url, headers=headers)
                print(f"💳 Payment service response: {payment_response.status_code}")
                print(f"📄 Payment service body: {payment_response.text}")
                
            else:
                print("❌ No access token in login response")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing JWT authentication...")
    print("\n1. Testing with test token:")
    test_token_validation()
    
    print("\n2. Testing with real user service token:")
    test_user_service_token() 