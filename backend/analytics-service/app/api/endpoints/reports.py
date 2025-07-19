
# Step 7: Fix app/api/endpoints/reports.py

from fastapi import APIRouter, Response, Query
from typing import Optional

router = APIRouter()

@router.get("/")
async def reports_root():
    """Root reports endpoint"""
    return {
        "message": "Reports API",
        "endpoints": ["campaign-performance-csv", "creator-leaderboard-csv"]
    }

@router.get("/campaign-performance-csv")
async def export_campaign_performance_csv(campaign_id: str):
    """Export campaign performance data as CSV"""
    
    try:
        from .campaigns import campaign_data_store
        
        # Create CSV content
        csv_content = "Date,Campaign ID,Total GMV,Posts Submitted,Total Views,Total Likes,Engagement Rate\n"
        
        for key, data in campaign_data_store.items():
            if key.startswith(campaign_id):
                csv_content += f"{data.get('date_snapshot', '')},{data.get('campaign_id', '')},{data.get('total_gmv', '0.00')},{data.get('posts_submitted', 0)},{data.get('total_views', 0)},{data.get('total_likes', 0)},{data.get('avg_engagement_rate', '0.00')}\n"
        
        if csv_content == "Date,Campaign ID,Total GMV,Posts Submitted,Total Views,Total Likes,Engagement Rate\n":
            csv_content += f"{date.today()},{campaign_id},0.00,0,0,0,0.00\n"
    
    except:
        # Fallback CSV
        csv_content = f"Date,Campaign ID,Total GMV,Posts Submitted,Total Views,Total Likes,Engagement Rate\n{date.today()},{campaign_id},0.00,0,0,0,0.00\n"
    
    headers = {
        'Content-Disposition': f'attachment; filename="campaign_{campaign_id}_performance.csv"'
    }
    
    return Response(
        content=csv_content,
        media_type='text/csv',
        headers=headers
    )

@router.get("/creator-leaderboard-csv")
async def export_creator_leaderboard_csv(
    campaign_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000)
):
    """Export creator leaderboard as CSV"""
    
    try:
        from .creators import creator_data_store
        
        # Get leaderboard data
        relevant_data = []
        for key, data in creator_data_store.items():
            if campaign_id is None or data.get('campaign_id') == campaign_id:
                relevant_data.append(data)
        
        # Sort by GMV descending
        sorted_data = sorted(relevant_data, key=lambda x: float(x.get('total_gmv', 0)), reverse=True)
        
        # Create CSV content
        csv_content = "Rank,Creator ID,Creator Name,Total GMV,Total Posts,Avg Engagement Rate\n"
        
        for idx, creator in enumerate(sorted_data[:limit]):
            csv_content += f"{idx + 1},{creator.get('creator_id', 'unknown')},Creator {creator.get('creator_id', 'unknown')[:8]}...,{creator.get('total_gmv', '0.00')},{creator.get('total_posts', 0)},{creator.get('avg_engagement_rate', '0.00')}\n"
        
        if not sorted_data:
            csv_content += "1,No Data,No Data,0.00,0,0.00\n"
    
    except:
        # Fallback CSV
        csv_content = "Rank,Creator ID,Creator Name,Total GMV,Total Posts,Avg Engagement Rate\n1,No Data,No Data,0.00,0,0.00\n"
    
    filename = f"creator_leaderboard_{campaign_id if campaign_id else 'all'}_{date.today()}.csv"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return Response(
        content=csv_content,
        media_type='text/csv',
        headers=headers
    )