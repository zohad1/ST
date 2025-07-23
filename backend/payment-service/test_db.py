#!/usr/bin/env python3
"""
Test database connectivity and table existence for payment service
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'database': 'crm_campaigns_db',
    'user': 'postgres',
    'password': 'admin',
    'port': 5432
}

def test_database_connection():
    """Test if we can connect to the database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful!")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def check_tables_exist(conn):
    """Check if the required tables exist"""
    cursor = conn.cursor()
    
    tables_to_check = [
        'creator_earnings',
        'payments', 
        'payment_schedules',
        'referrals'
    ]
    
    print("\n📋 Checking table existence:")
    for table in tables_to_check:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (table,))
        
        exists = cursor.fetchone()[0]
        status = "✅" if exists else "❌"
        print(f"{status} {table}")
    
    cursor.close()

def check_sample_data(conn):
    """Check if there's sample data in the tables"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("\n📊 Checking sample data:")
    
    # Check creator_earnings
    cursor.execute("SELECT COUNT(*) as count FROM creator_earnings")
    earnings_count = cursor.fetchone()['count']
    print(f"📈 creator_earnings: {earnings_count} records")
    
    # Check payments
    cursor.execute("SELECT COUNT(*) as count FROM payments")
    payments_count = cursor.fetchone()['count']
    print(f"💰 payments: {payments_count} records")
    
    # Check specific user data
    user_id = '4923df90-0ecb-40e4-8114-0b2a97a280a3'
    cursor.execute("""
        SELECT 
            COUNT(*) as earnings_count,
            SUM(base_earnings + gmv_commission + bonus_earnings + referral_earnings) as total_earnings,
            SUM(total_paid) as total_paid
        FROM creator_earnings 
        WHERE creator_id = %s
    """, (user_id,))
    
    user_data = cursor.fetchone()
    if user_data['earnings_count'] > 0:
        print(f"👤 User {user_id}:")
        print(f"   - Earnings records: {user_data['earnings_count']}")
        print(f"   - Total earnings: ${user_data['total_earnings'] or 0}")
        print(f"   - Total paid: ${user_data['total_paid'] or 0}")
        print(f"   - Pending: ${(user_data['total_earnings'] or 0) - (user_data['total_paid'] or 0)}")
    else:
        print(f"❌ No data found for user {user_id}")
    
    cursor.close()

def test_api_endpoint():
    """Test the API endpoint directly"""
    import requests
    import json
    
    # Create a test token
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0OTIzZGY5MC0wZWNiLTQwZTQtODExNC0wYjJhOTdhMjgwYTMiLCJyb2xlIjoiY3JlYXRvciIsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjE3MzE3Njk3MjMsImV4cCI6MTczMTc3MTUyM30.example"
    
    url = "http://localhost:8004/api/v1/earnings/creator/4923df90-0ecb-40e4-8114-0b2a97a280a3/summary"
    headers = {"Authorization": f"Bearer {test_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n🌐 API Test:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API endpoint working!")
        else:
            print("❌ API endpoint failed!")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Payment Service Database...")
    
    # Test database connection
    conn = test_database_connection()
    
    if conn:
        # Check if tables exist
        check_tables_exist(conn)
        
        # Check sample data
        check_sample_data(conn)
        
        # Close connection
        conn.close()
        
        # Test API endpoint
        test_api_endpoint()
    else:
        print("❌ Cannot proceed without database connection") 