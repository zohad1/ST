#!/usr/bin/env python3
"""
Run the SQL fix script to update enum types and insert sample data
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def run_sql_fix():
    """Run the SQL fix script"""
    
    # Database connection
    DATABASE_URL = "postgresql://postgres:admin@localhost:5432/crm_campaigns_db"
    
    try:
        # Read the SQL file
        with open('fix_enums_and_data.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("🔧 Running SQL fix script...")
        
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Execute the SQL script
        cursor.execute(sql_script)
        conn.commit()
        
        print("✅ SQL fix completed successfully!")
        
        # Verify the data was inserted
        cursor.execute("""
            SELECT 
                COUNT(*) as earnings_count,
                (SELECT COUNT(*) FROM payments.payments WHERE creator_id = '4923df90-0ecb-40e4-8114-0b2a97a280a3') as payments_count
            FROM payments.creator_earnings 
            WHERE creator_id = '4923df90-0ecb-40e4-8114-0b2a97a280a3'
        """)
        
        result = cursor.fetchone()
        print(f"📊 Verification:")
        print(f"   Earnings records: {result[0]}")
        print(f"   Payment records: {result[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database is now ready for testing!")
        
    except Exception as e:
        print(f"❌ Error running SQL fix: {e}")
        raise

if __name__ == "__main__":
    run_sql_fix() 