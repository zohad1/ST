"""
Complete mock implementations for all external services
No real API keys or external services required
"""
import asyncio
import json
import random
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class MockStripeClient:
    """Complete Stripe mock - no real API calls"""
    
    def __init__(self):
        self.payments = {}
        self.transfers = {}
        logger.info("🔧 Initialized Mock Stripe Client")
    
    async def create_payment_intent(self, amount: float, creator_id: UUID, **kwargs) -> Dict[str, Any]:
        """Simulate Stripe payment intent creation"""
        intent_id = f"pi_mock_{secrets.token_hex(12)}"
        
        result = {
            "payment_intent_id": intent_id,
            "status": "requires_confirmation",
            "amount": amount,
            "currency": "usd",
            "client_secret": f"{intent_id}_secret_mock"
        }
        
        self.payments[intent_id] = {
            **result,
            "creator_id": str(creator_id),
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"💳 Mock Stripe: Created payment intent {intent_id} for ${amount}")
        
        # Simulate async confirmation (90% success rate)
        if random.random() < 0.9:
            asyncio.create_task(self._simulate_success(intent_id))
        else:
            asyncio.create_task(self._simulate_failure(intent_id))
        
        return result
    
    async def _simulate_success(self, intent_id: str):
        """Simulate successful payment confirmation"""
        await asyncio.sleep(random.uniform(1, 3))
        if intent_id in self.payments:
            self.payments[intent_id]["status"] = "succeeded"
            logger.info(f"✅ Mock Stripe: Payment {intent_id} succeeded")
    
    async def _simulate_failure(self, intent_id: str):
        """Simulate payment failure"""
        await asyncio.sleep(random.uniform(1, 2))
        if intent_id in self.payments:
            self.payments[intent_id]["status"] = "failed"
            self.payments[intent_id]["failure_reason"] = "Mock failure for testing"
            logger.info(f"❌ Mock Stripe: Payment {intent_id} failed")
    
    async def create_transfer(self, amount: float, destination_account: str, creator_id: UUID, **kwargs) -> Dict[str, Any]:
        """Simulate Stripe transfer creation"""
        transfer_id = f"tr_mock_{secrets.token_hex(12)}"
        
        result = {
            "transfer_id": transfer_id,
            "status": "pending",
            "amount": amount,
            "destination": destination_account
        }
        
        self.transfers[transfer_id] = result
        logger.info(f"💸 Mock Stripe: Created transfer {transfer_id} for ${amount}")
        
        # Simulate transfer completion
        asyncio.create_task(self._complete_transfer(transfer_id))
        return result
    
    async def _complete_transfer(self, transfer_id: str):
        """Simulate transfer completion"""
        await asyncio.sleep(random.uniform(2, 4))
        if transfer_id in self.transfers:
            self.transfers[transfer_id]["status"] = "paid"
            logger.info(f"✅ Mock Stripe: Transfer {transfer_id} completed")
    
    async def get_payment_status(self, payment_intent_id: str) -> Dict[str, Any]:
        """Get mock payment status"""
        if payment_intent_id in self.payments:
            payment = self.payments[payment_intent_id]
            return {
                "payment_intent_id": payment_intent_id,
                "status": payment["status"],
                "amount": payment["amount"],
                "currency": payment["currency"],
                "charges": [{
                    "charge_id": f"ch_mock_{secrets.token_hex(8)}",
                    "status": payment["status"],
                    "failure_code": payment.get("failure_code"),
                    "failure_message": payment.get("failure_reason")
                }] if payment["status"] in ["succeeded", "failed"] else []
            }
        
        # Default successful payment for unknown IDs
        return {
            "payment_intent_id": payment_intent_id,
            "status": "succeeded",
            "amount": 100.0,
            "currency": "usd",
            "charges": []
        }
    
    async def refund_payment(self, payment_intent_id: str, amount: float = None) -> Dict[str, Any]:
        """Simulate payment refund"""
        refund_id = f"re_mock_{secrets.token_hex(12)}"
        payment = self.payments.get(payment_intent_id, {})
        refund_amount = amount or payment.get("amount", 100.0)
        
        logger.info(f"🔄 Mock Stripe: Created refund {refund_id} for ${refund_amount}")
        
        return {
            "refund_id": refund_id,
            "status": "succeeded",
            "amount": refund_amount,
            "currency": "usd"
        }
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Mock webhook signature verification (always valid in testing)"""
        return True
    
    def parse_webhook_event(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """Parse mock webhook event"""
        try:
            data = json.loads(payload.decode())
            return {
                "id": f"evt_mock_{secrets.token_hex(8)}",
                "type": data.get("type", "payment_intent.succeeded"),
                "data": {
                    "object": data.get("data", {})
                },
                "created": int(datetime.now().timestamp()),
                "livemode": False
            }
        except:
            # Return default successful payment event
            return {
                "id": f"evt_mock_{secrets.token_hex(8)}",
                "type": "payment_intent.succeeded",
                "data": {
                    "object": {
                        "id": f"pi_mock_{secrets.token_hex(12)}",
                        "status": "succeeded",
                        "amount": 15000,  # $150.00 in cents
                        "currency": "usd"
                    }
                },
                "created": int(datetime.now().timestamp()),
                "livemode": False
            }

class MockFanbasisClient:
    """Complete Fanbasis mock"""
    
    def __init__(self):
        self.payouts = {}
        logger.info("🔧 Initialized Mock Fanbasis Client")
    
    async def create_payout(self, amount: float, creator_id: UUID, creator_email: str, **kwargs) -> Dict[str, Any]:
        """Simulate Fanbasis payout creation"""
        transaction_id = f"fb_mock_{secrets.token_hex(12)}"
        
        result = {
            "transaction_id": transaction_id,
            "status": "processing",
            "amount": amount,
            "currency": "USD",
            "estimated_delivery": (datetime.now() + timedelta(days=2)).isoformat()
        }
        
        self.payouts[transaction_id] = {
            **result,
            "creator_id": str(creator_id),
            "creator_email": creator_email
        }
        
        logger.info(f"💰 Mock Fanbasis: Created payout {transaction_id} for ${amount}")
        
        # Simulate processing completion (95% success rate)
        if random.random() < 0.95:
            asyncio.create_task(self._complete_payout(transaction_id))
        else:
            asyncio.create_task(self._fail_payout(transaction_id))
        
        return result
    
    async def _complete_payout(self, transaction_id: str):
        """Simulate payout completion"""
        await asyncio.sleep(random.uniform(2, 5))
        if transaction_id in self.payouts:
            self.payouts[transaction_id]["status"] = "completed"
            self.payouts[transaction_id]["completed_at"] = datetime.now().isoformat()
            logger.info(f"✅ Mock Fanbasis: Payout {transaction_id} completed")
    
    async def _fail_payout(self, transaction_id: str):
        """Simulate payout failure"""
        await asyncio.sleep(random.uniform(1, 3))
        if transaction_id in self.payouts:
            self.payouts[transaction_id]["status"] = "failed"
            self.payouts[transaction_id]["failure_reason"] = "Mock payout failure for testing"
            logger.info(f"❌ Mock Fanbasis: Payout {transaction_id} failed")
    
    async def get_payout_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get mock payout status"""
        if transaction_id in self.payouts:
            return self.payouts[transaction_id]
        
        # Default completed payout for unknown IDs
        return {
            "transaction_id": transaction_id,
            "status": "completed",
            "amount": 100.0,
            "currency": "USD",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()
        }
    
    async def cancel_payout(self, transaction_id: str) -> Dict[str, Any]:
        """Simulate payout cancellation"""
        if transaction_id in self.payouts:
            self.payouts[transaction_id]["status"] = "cancelled"
            self.payouts[transaction_id]["cancelled_at"] = datetime.now().isoformat()
        
        logger.info(f"❌ Mock Fanbasis: Cancelled payout {transaction_id}")
        
        return {
            "transaction_id": transaction_id,
            "status": "cancelled",
            "cancelled_at": datetime.now().isoformat()
        }
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Mock webhook signature verification"""
        return True

class MockUserServiceClient:
    """Complete User Service mock with realistic data"""
    
    def __init__(self):
        # Pre-defined test users
        self.users = {
            "550e8400-e29b-41d4-a716-446655440000": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john.creator@test.com",
                "username": "johncreator",
                "role": "creator",
                "first_name": "John",
                "last_name": "Doe",
                "tiktok_handle": "@johncreator",
                "follower_count": 25000,
                "average_views": 15000,
                "engagement_rate": 4.2,
                "content_niche": "lifestyle"
            },
            "550e8400-e29b-41d4-a716-446655440001": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "email": "sarah.creator@test.com",
                "username": "sarahcreator",
                "role": "creator",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "tiktok_handle": "@sarahj",
                "follower_count": 45000,
                "average_views": 28000,
                "engagement_rate": 5.8,
                "content_niche": "fashion"
            },
            "660e8400-e29b-41d4-a716-446655440000": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "email": "agency@testmarketing.com",
                "username": "testmarketing",
                "role": "agency",
                "company_name": "Test Marketing Agency",
                "website_url": "https://testmarketing.com"
            }
        }
        logger.info("🔧 Initialized Mock User Service Client")
    
    async def get_user(self, user_id: UUID) -> Optional[Dict]:
        """Get mock user data"""
        user_str = str(user_id)
        if user_str in self.users:
            return self.users[user_str]
        
        # Generate random user if not predefined
        return self._generate_random_user(user_id)
    
    def _generate_random_user(self, user_id: UUID) -> Dict:
        """Generate random test user"""
        user_types = ["creator", "agency", "brand"]
        role = random.choice(user_types)
        
        base_user = {
            "id": str(user_id),
            "email": f"user_{str(user_id)[:8]}@test.com",
            "username": f"user_{str(user_id)[:8]}",
            "role": role,
            "first_name": random.choice(["Alex", "Jordan", "Taylor", "Casey", "Morgan"]),
            "last_name": random.choice(["Smith", "Johnson", "Brown", "Davis", "Wilson"])
        }
        
        if role == "creator":
            base_user.update({
                "tiktok_handle": f"@{base_user['username']}",
                "follower_count": random.randint(1000, 100000),
                "average_views": random.randint(500, 50000),
                "engagement_rate": round(random.uniform(2.0, 8.0), 1),
                "content_niche": random.choice(["lifestyle", "fashion", "tech", "food", "travel"])
            })
        elif role == "agency":
            base_user.update({
                "company_name": f"{base_user['first_name']} Marketing Agency",
                "website_url": f"https://{base_user['username']}.com"
            })
        
        return base_user
    
    async def check_user_exists_and_role(self, user_id: UUID, expected_role: str) -> bool:
        """Validate user role"""
        user = await self.get_user(user_id)
        return user and user.get("role") == expected_role
    
    async def get_creator_details(self, creator_id: UUID) -> Optional[Dict]:
        """Get detailed creator information"""
        user = await self.get_user(creator_id)
        if user and user.get("role") == "creator":
            return user
        return None
    
    async def get_users_batch(self, user_ids: List[UUID]) -> Dict[UUID, Dict]:
        """Get multiple users"""
        result = {}
        for user_id in user_ids:
            user = await self.get_user(user_id)
            if user:
                result[user_id] = user
        return result

class MockCampaignServiceClient:
    """Complete Campaign Service mock"""
    
    def __init__(self):
        # Pre-defined test campaigns
        self.campaigns = {
            "770e8400-e29b-41d4-a716-446655440000": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "name": "Summer Fashion Collection",
                "payout_model": "hybrid",
                "base_payout_per_post": 75.0,
                "gmv_commission_rate": 8.0,
                "status": "active",
                "gmv_bonus_tiers": [
                    {
                        "tier_name": "Bronze Tier",
                        "min_gmv": 1000.0,
                        "max_gmv": 2500.0,
                        "bonus_type": "flat_amount",
                        "bonus_value": 100.0
                    },
                    {
                        "tier_name": "Silver Tier", 
                        "min_gmv": 2500.0,
                        "max_gmv": 5000.0,
                        "bonus_type": "flat_amount",
                        "bonus_value": 250.0
                    },
                    {
                        "tier_name": "Gold Tier",
                        "min_gmv": 5000.0,
                        "max_gmv": None,
                        "bonus_type": "commission_increase",
                        "bonus_value": 2.0  # Additional 2% commission
                    }
                ],
                "leaderboard_bonuses": [
                    {
                        "position_start": 1,
                        "position_end": 1,
                        "bonus_amount": 500.0,
                        "metric_type": "gmv",
                        "description": "Top GMV Creator"
                    },
                    {
                        "position_start": 2,
                        "position_end": 3,
                        "bonus_amount": 200.0,
                        "metric_type": "gmv",
                        "description": "Top 3 GMV Creators"
                    }
                ]
            }
        }
        logger.info("🔧 Initialized Mock Campaign Service Client")
    
    async def get_campaign(self, campaign_id: UUID) -> Optional[Dict]:
        """Get mock campaign data"""
        campaign_str = str(campaign_id)
        if campaign_str in self.campaigns:
            return self.campaigns[campaign_str]
        
        # Generate random campaign
        return self._generate_random_campaign(campaign_id)
    
    def _generate_random_campaign(self, campaign_id: UUID) -> Dict:
        """Generate random test campaign"""
        payout_models = ["fixed_per_post", "gmv_commission", "hybrid", "retainer_gmv"]
        
        return {
            "id": str(campaign_id),
            "name": f"Test Campaign {str(campaign_id)[:8]}",
            "payout_model": random.choice(payout_models),
            "base_payout_per_post": round(random.uniform(25.0, 100.0), 2),
            "gmv_commission_rate": round(random.uniform(3.0, 10.0), 1),
            "status": "active",
            "gmv_bonus_tiers": [],
            "leaderboard_bonuses": []
        }
    
    async def get_creator_application(self, application_id: UUID) -> Optional[Dict]:
        """Get mock application data"""
        return {
            "id": str(application_id),
            "creator_id": "550e8400-e29b-41d4-a716-446655440000",
            "campaign_id": "770e8400-e29b-41d4-a716-446655440000",
            "status": "approved",
            "applied_at": datetime.now().isoformat()
        }
    
    async def get_creator_deliverables(self, application_id: UUID) -> Dict:
        """Get mock deliverable data"""
        num_deliverables = random.randint(2, 5)
        deliverables = []
        
        for i in range(num_deliverables):
            status = "approved" if i < num_deliverables - 1 else random.choice(["pending", "approved"])
            deliverables.append({
                "id": f"del_{i+1}",
                "deliverable_number": i + 1,
                "status": status,
                "tiktok_post_url": f"https://tiktok.com/@test/video/{secrets.token_hex(8)}",
                "views_count": random.randint(1000, 50000),
                "likes_count": random.randint(100, 5000),
                "submitted_at": datetime.now().isoformat()
            })
        
        completed_count = len([d for d in deliverables if d["status"] == "approved"])
        
        return {
            "deliverables": deliverables,
            "completed_count": completed_count,
            "total_count": len(deliverables)
        }
    
    async def get_campaign_creators(self, campaign_id: UUID) -> List[Dict]:
        """Get mock campaign creators"""
        return [
            {
                "creator_id": "550e8400-e29b-41d4-a716-446655440000",
                "application_id": "880e8400-e29b-41d4-a716-446655440000",
                "status": "approved"
            },
            {
                "creator_id": "550e8400-e29b-41d4-a716-446655440001", 
                "application_id": "880e8400-e29b-41d4-a716-446655440001",
                "status": "approved"
            }
        ]
    
    async def update_campaign_spent_amount(self, campaign_id: UUID, amount: float):
        """Mock campaign spent amount update"""
        logger.info(f"💸 Mock Campaign: Updated spent amount for {campaign_id}: +${amount}")

# Export all mock clients
__all__ = [
    "MockStripeClient",
    "MockFanbasisClient", 
    "MockUserServiceClient",
    "MockCampaignServiceClient"
]
