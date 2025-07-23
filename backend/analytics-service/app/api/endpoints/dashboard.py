
# app/api/endpoints/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, distinct
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Import database models - these would need to be available in analytics service
# For now, we'll create mock responses matching the expected structure
router = APIRouter()
logger = logging.getLogger(__name__)

# ============== CREATOR DASHBOARD ENDPOINTS ==============

@router.get("/creator/{user_id}/overview")
async def get_creator_overview(
    user_id: str
):
    """Get creator dashboard overview data"""
    try:
        # Mock data matching the UI structure
        # In production, this would query the actual databases
        
        # Calculate mock GMV and metrics
        total_gmv = 12500.0
        total_views = 450000
        bonuses = calculate_milestone_bonuses(total_gmv)
        
        return {
            "total_gmv": total_gmv,
            "total_gmv_formatted": f"${total_gmv:,.0f}",
            "gmv_change": "+17%",
            "total_views": total_views,
            "total_views_formatted": format_number(total_views),
            "views_change": "+18%",
            "active_campaigns": 3,
            "bonuses_earned": bonuses,
            "bonuses_earned_formatted": f"${bonuses:,.0f}",
            "bonuses_change": "+21%"
        }
    except Exception as e:
        logger.error(f"Error getting creator overview: {e}")
        return {
            "total_gmv": 0,
            "total_views": 0,
            "active_campaigns": 0,
            "bonuses_earned": 0
        }

@router.get("/creator/{user_id}/campaigns")
async def get_creator_campaigns(
    user_id: str
):
    """Get creator's campaign performance data"""
    return {
        "campaigns": [
            {
                "id": "camp1",
                "brand": "BeautyBrand",
                "brand_logo": "/api/placeholder/40/40",
                "name": "Beauty Essentials Kit",
                "status": "overdue",
                "gmv_generated": 1700,
                "gmv_target": 4000,
                "deliverables_completed": 1,
                "deliverables_total": 4,
                "days_overdue": 2
            },
            {
                "id": "camp2",
                "brand": "FashionBrand",
                "name": "Summer Fashion Collection",
                "status": "active",
                "gmv_generated": 850,
                "gmv_target": 5000,
                "deliverables_completed": 2,
                "deliverables_total": 5,
                "days_left": 13
            },
            {
                "id": "camp3",
                "brand": "TechCorp",
                "name": "Tech Gadget Pro Launch",
                "status": "active",
                "gmv_generated": 2800,
                "gmv_target": 3000,
                "deliverables_completed": 1,
                "deliverables_total": 2,
                "days_left": 14
            }
        ]
    }

@router.get("/creator/{user_id}/badges")
async def get_creator_badges(
    user_id: str
):
    """Get creator's badge achievements"""
    # This would query actual GMV data
    total_gmv = 12500.0
    
    badges = [
        {"name": "$5K GMV", "achieved": total_gmv >= 5000, "milestone": 5000},
        {"name": "$10K GMV", "achieved": total_gmv >= 10000, "milestone": 10000},
        {"name": "$25K GMV", "achieved": total_gmv >= 25000, "milestone": 25000},
        {"name": "1M Views", "achieved": False, "milestone": 1000000},
        {"name": "Rising Star", "achieved": True, "milestone": None},
        {"name": "Top Earner", "achieved": False, "milestone": None}
    ]
    
    return {"badges": badges, "total_gmv": total_gmv}

# ============== AGENCY DASHBOARD ENDPOINTS ==============

@router.get("/agency/{agency_id}/overview")
async def get_agency_overview(
    agency_id: str
):
    """Get agency dashboard overview data"""
    return {
        "total_views": 2400000,
        "total_views_formatted": "2.4M",
        "views_change": "+125%",
        "total_likes": 145000,
        "total_likes_formatted": "145K",
        "likes_change": "+132%",
        "total_payouts": 45860,
        "total_payouts_formatted": "$45,860",
        "new_creators": 23,
        "creators_period": "this period"
    }

@router.get("/agency/{agency_id}/top-creators")
async def get_top_creators(
    agency_id: str,
    limit: int = Query(4, le=10)
):
    """Get top creators by posts for agency"""
    return {
        "creators": [
            {"name": "Ty Anderson", "handle": "@tyanderson", "posts": 76, "avatar": "/api/placeholder/40/40"},
            {"name": "Jana Burkett", "handle": "@janaburkett", "posts": 74, "avatar": "/api/placeholder/40/40"},
            {"name": "Chloe VanScoder", "handle": "@chloevs", "posts": 65, "avatar": "/api/placeholder/40/40"},
            {"name": "Lambirla Burns", "handle": "@lambirlaburns", "posts": 58, "avatar": "/api/placeholder/40/40"}
        ]
    }

@router.get("/agency/{agency_id}/posts-per-day")
async def get_posts_per_day(
    agency_id: str,
    days: int = Query(7, ge=1, le=30)
):
    """Get posts per day analytics"""
    return {
        "data": [
            {"date": "Jun 05", "posts": 250},
            {"date": "Jun 06", "posts": 100},
            {"date": "Jun 07", "posts": 350},
            {"date": "Jun 08", "posts": 400},
            {"date": "Jun 09", "posts": 300},
            {"date": "Jun 10", "posts": 200},
            {"date": "Jun 11", "posts": 150}
        ]
    }

@router.get("/agency/{agency_id}/engagement")
async def get_engagement_metrics(
    agency_id: str,
    period: str = Query("week", regex="^(week|month|quarter)$")
):
    """Get engagement metrics over time"""
    return {
        "data": [
            {"week": "Week 1", "likes": 20000, "comments": 8000, "views": 1800000},
            {"week": "Week 2", "likes": 18000, "comments": 9500, "views": 210000},
            {"week": "Week 3", "likes": 22000, "comments": 11000, "views": 245000},
            {"week": "Week 4", "likes": 24000, "comments": 12000, "views": 268000}
        ]
    }

# ============== BRAND DASHBOARD ENDPOINTS ==============

@router.get("/brand/{shop_id}/overview")
async def get_brand_overview(
    shop_id: str
):
    """Get brand dashboard overview data"""
    total_gmv = 75000.0
    roi = calculate_roi(total_gmv, 10000)  # Assuming 10k spend
    
    return {
        "total_gmv": total_gmv,
        "total_gmv_formatted": f"${total_gmv:,.0f}",
        "gmv_change": "+38%",
        "campaign_roi": roi,
        "roi_formatted": f"{roi:.1f}x",
        "roi_change": "+145%",
        "active_creators": 15,
        "content_reach": 2400000,
        "reach_formatted": "2.4M"
    }

@router.get("/brand/{shop_id}/campaign-performance")
async def get_campaign_performance(
    shop_id: str,
    campaign_id: str,
    days: int = Query(30, ge=1, le=90)
):
    """Get campaign performance over time"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Generate mock daily GMV data
    dates = []
    current = start_date
    day_count = 0
    while current <= end_date and day_count < days:
        dates.append({
            "date": current.strftime("%b %d"),
            "gmv": 5000 + (day_count * 200),  # Mock progressive growth
            "orders": 20 + day_count
        })
        current += timedelta(days=3)
        day_count += 3
    
    return {
        "data": dates,
        "metrics": {
            "conversion_rate": 3.2,
            "average_order_value": 67.50,
            "cost_per_acquisition": 12.30,
            "return_on_ad_spend": 4.2
        }
    }

@router.get("/brand/{shop_id}/top-content")
async def get_top_campaign_content(
    shop_id: str,
    campaign_id: str = None,
    limit: int = Query(6, le=20)
):
    """Get top performing content for campaigns"""
    return {
        "content": [
            {
                "id": "video1",
                "creator": {"name": "Emma Rodriguez", "handle": "@emmarodriguez"},
                "thumbnail": "/api/placeholder/300/400",
                "views": 125400,
                "gmv": 3250,
                "engagement_rate": 8.2,
                "likes": 10289,
                "comments": 892
            },
            {
                "id": "video2",
                "creator": {"name": "Sofia Chen", "handle": "@sofichen"},
                "thumbnail": "/api/placeholder/300/400",
                "views": 98200,
                "gmv": 2890,
                "engagement_rate": 7.5,
                "likes": 7365,
                "comments": 623
            }
        ]
    }

# ============== HELPER FUNCTIONS ==============

def format_number(num: int) -> str:
    """Format large numbers with K/M suffix"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.0f}K"
    return str(num)

def calculate_milestone_bonuses(total_gmv: float) -> float:
    """Calculate bonuses based on GMV milestones"""
    bonuses = 0
    milestones = [
        (5000, 250),
        (10000, 500),
        (25000, 1000),
        (50000, 2000),
        (100000, 5000)
    ]
    
    for milestone, bonus in milestones:
        if total_gmv >= milestone:
            bonuses += bonus
    
    return bonuses

def calculate_roi(revenue: float, cost: float) -> float:
    """Calculate ROI"""
    if cost == 0:
        return 0
    return revenue / cost

