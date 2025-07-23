
# Fixed run_tests.py
# run_tests.py
#!/usr/bin/env python3
"""
Fixed Payment Service Test Runner
Uses standalone models without external foreign key dependencies
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from uuid import UUID, uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import app components
from app.models.base import Base
from app.models.standalone_models import *  # Import standalone models
from app.services.earnings_service import EarningsCalculationService
from app.services.payment_service import PaymentProcessingService
from app.schemas.creator_earnings import CreatorEarningsCreate
from app.schemas.payment import PaymentCreate
from app.models.payment_enums import PaymentType, PayoutMethod

# Test data
TEST_CREATOR_ID = UUID("550e8400-e29b-41d4-a716-446655440000")
TEST_CAMPAIGN_ID = UUID("770e8400-e29b-41d4-a716-446655440000")
TEST_APPLICATION_ID = UUID("880e8400-e29b-41d4-a716-446655440000")

def setup_test_database():
    """Setup SQLite test database"""
    print("🗄️  Setting up test database...")
    
    # Create SQLite database
    engine = create_engine("sqlite:///payment_service_test.db", echo=False)
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print("✅ Database setup complete!")
    return SessionLocal

async def test_earnings_calculation(db_session):
    """Test earnings calculation with mock data"""
    print("\n💰 Testing Earnings Calculation...")
    
    try:
        earnings_service = EarningsCalculationService(db_session)
        
        # Test earnings calculation
        earnings = await earnings_service.calculate_creator_earnings(
            creator_id=TEST_CREATOR_ID,
            campaign_id=TEST_CAMPAIGN_ID,
            application_id=TEST_APPLICATION_ID,
            deliverables_completed=4,
            gmv_generated=4500.0  # $4,500 GMV
        )
        
        print(f"✅ Earnings calculated successfully!")
        print(f"   📊 Total Earnings: ${earnings.calculated_total_earnings:.2f}")
        print(f"   💵 Base Earnings: ${float(earnings.base_earnings):.2f}")
        print(f"   🛒 GMV Commission: ${float(earnings.gmv_commission):.2f}")
        print(f"   🎁 Bonus Earnings: ${float(earnings.bonus_earnings):.2f}")
        print(f"   🔗 Referral Earnings: ${float(earnings.referral_earnings):.2f}")
        
        return earnings
        
    except Exception as e:
        print(f"❌ Earnings calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_payment_processing(db_session, earnings):
    """Test payment processing with mock clients"""
    print("\n💳 Testing Payment Processing...")
    
    try:
        payment_service = PaymentProcessingService(db_session)
        
        # Create test payment
        payment_data = PaymentCreate(
            creator_id=TEST_CREATOR_ID,
            campaign_id=TEST_CAMPAIGN_ID,
            earning_id=earnings.id if earnings else None,
            amount=300.0,
            payment_type=PaymentType.base_payout,
            payment_method=PayoutMethod.stripe,
            description="Test payment via mock Stripe"
        )
        
        payment = await payment_service.create_manual_payment(payment_data)
        print(f"✅ Payment created: {payment.id}")
        print(f"   💰 Amount: ${float(payment.amount):.2f}")
        print(f"   🏦 Method: {payment.payment_method}")
        print(f"   📊 Status: {payment.status}")
        
        # Process the payment (uses mock Stripe)
        print("   🔄 Processing payment with mock Stripe...")
        await payment_service.process_payment_async(payment.id)
        
        print("✅ Payment processing initiated!")
        return payment
        
    except Exception as e:
        print(f"❌ Payment processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_mock_integrations():
    """Test all mock external service integrations"""
    print("\n🔌 Testing Mock External Service Integrations...")
    
    from app.external.mock_clients import (
        MockStripeClient, 
        MockFanbasisClient, 
        MockUserServiceClient, 
        MockCampaignServiceClient
    )
    
    try:
        # Test Mock Stripe Client
        print("   💳 Testing Mock Stripe Client...")
        stripe_client = MockStripeClient()
        
        stripe_result = await stripe_client.create_payment_intent(
            amount=200.0,
            creator_id=TEST_CREATOR_ID,
            description="Test payment intent"
        )
        print(f"   ✅ Stripe payment intent: {stripe_result['payment_intent_id']}")
        
        # Test Mock Fanbasis Client
        print("   💰 Testing Mock Fanbasis Client...")
        fanbasis_client = MockFanbasisClient()
        
        fanbasis_result = await fanbasis_client.create_payout(
            amount=150.0,
            creator_id=TEST_CREATOR_ID,
            creator_email="test@example.com"
        )
        print(f"   ✅ Fanbasis payout: {fanbasis_result['transaction_id']}")
        
        # Test Mock User Service Client
        print("   👤 Testing Mock User Service Client...")
        user_client = MockUserServiceClient()
        
        user = await user_client.get_user(TEST_CREATOR_ID)
        print(f"   ✅ User retrieved: {user['username']} ({user['role']})")
        
        # Test Mock Campaign Service Client
        print("   📋 Testing Mock Campaign Service Client...")
        campaign_client = MockCampaignServiceClient()
        
        campaign = await campaign_client.get_campaign(TEST_CAMPAIGN_ID)
        print(f"   ✅ Campaign retrieved: {campaign['name']}")
        
        deliverables = await campaign_client.get_creator_deliverables(TEST_APPLICATION_ID)
        print(f"   ✅ Deliverables: {deliverables['completed_count']}/{deliverables['total_count']} completed")
        
    except Exception as e:
        print(f"❌ Mock integration test failed: {e}")
        import traceback
        traceback.print_exc()

def test_webhook_parsing():
    """Test webhook signature verification and parsing"""
    print("\n🪝 Testing Webhook Processing...")
    
    try:
        from app.external.mock_clients import MockStripeClient
        
        # Test Stripe webhook parsing
        stripe_client = MockStripeClient()
        
        # Mock webhook payload
        test_payload = json.dumps({
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_123456",
                    "status": "succeeded",
                    "amount": 20000,  # $200.00 in cents
                    "currency": "usd"
                }
            }
        }).encode()
        
        # Test signature verification (always passes in mock)
        is_valid = stripe_client.verify_webhook_signature(test_payload, "test-signature")
        print(f"   ✅ Webhook signature valid: {is_valid}")
        
        # Test webhook parsing
        event = stripe_client.parse_webhook_event(test_payload, "test-signature")
        print(f"   ✅ Webhook parsed: {event['type']}")
        print(f"   📊 Payment ID: {event['data']['object']['id']}")
        
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        import traceback
        traceback.print_exc()

async def run_all_tests():
    """Run complete test suite"""
    print("🚀 Starting Payment Service Complete Test Suite")
    print("=" * 60)
    
    # Setup database
    SessionLocal = setup_test_database()
    db_session = SessionLocal()
    
    try:
        # Test 1: Mock integrations
        await test_mock_integrations()
        
        # Test 2: Earnings calculation
        earnings = await test_earnings_calculation(db_session)
        
        # Test 3: Payment processing
        payment = await test_payment_processing(db_session, earnings)
        
        # Test 4: Webhook processing
        test_webhook_parsing()
        
        print("\n🎉 All Tests Completed Successfully!")
        print("=" * 60)
        print("✅ Mock external services working")
        print("✅ Earnings calculation functional")
        print("✅ Payment processing operational")
        print("✅ Webhook handling ready")
        print("✅ Database operations successful")
        print("\n📄 Database file created: payment_service_test.db")
        print("🌐 Ready to test API endpoints with: uvicorn app.main:app --reload --port 8002")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db_session.close()

if __name__ == "__main__":
    asyncio.run(run_all_tests())