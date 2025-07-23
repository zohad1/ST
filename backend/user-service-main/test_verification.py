#!/usr/bin/env python3
"""
Test script to verify email verification flow
"""

import asyncio
import requests
import json
from datetime import datetime, timezone

# Test configuration
BASE_URL = "http://localhost:8000/api/v1/auth"

def test_signup():
    """Test user signup"""
    print("🔍 Testing user signup...")
    
    signup_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "role": "creator",
        "firstName": "Test",
        "lastName": "User"
    }
    
    response = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"Signup response status: {response.status_code}")
    print(f"Signup response: {response.json()}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Signup failed")
        return None

def test_verification_token(token):
    """Test verification token debug endpoint"""
    print(f"🔍 Testing verification token: {token[:8]}...")
    
    response = requests.get(f"{BASE_URL}/debug/verification/{token}")
    print(f"Debug response status: {response.status_code}")
    print(f"Debug response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_verify_email(token):
    """Test email verification"""
    print(f"🔍 Testing email verification with token: {token[:8]}...")
    
    verify_data = {
        "token": token
    }
    
    response = requests.post(f"{BASE_URL}/verify-email", json=verify_data)
    print(f"Verification response status: {response.status_code}")
    print(f"Verification response: {response.json()}")
    
    return response.json()

def test_login():
    """Test login after verification"""
    print("🔍 Testing login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.json()}")
    
    return response.json()

def main():
    """Run the complete verification test"""
    print("🚀 Starting email verification test...")
    print("=" * 50)
    
    # Step 1: Signup
    signup_result = test_signup()
    if not signup_result:
        print("❌ Test failed at signup step")
        return
    
    print("✅ Signup successful")
    print("=" * 50)
    
    # Step 2: Get verification token from database (you'll need to check the logs or database)
    print("⚠️  Please check the user service logs to get the verification token")
    print("   Or check the database for the latest verification token")
    print("   Then run: python test_verification.py <token>")
    
    # If token is provided as command line argument
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        
        # Step 3: Debug token
        debug_result = test_verification_token(token)
        print("=" * 50)
        
        # Step 4: Verify email
        verify_result = test_verify_email(token)
        print("=" * 50)
        
        # Step 5: Test login
        login_result = test_login()
        print("=" * 50)
        
        if login_result.get("success"):
            print("✅ Email verification test completed successfully!")
        else:
            print("❌ Email verification test failed!")
    else:
        print("💡 To test with a specific token, run:")
        print("   python test_verification.py <token>")

if __name__ == "__main__":
    main() 