#!/usr/bin/env python3
"""
Script to insert sample creator earnings data for testing
"""

import asyncio
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/launchpaid_dev"

def insert_sample_earnings():
    """Insert sample earnings data for the test creator"""
    
    # Test creator ID (from your test user)
    CREATOR_ID = "4923df90-0ecb-40e4-8114-0b2a97a280a3"
    
    # Sample campaign and application IDs (you may need to adjust these)
    CAMPAIGN_ID = "550e8400-e29b-41d4-a716-446655440000"  # Sample campaign
    APPLICATION_ID = "660e8400-e29b-41d4-a716-446655440000"  # Sample application
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        try:
            # Check if earnings record already exists
            check_query = text("""
                SELECT COUNT(*) as count 
                FROM payments.creator_earnings 
                WHERE creator_id = :creator_id
            """)
            
            result = db.execute(check_query, {"creator_id": CREATOR_ID})
            count = result.fetchone()[0]
            
            if count > 0:
                print(f"✅ Creator earnings already exist for creator {CREATOR_ID}")
                return
            
            # Insert sample earnings data
            insert_query = text("""
                INSERT INTO payments.creator_earnings (
                    id, creator_id, campaign_id, application_id,
                    base_earnings, gmv_commission, bonus_earnings, referral_earnings,
                    total_paid, first_earned_at, last_updated
                ) VALUES (
                    :id, :creator_id, :campaign_id, :application_id,
                    :base_earnings, :gmv_commission, :bonus_earnings, :referral_earnings,
                    :total_paid, :first_earned_at, :last_updated
                )
            """)
            
            # Sample earnings data
            earnings_data = {
                "id": str(uuid.uuid4()),
                "creator_id": CREATOR_ID,
                "campaign_id": CAMPAIGN_ID,
                "application_id": APPLICATION_ID,
                "base_earnings": Decimal("500.00"),
                "gmv_commission": Decimal("250.00"),
                "bonus_earnings": Decimal("100.00"),
                "referral_earnings": Decimal("50.00"),
                "total_paid": Decimal("300.00"),
                "first_earned_at": datetime.now(timezone.utc),
                "last_updated": datetime.now(timezone.utc)
            }
            
            db.execute(insert_query, earnings_data)
            db.commit()
            
            print(f"✅ Successfully inserted sample earnings for creator {CREATOR_ID}")
            print(f"   📊 Base Earnings: ${earnings_data['base_earnings']}")
            print(f"   💰 GMV Commission: ${earnings_data['gmv_commission']}")
            print(f"   🎁 Bonus Earnings: ${earnings_data['bonus_earnings']}")
            print(f"   🔗 Referral Earnings: ${earnings_data['referral_earnings']}")
            print(f"   💵 Total Paid: ${earnings_data['total_paid']}")
            print(f"   ⏳ Pending Payment: ${earnings_data['base_earnings'] + earnings_data['gmv_commission'] + earnings_data['bonus_earnings'] + earnings_data['referral_earnings'] - earnings_data['total_paid']}")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error inserting sample earnings: {e}")
            raise
        finally:
            db.close()

if __name__ == "__main__":
    print("🔄 Inserting sample creator earnings data...")
    insert_sample_earnings()
    print("✅ Done!") 