from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.campaign import Campaign, CampaignApplication, Deliverable
from app.models.user import User
from app.schemas.leaderboard import LeaderboardEntry, CampaignLeaderboard

router = APIRouter()

@router.get("/campaigns/{campaign_id}/leaderboard", response_model=CampaignLeaderboard)
async def get_campaign_leaderboard(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the leaderboard for a specific campaign
    """
    # Check if campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get all applications for this campaign
    applications = db.query(CampaignApplication).filter(
        CampaignApplication.campaign_id == campaign_id,
        CampaignApplication.status == "approved"
    ).all()
    
    # Get creator data with their deliverables and performance
    leaderboard_entries = []
    total_gmv = 0
    total_views = 0
    
    for app in applications:
        # Get creator details
        creator = db.query(User).filter(User.id == app.creator_id).first()
        if not creator:
            continue
            
        # Get creator's deliverables for this campaign
        deliverables = db.query(Deliverable).filter(
            Deliverable.campaign_id == campaign_id,
            Deliverable.creator_id == app.creator_id
        ).all()
        
        # Calculate metrics
        creator_gmv = sum(d.gmv_generated or 0 for d in deliverables)
        creator_views = sum(d.views or 0 for d in deliverables)
        creator_likes = sum(d.likes or 0 for d in deliverables)
        creator_comments = sum(d.comments or 0 for d in deliverables)
        creator_shares = sum(d.shares or 0 for d in deliverables)
        
        # Calculate engagement rate
        total_engagement = creator_likes + creator_comments + creator_shares
        engagement_rate = (total_engagement / creator_views * 100) if creator_views > 0 else 0
        
        # Count completed deliverables
        completed_deliverables = len([d for d in deliverables if d.status in ["approved", "submitted"]])
        total_deliverables = len(deliverables)
        
        # Check if this is the current user
        is_current_user = app.creator_id == current_user["id"]
        
        entry = LeaderboardEntry(
            rank=0,  # Will be set after sorting
            creator_id=str(app.creator_id),
            creator_name=f"{creator.first_name} {creator.last_name}",
            username=creator.username or f"@{creator.username}",
            avatar_url=creator.profile_image_url,
            gmv=creator_gmv,
            deliverables_completed=completed_deliverables,
            total_deliverables=total_deliverables,
            engagement_rate=round(engagement_rate, 1),
            total_views=creator_views,
            is_current_user=is_current_user
        )
        
        leaderboard_entries.append(entry)
        total_gmv += creator_gmv
        total_views += creator_views
    
    # Sort by GMV (descending) and assign ranks
    leaderboard_entries.sort(key=lambda x: x.gmv, reverse=True)
    for i, entry in enumerate(leaderboard_entries):
        entry.rank = i + 1
    
    # Find current user's rank
    current_user_rank = None
    current_user_gmv = None
    for entry in leaderboard_entries:
        if entry.is_current_user:
            current_user_rank = entry.rank
            current_user_gmv = entry.gmv
            break
    
    return CampaignLeaderboard(
        campaign_id=str(campaign_id),
        campaign_name=campaign.name,
        total_creators=len(leaderboard_entries),
        total_gmv=total_gmv,
        total_views=total_views,
        entries=leaderboard_entries,
        current_user_rank=current_user_rank,
        current_user_gmv=current_user_gmv
    ) 