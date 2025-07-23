# simple_analytics.py
# Complete working analytics service in one file

from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
import uuid
import json

app = FastAPI(
    title="Analytics Service",
    version="1.0.0",
    description="Analytics and reporting service for TikTok Shop Creator CRM"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CampaignPerformanceCreate(BaseModel):
    campaign_id: str
    date_snapshot: date
    total_creators: int = 0
    active_creators: int = 0
    new_applications: int = 0
    approved_applications: int = 0
    posts_submitted: int = 0
    posts_approved: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_gmv: str = "0.00"
    total_commissions: str = "0.00"
    total_payouts: str = "0.00"
    avg_engagement_rate: str = "0.00"
    conversion_rate: str = "0.00"
    cost_per_acquisition: str = "0.00"

class CampaignPerformanceResponse(CampaignPerformanceCreate):
    id: str
    created_at: datetime

class CreatorPerformanceUpdate(BaseModel):
    total_posts: Optional[int] = None
    completed_deliverables: Optional[int] = None
    on_time_deliverables: Optional[int] = None
    total_gmv: Optional[str] = None
    avg_views_per_post: Optional[str] = None
    avg_engagement_rate: Optional[str] = None
    consistency_score: Optional[str] = None
    reliability_rating: Optional[str] = None

# In-memory storage
performance_data = {}
creator_data = {}

# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "Analytics Service is running!",
        "version": "1.0.0",
        "environment": "development",
        "total_records": len(performance_data)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "analytics-service",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

# =============================================================================
# CAMPAIGN ANALYTICS ENDPOINTS
# =============================================================================

@app.post("/api/v1/campaigns/{campaign_id}/performance/daily", response_model=CampaignPerformanceResponse)
async def create_campaign_performance(
    campaign_id: str,
    performance_data_input: CampaignPerformanceCreate
):
    """Create or update daily performance metrics for a campaign"""
    
    # Validate campaign_id matches
    if performance_data_input.campaign_id != campaign_id:
        raise HTTPException(
            status_code=400,
            detail="Campaign ID in URL does not match campaign ID in data"
        )
    
    # Create response data
    record_id = str(uuid.uuid4())
    response_data = CampaignPerformanceResponse(
        **performance_data_input.model_dump(),
        id=record_id,
        created_at=datetime.now()
    )
    
    # Store in memory
    key = f"{campaign_id}_{performance_data_input.date_snapshot}"
    performance_data[key] = response_data.model_dump()
    
    return response_data

@app.get("/api/v1/campaigns/{campaign_id}/performance/daily")
async def get_campaign_daily_performance(
    campaign_id: str,
    date_snapshot: date = Query(default_factory=lambda: date.today())
):
    """Get daily performance metrics for a specific campaign"""
    
    key = f"{campaign_id}_{date_snapshot}"
    
    if key not in performance_data:
        raise HTTPException(
            status_code=404,
            detail=f"No performance data found for campaign {campaign_id} on {date_snapshot}"
        )
    
    return performance_data[key]

@app.get("/api/v1/campaigns/{campaign_id}/performance/range")
async def get_campaign_performance_range(
    campaign_id: str,
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today())
):
    """Get performance metrics for a campaign over a date range"""
    
    result = []
    for key, data in performance_data.items():
        if key.startswith(campaign_id):
            data_date = datetime.fromisoformat(data['date_snapshot']).date()
            if start_date <= data_date <= end_date:
                result.append(data)
    
    return sorted(result, key=lambda x: x['date_snapshot'])

@app.get("/api/v1/campaigns/{campaign_id}/summary")
async def get_campaign_summary(
    campaign_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get campaign analytics summary"""
    
    # Filter data for this campaign
    campaign_records = []
    for key, data in performance_data.items():
        if key.startswith(campaign_id):
            if start_date and end_date:
                data_date = datetime.fromisoformat(data['date_snapshot']).date()
                if start_date <= data_date <= end_date:
                    campaign_records.append(data)
            else:
                campaign_records.append(data)
    
    if not campaign_records:
        return {
            "campaign_id": campaign_id,
            "campaign_name": f"Campaign {campaign_id[:8]}...",
            "total_gmv": "0.00",
            "total_creators": 0,
            "total_posts": 0,
            "avg_engagement_rate": "0.00",
            "conversion_rate": "0.00",
            "date_range": {
                "start_date": str(start_date or date.today()),
                "end_date": str(end_date or date.today())
            }
        }
    
    # Calculate summary
    total_gmv = sum(float(record.get('total_gmv', 0)) for record in campaign_records)
    total_posts = sum(record.get('posts_submitted', 0) for record in campaign_records)
    max_creators = max(record.get('total_creators', 0) for record in campaign_records)
    avg_engagement = sum(float(record.get('avg_engagement_rate', 0)) for record in campaign_records) / len(campaign_records)
    avg_conversion = sum(float(record.get('conversion_rate', 0)) for record in campaign_records) / len(campaign_records)
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": f"Campaign {campaign_id[:8]}...",
        "total_gmv": f"{total_gmv:.2f}",
        "total_creators": max_creators,
        "total_posts": total_posts,
        "avg_engagement_rate": f"{avg_engagement:.2f}",
        "conversion_rate": f"{avg_conversion:.2f}",
        "date_range": {
            "start_date": str(start_date or date.today() - timedelta(days=30)),
            "end_date": str(end_date or date.today())
        }
    }

@app.get("/api/v1/campaigns/{campaign_id}/progress")
async def get_campaign_progress(campaign_id: str):
    """Get campaign progress against targets"""
    
    # Get all data for campaign
    campaign_records = [
        data for key, data in performance_data.items() 
        if key.startswith(campaign_id)
    ]
    
    if not campaign_records:
        return {
            "campaign_id": campaign_id,
            "target_gmv": None,
            "current_gmv": "0.00",
            "target_posts": None,
            "current_posts": 0,
            "progress_percentage": 0.0,
            "status": "no_data",
            "days_remaining": None
        }
    
    # Calculate current totals
    current_gmv = sum(float(record.get('total_gmv', 0)) for record in campaign_records)
    current_posts = sum(record.get('posts_submitted', 0) for record in campaign_records)
    
    # Mock targets (in real implementation, get from campaign service)
    target_gmv = 10000.0
    target_posts = 100
    
    # Calculate progress
    gmv_progress = (current_gmv / target_gmv) * 100 if target_gmv > 0 else 0
    posts_progress = (current_posts / target_posts) * 100 if target_posts > 0 else 0
    progress_percentage = (gmv_progress + posts_progress) / 2
    
    # Determine status
    if progress_percentage >= 100:
        status = "completed"
    elif progress_percentage >= 80:
        status = "ahead"
    elif progress_percentage >= 60:
        status = "on_track"
    else:
        status = "behind"
    
    return {
        "campaign_id": campaign_id,
        "target_gmv": f"{target_gmv:.2f}",
        "current_gmv": f"{current_gmv:.2f}",
        "target_posts": target_posts,
        "current_posts": current_posts,
        "progress_percentage": round(progress_percentage, 2),
        "status": status,
        "days_remaining": 30  # Mock value
    }

# =============================================================================
# CREATOR ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/v1/creators/{creator_id}/performance")
async def get_creator_performance(
    creator_id: str,
    campaign_id: Optional[str] = Query(None)
):
    """Get performance metrics for a specific creator"""
    
    key = f"{creator_id}_{campaign_id or 'overall'}"
    
    if key not in creator_data:
        # Return default performance data
        return {
            "id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "campaign_id": campaign_id,
            "total_posts": 0,
            "completed_deliverables": 0,
            "on_time_deliverables": 0,
            "total_gmv": "0.00",
            "avg_views_per_post": "0.00",
            "avg_engagement_rate": "0.00",
            "consistency_score": "0.00",
            "reliability_rating": "0.0",
            "last_calculated": datetime.now().isoformat()
        }
    
    return creator_data[key]

@app.put("/api/v1/creators/{creator_id}/performance")
async def update_creator_performance(
    creator_id: str,
    performance_update: CreatorPerformanceUpdate,
    campaign_id: Optional[str] = Query(None)
):
    """Update performance metrics for a creator"""
    
    key = f"{creator_id}_{campaign_id or 'overall'}"
    
    # Get existing data or create new
    if key in creator_data:
        existing_data = creator_data[key]
    else:
        existing_data = {
            "id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "campaign_id": campaign_id,
            "total_posts": 0,
            "completed_deliverables": 0,
            "on_time_deliverables": 0,
            "total_gmv": "0.00",
            "avg_views_per_post": "0.00",
            "avg_engagement_rate": "0.00",
            "consistency_score": "0.00",
            "reliability_rating": "0.0"
        }
    
    # Update with new data
    update_dict = performance_update.model_dump(exclude_unset=True)
    existing_data.update(update_dict)
    existing_data["last_calculated"] = datetime.now().isoformat()
    
    creator_data[key] = existing_data
    
    return existing_data

@app.get("/api/v1/creators/leaderboard")
async def get_creator_leaderboard(
    campaign_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    """Get creator leaderboard by GMV performance"""
    
    # Filter creator data
    relevant_data = []
    for key, data in creator_data.items():
        if campaign_id is None or data.get('campaign_id') == campaign_id:
            relevant_data.append(data)
    
    # Sort by GMV descending
    sorted_data = sorted(relevant_data, key=lambda x: float(x.get('total_gmv', 0)), reverse=True)
    
    # Add rank and limit results
    leaderboard = []
    for idx, creator in enumerate(sorted_data[:limit]):
        leaderboard.append({
            "creator_id": creator['creator_id'],
            "creator_name": f"Creator {creator['creator_id'][:8]}...",
            "total_gmv": creator.get('total_gmv', '0.00'),
            "total_posts": creator.get('total_posts', 0),
            "avg_engagement_rate": creator.get('avg_engagement_rate', '0.00'),
            "rank": idx + 1
        })
    
    return leaderboard

# =============================================================================
# DASHBOARD ENDPOINTS
# =============================================================================

@app.get("/api/v1/dashboard/overview")
async def get_overview_metrics():
    """Get overview analytics metrics"""
    
    total_campaigns = len(set(key.split('_')[0] for key in performance_data.keys()))
    total_creators = len(creator_data)
    total_gmv = sum(float(data.get('total_gmv', 0)) for data in performance_data.values())
    total_posts = sum(data.get('posts_submitted', 0) for data in performance_data.values())
    total_views = sum(data.get('total_views', 0) for data in performance_data.values())
    
    avg_engagement = 0
    if performance_data:
        avg_engagement = sum(float(data.get('avg_engagement_rate', 0)) for data in performance_data.values()) / len(performance_data)
    
    return {
        "total_campaigns": total_campaigns,
        "total_creators": total_creators,
        "total_gmv": f"{total_gmv:.2f}",
        "total_posts": total_posts,
        "total_views": total_views,
        "avg_engagement_rate": f"{avg_engagement:.2f}",
        "top_performing_campaigns": [],
        "top_performing_creators": []
    }

@app.get("/api/v1/dashboard/engagement")
async def get_engagement_analytics():
    """Get engagement analytics"""
    
    total_views = sum(data.get('total_views', 0) for data in performance_data.values())
    total_likes = sum(data.get('total_likes', 0) for data in performance_data.values())
    total_comments = sum(data.get('total_comments', 0) for data in performance_data.values())
    total_shares = sum(data.get('total_shares', 0) for data in performance_data.values())
    
    engagement_rate = 0
    if total_views > 0:
        total_engagement = total_likes + total_comments + total_shares
        engagement_rate = (total_engagement / total_views) * 100
    
    view_to_like_ratio = 0
    if total_likes > 0:
        view_to_like_ratio = total_views / total_likes
    
    return {
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "engagement_rate": f"{engagement_rate:.2f}",
        "view_to_like_ratio": f"{view_to_like_ratio:.2f}"
    }

@app.get("/api/v1/dashboard/gmv")
async def get_gmv_analytics():
    """Get GMV analytics"""
    
    total_gmv = sum(float(data.get('total_gmv', 0)) for data in performance_data.values())
    total_posts = sum(data.get('posts_submitted', 0) for data in performance_data.values())
    total_creators = len(set(data.get('campaign_id', '').split('_')[0] for data in performance_data.values() if data.get('campaign_id')))
    
    avg_gmv_per_post = 0
    if total_posts > 0:
        avg_gmv_per_post = total_gmv / total_posts
    
    avg_gmv_per_creator = 0
    if total_creators > 0:
        avg_gmv_per_creator = total_gmv / total_creators
    
    return {
        "total_gmv": f"{total_gmv:.2f}",
        "gmv_growth_rate": "0.00",
        "avg_gmv_per_creator": f"{avg_gmv_per_creator:.2f}",
        "avg_gmv_per_post": f"{avg_gmv_per_post:.2f}",
        "top_gmv_days": []
    }

# =============================================================================
# REPORTS ENDPOINTS
# =============================================================================

@app.get("/api/v1/reports/campaign-performance-csv")
async def export_campaign_performance_csv(campaign_id: str):
    """Export campaign performance data as CSV"""
    
    # Create CSV content
    csv_content = "Date,Campaign ID,Total GMV,Posts Submitted,Total Views,Total Likes,Engagement Rate\n"
    
    for key, data in performance_data.items():
        if key.startswith(campaign_id):
            csv_content += f"{data.get('date_snapshot')},{data.get('campaign_id')},{data.get('total_gmv')},{data.get('posts_submitted')},{data.get('total_views')},{data.get('total_likes')},{data.get('avg_engagement_rate')}\n"
    
    if csv_content == "Date,Campaign ID,Total GMV,Posts Submitted,Total Views,Total Likes,Engagement Rate\n":
        csv_content += f"{date.today()},{campaign_id},0.00,0,0,0,0.00\n"
    
    headers = {
        'Content-Disposition': f'attachment; filename="campaign_{campaign_id}_performance.csv"'
    }
    
    return Response(
        content=csv_content,
        media_type='text/csv',
        headers=headers
    )

@app.get("/api/v1/reports/creator-leaderboard-csv")
async def export_creator_leaderboard_csv(
    campaign_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000)
):
    """Export creator leaderboard as CSV"""
    
    # Get leaderboard data
    leaderboard_data = await get_creator_leaderboard(campaign_id, limit)
    
    # Create CSV content
    csv_content = "Rank,Creator ID,Creator Name,Total GMV,Total Posts,Avg Engagement Rate\n"
    
    for creator in leaderboard_data:
        csv_content += f"{creator['rank']},{creator['creator_id']},{creator['creator_name']},{creator['total_gmv']},{creator['total_posts']},{creator['avg_engagement_rate']}\n"
    
    if not leaderboard_data:
        csv_content += "1,No Data,No Data,0.00,0,0.00\n"
    
    filename = f"creator_leaderboard_{campaign_id if campaign_id else 'all'}_{date.today()}.csv"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return Response(
        content=csv_content,
        media_type='text/csv',
        headers=headers
    )

# =============================================================================
# TEST AND DEBUG ENDPOINTS
# =============================================================================

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify service is working"""
    return {
        "message": "Analytics Service test successful!",
        "timestamp": datetime.now().isoformat(),
        "data_status": {
            "performance_records": len(performance_data),
            "creator_records": len(creator_data)
        },
        "endpoints_available": [
            "/health",
            "/api/v1/dashboard/overview",
            "/api/v1/campaigns/{id}/performance/daily",
            "/api/v1/creators/leaderboard",
            "/api/v1/reports/campaign-performance-csv"
        ]
    }

@app.get("/api/v1/debug")
async def debug_data():
    """Debug endpoint to see stored data"""
    return {
        "performance_data": {
            "total_records": len(performance_data),
            "sample_keys": list(performance_data.keys())[:3],
            "sample_data": dict(list(performance_data.items())[:2]) if performance_data else {}
        },
        "creator_data": {
            "total_records": len(creator_data),
            "sample_keys": list(creator_data.keys())[:3]
        }
    }