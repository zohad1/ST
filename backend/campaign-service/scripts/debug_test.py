# scripts/debug_test.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import traceback
from sqlalchemy import text, inspect
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test basic database connection"""
    logger.info("=" * 80)
    logger.info("🔍 TESTING DATABASE CONNECTION")
    logger.info("=" * 80)
    
    try:
        from app.core.config import settings
        logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[0]}@****")
        
        from app.core.database import engine, SessionLocal
        logger.info("✅ Database engine created")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Connected to: {version}")
            
            # Check current database and schema
            result = conn.execute(text("SELECT current_database(), current_schema()"))
            db_info = result.fetchone()
            logger.info(f"📍 Database: {db_info[0]}, Schema: {db_info[1]}")
            
    except Exception as e:
        logger.error(f"❌ Connection error: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    
    return True

def test_tables_exist():
    """Check if required tables exist"""
    logger.info("\n" + "=" * 80)
    logger.info("🔍 CHECKING TABLES")
    logger.info("=" * 80)
    
    try:
        from app.core.database import engine
        
        with engine.connect() as conn:
            # Check schemas
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ('campaigns', 'users')
                ORDER BY schema_name
            """))
            schemas = [row[0] for row in result]
            logger.info(f"Found schemas: {schemas}")
            
            # Check tables
            result = conn.execute(text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema IN ('campaigns', 'users')
                ORDER BY table_schema, table_name
            """))
            
            tables = {}
            for row in result:
                schema = row[0]
                table = row[1]
                if schema not in tables:
                    tables[schema] = []
                tables[schema].append(table)
            
            for schema, table_list in tables.items():
                logger.info(f"\n📁 Schema: {schema}")
                for table in table_list:
                    logger.info(f"   📄 {table}")
            
            # Check specific required tables
            required_tables = [
                ('campaigns', 'campaigns'),
                ('campaigns', 'creator_applications'),
                ('campaigns', 'deliverables'),
                ('users', 'users')
            ]
            
            missing_tables = []
            for schema, table in required_tables:
                full_name = f"{schema}.{table}"
                if schema in tables and table in tables[schema]:
                    logger.info(f"✅ Table exists: {full_name}")
                else:
                    logger.error(f"❌ Table missing: {full_name}")
                    missing_tables.append(full_name)
            
            return len(missing_tables) == 0
            
    except Exception as e:
        logger.error(f"❌ Error checking tables: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_campaign_columns():
    """Check campaign table columns"""
    logger.info("\n" + "=" * 80)
    logger.info("🔍 CHECKING CAMPAIGN TABLE COLUMNS")
    logger.info("=" * 80)
    
    try:
        from app.core.database import engine
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'campaigns' AND table_name = 'campaigns'
                ORDER BY ordinal_position
            """))
            
            columns = {}
            for row in result:
                columns[row[0]] = {
                    'type': row[1],
                    'nullable': row[2],
                    'default': row[3]
                }
            
            logger.info(f"Found {len(columns)} columns:")
            for col_name, col_info in columns.items():
                logger.info(f"   • {col_name}: {col_info['type']} (nullable: {col_info['nullable']})")
            
            # Check required columns
            required_columns = [
                'id', 'name', 'status', 'type', 'budget', 'total_budget',
                'current_gmv', 'current_posts', 'current_creators',
                'target_gmv', 'target_posts', 'target_creators',
                'total_views', 'total_engagement'
            ]
            
            missing_columns = []
            for col in required_columns:
                if col in columns:
                    logger.info(f"✅ Column exists: {col}")
                else:
                    logger.error(f"❌ Column missing: {col}")
                    missing_columns.append(col)
            
            return len(missing_columns) == 0
            
    except Exception as e:
        logger.error(f"❌ Error checking columns: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_model_imports():
    """Test importing models"""
    logger.info("\n" + "=" * 80)
    logger.info("🔍 TESTING MODEL IMPORTS")
    logger.info("=" * 80)
    
    try:
        logger.info("Importing Campaign models...")
        from app.models.campaign import (
            Campaign, CampaignApplication, Deliverable,
            CampaignStatus, PayoutModel, TrackingMethod
        )
        logger.info("✅ Campaign models imported")
        
        logger.info("Importing User model...")
        from app.models.user import User
        logger.info("✅ User model imported")
        
        # Check model attributes
        logger.info("\nChecking Campaign model attributes:")
        campaign_attrs = [attr for attr in dir(Campaign) if not attr.startswith('_')]
        important_attrs = ['id', 'name', 'status', 'type', 'budget', 'current_gmv']
        for attr in important_attrs:
            if attr in campaign_attrs:
                logger.info(f"✅ Campaign.{attr} exists")
            else:
                logger.error(f"❌ Campaign.{attr} missing")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_simple_query():
    """Test a simple query"""
    logger.info("\n" + "=" * 80)
    logger.info("🔍 TESTING SIMPLE QUERY")
    logger.info("=" * 80)
    
    try:
        from app.core.database import SessionLocal
        from app.models.campaign import Campaign
        
        db = SessionLocal()
        logger.info("✅ Created database session")
        
        # Count campaigns
        count = db.query(Campaign).count()
        logger.info(f"📊 Total campaigns: {count}")
        
        # Get first campaign
        if count > 0:
            campaign = db.query(Campaign).first()
            logger.info(f"\n📋 First campaign:")
            logger.info(f"   ID: {campaign.id}")
            logger.info(f"   Name: {campaign.name}")
            logger.info(f"   Status: {campaign.status}")
            logger.info(f"   Type: {getattr(campaign, 'type', 'N/A')}")
            logger.info(f"   Budget: {getattr(campaign, 'budget', 'N/A')}")
            logger.info(f"   Current GMV: {getattr(campaign, 'current_gmv', 'N/A')}")
        
        # Test querying with filters
        active_campaigns = db.query(Campaign).filter(Campaign.status == "active").count()
        logger.info(f"\n📊 Active campaigns: {active_campaigns}")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Query error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_dashboard_query():
    """Test dashboard-specific queries"""
    logger.info("\n" + "=" * 80)
    logger.info("🔍 TESTING DASHBOARD QUERIES")
    logger.info("=" * 80)
    
    try:
        from app.core.database import SessionLocal
        from app.models.campaign import Campaign, CampaignApplication
        from app.models.user import User
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        
        # Test date range query
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        logger.info(f"📅 Date range: {start_date.date()} to {end_date.date()}")
        
        # Query campaigns in date range
        campaigns = db.query(Campaign).filter(
            Campaign.created_at >= start_date,
            Campaign.created_at <= end_date
        ).all()
        
        logger.info(f"📊 Campaigns in last 30 days: {len(campaigns)}")
        
        # Calculate metrics
        total_gmv = sum(float(c.current_gmv or 0) for c in campaigns)
        total_views = sum(c.total_views or 0 for c in campaigns)
        active_count = len([c for c in campaigns if c.status == "active"])
        
        logger.info(f"\n📈 Metrics:")
        logger.info(f"   Total GMV: ${total_gmv:,.2f}")
        logger.info(f"   Total Views: {total_views:,}")
        logger.info(f"   Active Campaigns: {active_count}")
        
        # Test join query
        logger.info("\n🔗 Testing join queries...")
        applications = db.query(CampaignApplication).join(User).filter(
            CampaignApplication.status == "approved"
        ).limit(5).all()
        
        logger.info(f"📋 Found {len(applications)} approved applications")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard query error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Campaign Service Debug Tests")
    logger.info(f"⏰ Time: {datetime.now()}")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Tables Exist", test_tables_exist),
        ("Campaign Columns", test_campaign_columns),
        ("Model Imports", test_model_imports),
        ("Simple Query", test_simple_query),
        ("Dashboard Query", test_dashboard_query)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
    else:
        logger.error("⚠️  Some tests failed. Check logs above for details.")

if __name__ == "__main__":
    main()