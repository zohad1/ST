# scripts/test_campaign_crud.py
import requests
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8002/api/v1"

# Test data
test_campaign = {
    "name": "Summer Fashion Collection 2025",
    "description": "Showcase our latest summer fashion line with authentic creator content",
    "payout_model": "gmv_commission",
    "tracking_method": "product_link",
    "start_date": datetime.utcnow().isoformat(),
    "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
    "max_creators": 50,
    "min_deliverables_per_creator": 3,
    "base_payout_per_post": 100.0,
    "gmv_commission_rate": 15.0,
    "total_budget": 50000.0,
    "target_gmv": 150000.0,
    "target_posts": 150,
    "target_creators": 50,
    "hashtag": "#LaunchPAIDSummer2025"
}

def test_create_campaign():
    """Test creating a new campaign"""
    logger.info("Testing campaign creation...")
    
    response = requests.post(
        f"{BASE_URL}/campaigns",
        json=test_campaign,
        headers={"Authorization": "agency_token"}
    )
    
    if response.status_code == 201:
        campaign = response.json()
        logger.info(f"✅ Campaign created: {campaign['name']} (ID: {campaign['id']})")
        return campaign['id']
    else:
        logger.error(f"❌ Failed to create campaign: {response.status_code} - {response.text}")
        return None

def test_get_campaigns():
    """Test listing campaigns"""
    logger.info("\nTesting campaign listing...")
    
    response = requests.get(
        f"{BASE_URL}/campaigns",
        headers={"Authorization": "agency_token"}
    )
    
    if response.status_code == 200:
        campaigns = response.json()
        logger.info(f"✅ Found {len(campaigns)} campaigns")
        for campaign in campaigns[:3]:  # Show first 3
            logger.info(f"   - {campaign['name']} ({campaign['status']})")
    else:
        logger.error(f"❌ Failed to get campaigns: {response.status_code}")

def test_update_campaign(campaign_id):
    """Test updating a campaign"""
    logger.info(f"\nTesting campaign update for ID: {campaign_id}")
    
    update_data = {
        "status": "active",
        "max_creators": 75,
        "target_gmv": 200000.0
    }
    
    response = requests.put(
        f"{BASE_URL}/campaigns/{campaign_id}",
        json=update_data,
        headers={"Authorization": "agency_token"}
    )
    
    if response.status_code == 200:
        campaign = response.json()
        logger.info(f"✅ Campaign updated: Status={campaign['status']}, Max Creators={campaign['max_creators']}")
    else:
        logger.error(f"❌ Failed to update campaign: {response.status_code}")

def test_campaign_segments(campaign_id):
    """Test creating campaign segments"""
    logger.info(f"\nTesting segment creation for campaign: {campaign_id}")
    
    segments = [
        {
            "segment_name": "Fashion Enthusiasts",
            "segment_description": "Creators focused on fashion and style content",
            "age_min": 18,
            "age_max": 35,
            "min_followers": 10000,
            "gender_filter": ["FEMALE"],
            "max_creators_in_segment": 25
        },
        {
            "segment_name": "Lifestyle Influencers",
            "segment_description": "Broad lifestyle content creators",
            "age_min": 21,
            "age_max": 45,
            "min_followers": 5000,
            "max_creators_in_segment": 25
        }
    ]
    
    for segment in segments:
        response = requests.post(
            f"{BASE_URL}/campaigns/{campaign_id}/segments",
            json=segment,
            headers={"Authorization": "agency_token"}
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Segment created: {segment['segment_name']}")
        else:
            logger.error(f"❌ Failed to create segment: {response.status_code}")

def test_bonus_tiers(campaign_id):
    """Test creating GMV bonus tiers"""
    logger.info(f"\nTesting bonus tier creation for campaign: {campaign_id}")
    
    bonus_tiers = [
        {
            "tier_name": "Bronze",
            "min_gmv": 1000.0,
            "max_gmv": 5000.0,
            "bonus_type": "flat_amount",
            "bonus_value": 100.0
        },
        {
            "tier_name": "Silver",
            "min_gmv": 5000.0,
            "max_gmv": 10000.0,
            "bonus_type": "flat_amount",
            "bonus_value": 300.0
        },
        {
            "tier_name": "Gold",
            "min_gmv": 10000.0,
            "bonus_type": "commission_increase",
            "bonus_value": 5.0  # 5% additional commission
        }
    ]
    
    for tier in bonus_tiers:
        response = requests.post(
            f"{BASE_URL}/campaigns/{campaign_id}/bonus-tiers",
            json=tier,
            headers={"Authorization": "agency_token"}
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Bonus tier created: {tier['tier_name']}")
        else:
            logger.error(f"❌ Failed to create bonus tier: {response.status_code}")

def test_leaderboard_bonuses(campaign_id):
    """Test creating leaderboard bonuses"""
    logger.info(f"\nTesting leaderboard bonus creation for campaign: {campaign_id}")
    
    leaderboard_bonuses = [
        {
            "position_start": 1,
            "position_end": 1,
            "bonus_amount": 1000.0,
            "metric_type": "gmv",
            "description": "Top GMV performer bonus"
        },
        {
            "position_start": 2,
            "position_end": 3,
            "bonus_amount": 500.0,
            "metric_type": "gmv",
            "description": "2nd and 3rd place GMV bonus"
        },
        {
            "position_start": 1,
            "position_end": 5,
            "bonus_amount": 200.0,
            "metric_type": "posts",
            "description": "Top 5 most active creators"
        }
    ]
    
    for bonus in leaderboard_bonuses:
        response = requests.post(
            f"{BASE_URL}/campaigns/{campaign_id}/leaderboard-bonuses",
            json=bonus,
            headers={"Authorization": "agency_token"}
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Leaderboard bonus created: {bonus['description']}")
        else:
            logger.error(f"❌ Failed to create leaderboard bonus: {response.status_code}")

def run_all_tests():
    """Run all campaign CRUD tests"""
    logger.info("🚀 Starting Campaign CRUD Tests")
    logger.info("=" * 60)
    
    # Create a campaign
    campaign_id = test_create_campaign()
    
    if campaign_id:
        # Test other operations
        test_get_campaigns()
        test_update_campaign(campaign_id)
        test_campaign_segments(campaign_id)
        test_bonus_tiers(campaign_id)
        test_leaderboard_bonuses(campaign_id)
        
        # Get full campaign details
        logger.info(f"\nFetching complete campaign details...")
        response = requests.get(
            f"{BASE_URL}/campaigns/{campaign_id}",
            headers={"Authorization": "agency_token"}
        )
        
        if response.status_code == 200:
            campaign = response.json()
            logger.info(f"✅ Campaign retrieved successfully")
            logger.info(f"   Name: {campaign['name']}")
            logger.info(f"   Status: {campaign['status']}")
            logger.info(f"   Budget: ${campaign['total_budget']}")
            logger.info(f"   Target GMV: ${campaign['target_gmv']}")
    
    logger.info("\n✅ All tests completed!")

if __name__ == "__main__":
    run_all_tests()