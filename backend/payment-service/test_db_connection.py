#!/usr/bin/env python3
"""
Test database connection and provide setup instructions
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def test_connection():
    """Test database connection"""
    
    # Try different connection strings
    connection_strings = [
        "postgresql://postgres:admin@localhost:5432/crm_campaigns_db",
        "postgresql://postgres:admin@localhost:5432/launchpaid_db",
        "postgresql://postgres:admin@localhost:5432/launchpaid_dev"
    ]
    
    for conn_str in connection_strings:
        try:
            print(f"🔍 Testing connection: {conn_str}")
            conn = psycopg2.connect(conn_str)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Test basic query
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"✅ Connection successful!")
            print(f"   Database version: {version['version']}")
            
            # Check if payments schema exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = 'payments'
                )
            """)
            schema_exists = cursor.fetchone()['exists']
            print(f"   Payments schema exists: {schema_exists}")
            
            # Check if tables exist
            if schema_exists:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'payments'
                """)
                tables = [row['table_name'] for row in cursor.fetchall()]
                print(f"   Existing tables: {tables}")
            
            cursor.close()
            conn.close()
            return conn_str
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            continue
    
    return None

def main():
    print("🔍 Testing database connections...")
    
    working_connection = test_connection()
    
    if working_connection:
        print(f"\n✅ Found working connection: {working_connection}")
        print("\n📋 Next steps:")
        print("1. Run the SQL script to create tables:")
        print("   psql -d launchpaid_dev -f create_tables.sql")
        print("   OR")
        print("   Copy and paste the contents of create_tables.sql into your database client")
        print("\n2. After creating tables, test the API endpoints again")
    else:
        print("\n❌ No working database connection found")
        print("\n📋 Please check:")
        print("1. Is PostgreSQL running?")
        print("2. Is the database 'launchpaid_dev' created?")
        print("3. Are the credentials correct?")
        print("\nCommon solutions:")
        print("- Start PostgreSQL: sudo service postgresql start")
        print("- Create database: createdb launchpaid_dev")
        print("- Check credentials in your .env file")

if __name__ == "__main__":
    main() 