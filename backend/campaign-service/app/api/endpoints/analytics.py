from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.campaign import Campaign, CampaignApplication, Deliverable
from app.models.user import User
from app.schemas.analytics import CampaignAnalytics

router = APIRouter()

@router.get("/campaigns/{campaign_id}/analytics", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics for a specific campaign for the current user
    """
    # Check if campaign exists
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check if user has an approved application for this campaign
    result = await db.execute(
        select(CampaignApplication).where(
            CampaignApplication.campaign_id == campaign_id,
            CampaignApplication.creator_id == current_user["id"],
            CampaignApplication.status == "approved"
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=403, detail="You don't have access to this campaign")
    
    # Get user's deliverables for this campaign
    result = await db.execute(
        select(Deliverable).where(
            Deliverable.campaign_id == campaign_id,
            Deliverable.creator_id == current_user["id"]
        )
    )
    user_deliverables = result.scalars().all()
    
    # Calculate user metrics
    user_gmv = sum(d.gmv_generated or 0 for d in user_deliverables)
    user_views = sum(d.views or 0 for d in user_deliverables)
    user_likes = sum(d.likes or 0 for d in user_deliverables)
    user_comments = sum(d.comments or 0 for d in user_deliverables)
    user_shares = sum(d.shares or 0 for d in user_deliverables)
    
    # Calculate user engagement rate
    total_engagement = user_likes + user_comments + user_shares
    user_engagement_rate = (total_engagement / user_views * 100) if user_views > 0 else 0
    
    # Count user deliverables
    user_completed_deliverables = len([d for d in user_deliverables if d.status in ["approved", "submitted"]])
    user_total_deliverables = len(user_deliverables)
    
    # Calculate campaign-wide metrics
    campaign_gmv = campaign.current_gmv or 0
    campaign_target_gmv = campaign.target_gmv or 0
    gmv_progress_percentage = (campaign_gmv / campaign_target_gmv * 100) if campaign_target_gmv > 0 else 0
    
    # Get total deliverables for the campaign
    total_deliverables = campaign.min_deliverables_per_creator or 1
    
    # Count completed deliverables across all creators
    result = await db.execute(
        select(func.count()).select_from(Deliverable).where(
            Deliverable.campaign_id == campaign_id,
            Deliverable.status.in_(["approved", "submitted"])
        )
    )
    all_deliverables = result.scalar()
    
    deliverable_progress_percentage = (all_deliverables / total_deliverables * 100) if total_deliverables > 0 else 0
    
    # Calculate days remaining
    if campaign.end_date:
        days_remaining = max(0, (campaign.end_date - datetime.now()).days)
    else:
        days_remaining = 0
    
    # Determine campaign status
    if days_remaining == 0:
        campaign_status = "completed"
    elif days_remaining <= 7:
        campaign_status = "ending_soon"
    else:
        campaign_status = "active"
    
    # Get user's rank in the campaign
    # Get all creators with their GMV for ranking
    result = await db.execute(
        select(
            Deliverable.creator_id,
            func.sum(Deliverable.gmv_generated).label('total_gmv')
        ).where(
            Deliverable.campaign_id == campaign_id
        ).group_by(Deliverable.creator_id)
    )
    all_creators_gmv = result.all()
    
    # Sort by GMV to find user's rank
    sorted_creators = sorted(all_creators_gmv, key=lambda x: x.total_gmv or 0, reverse=True)
    user_rank = None
    for i, (creator_id, gmv) in enumerate(sorted_creators):
        if creator_id == current_user["id"]:
            user_rank = i + 1
            break
    
    # Get total number of creators in the campaign
    result = await db.execute(
        select(func.count()).select_from(CampaignApplication).where(
            CampaignApplication.campaign_id == campaign_id,
            CampaignApplication.status == "approved"
        )
    )
    total_creators = result.scalar()
    
    return CampaignAnalytics(
        campaign_id=str(campaign_id),
        campaign_name=campaign.name,
        current_gmv=campaign_gmv,
        target_gmv=campaign_target_gmv,
        gmv_progress_percentage=round(gmv_progress_percentage, 1),
        total_deliverables=total_deliverables,
        completed_deliverables=all_deliverables,
        deliverable_progress_percentage=round(deliverable_progress_percentage, 1),
        days_remaining=days_remaining,
        campaign_status=campaign_status,
        user_rank=user_rank or 0,
        total_creators=total_creators,
        user_gmv=user_gmv,
        user_deliverables_completed=user_completed_deliverables,
        user_total_deliverables=user_total_deliverables,
        user_engagement_rate=round(user_engagement_rate, 1),
        user_total_views=user_views
    ) 