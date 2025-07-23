# app/api/v1/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.rate_limiter import api_limit
from app.utils.dependencies import get_current_verified_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardAnalyticsResponse, CampaignResponse, CampaignCreateRequest, 
    CampaignUpdateRequest, CampaignApplicationResponse, ApplicationReviewRequest,
    DeliverableResponse, DeliverableCreateRequest, DeliverableUpdateRequest,
    ContentSubmissionRequest, ContentReviewRequest, CreatorPerformanceResponse,
    LeaderboardResponse, AnalyticsRequest, AnalyticsTimeframe
)
from app.services.dashboard_service import dashboard_service
from app.services.campaign_service import campaign_service
from app.services.analytics_service import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dashboard"])


# =============================================================================
# ANALYTICS & DASHBOARD ENDPOINTS
# =============================================================================

@router.get("/analytics", response_model=DashboardAnalyticsResponse)
@api_limit
async def get_dashboard_analytics(
    request: Request,
    response: Response,
    timeframe: AnalyticsTimeframe = Query(AnalyticsTimeframe.LAST_30_DAYS),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard analytics for the current user.
    
    Supports different timeframes and custom date ranges.
    Returns KPIs, campaign summaries, and top creators.
    """
    try:
        analytics_request = AnalyticsRequest(
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        analytics_data = await dashboard_service.get_dashboard_analytics(
            db, current_user, analytics_request
        )
        
        return analytics_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard analytics"
        )


@router.get("/creator-performance", response_model=List[CreatorPerformanceResponse])
@api_limit
async def get_creator_performance(
    request: Request,
    response: Response,
    campaign_id: Optional[str] = Query(None),
    timeframe: AnalyticsTimeframe = Query(AnalyticsTimeframe.LAST_30_DAYS),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get creator performance metrics.
    
    For agencies: Shows their managed creators
    For creators: Shows their own performance
    For brands: Shows creators from their campaigns
    """
    try:
        performance_data = await analytics_service.get_creator_performance(
            db, current_user, campaign_id, timeframe, limit
        )
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Error fetching creator performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch creator performance"
        )


@router.get("/leaderboard", response_model=LeaderboardResponse)
@api_limit
async def get_creator_leaderboard(
    request: Request,
    response: Response,
    metric: str = Query("gmv", regex="^(gmv|engagement|consistency)$"),
    timeframe: AnalyticsTimeframe = Query(AnalyticsTimeframe.LAST_30_DAYS),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get creator leaderboard ranked by specified metric.
    
    Available metrics: gmv, engagement, consistency
    """
    try:
        leaderboard = await analytics_service.get_creator_leaderboard(
            db, current_user, metric, timeframe, limit
        )
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch creator leaderboard"
        )


# =============================================================================
# CAMPAIGN MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/campaigns", response_model=List[CampaignResponse])
@api_limit
async def get_campaigns(
    request: Request,
    response: Response,
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get campaigns based on user role.
    
    Agency: Their created campaigns
    Creator: Campaigns they've applied to or are participating in
    Brand: Their sponsored campaigns
    """
    try:
        campaigns = await campaign_service.get_user_campaigns(
            db, current_user, status, limit, offset
        )
        
        return campaigns
        
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaigns"
        )


@router.post("/campaigns", response_model=CampaignResponse)
@api_limit
async def create_campaign(
    request: Request,
    response: Response,
    campaign_data: CampaignCreateRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Create a new campaign.
    
    Only available to agency and brand users.
    """
    if current_user.role not in ["agency", "brand"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agencies and brands can create campaigns"
        )
    
    try:
        campaign = await campaign_service.create_campaign(
            db, current_user, campaign_data
        )
        
        return campaign
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign"
        )


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
@api_limit
async def get_campaign(
    request: Request,
    response: Response,
    campaign_id: str,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get campaign details by ID."""
    try:
        campaign = await campaign_service.get_campaign_by_id(
            db, current_user, campaign_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaign"
        )


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
@api_limit
async def update_campaign(
    request: Request,
    response: Response,
    campaign_id: str,
    update_data: CampaignUpdateRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Update campaign details."""
    try:
        campaign = await campaign_service.update_campaign(
            db, current_user, campaign_id, update_data
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return campaign
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campaign"
        )


# =============================================================================
# APPLICATION MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/applications", response_model=List[CampaignApplicationResponse])
@api_limit
async def get_applications(
    request: Request,
    response: Response,
    campaign_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get campaign applications.
    
    Agency/Brand: Applications to their campaigns
    Creator: Their submitted applications
    """
    try:
        applications = await campaign_service.get_applications(
            db, current_user, campaign_id, status, limit
        )
        
        return applications
        
    except Exception as e:
        logger.error(f"Error fetching applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applications"
        )


@router.post("/campaigns/{campaign_id}/apply")
@api_limit
async def apply_to_campaign(
    request: Request,
    response: Response,
    campaign_id: str,
    application_message: str,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Apply to a campaign as a creator."""
    if current_user.role != "creator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creators can apply to campaigns"
        )
    
    try:
        application = await campaign_service.apply_to_campaign(
            db, current_user, campaign_id, application_message
        )
        
        return {"success": True, "message": "Application submitted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application"
        )


@router.put("/applications/{application_id}/review")
@api_limit
async def review_application(
    request: Request,
    response: Response,
    application_id: str,
    review_data: ApplicationReviewRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Review a campaign application (approve/reject)."""
    if current_user.role not in ["agency", "brand"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agencies and brands can review applications"
        )
    
    try:
        application = await campaign_service.review_application(
            db, current_user, application_id, review_data
        )
        
        return {"success": True, "message": "Application reviewed successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error reviewing application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to review application"
        )


# =============================================================================
# DELIVERABLE MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/deliverables", response_model=List[DeliverableResponse])
@api_limit
async def get_deliverables(
    request: Request,
    response: Response,
    campaign_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get deliverables based on user role."""
    try:
        deliverables = await campaign_service.get_deliverables(
            db, current_user, campaign_id, status, limit
        )
        
        return deliverables
        
    except Exception as e:
        logger.error(f"Error fetching deliverables: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch deliverables"
        )


@router.post("/deliverables/{deliverable_id}/submit")
@api_limit
async def submit_content(
    request: Request,
    response: Response,
    deliverable_id: str,
    submission_data: ContentSubmissionRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Submit content for a deliverable."""
    if current_user.role != "creator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creators can submit content"
        )
    
    try:
        result = await campaign_service.submit_content(
            db, current_user, deliverable_id, submission_data
        )
        
        return {"success": True, "message": "Content submitted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit content"
        )


@router.put("/deliverables/{deliverable_id}/review")
@api_limit
async def review_content(
    request: Request,
    response: Response,
    deliverable_id: str,
    review_data: ContentReviewRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Review submitted content."""
    if current_user.role not in ["agency", "brand"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agencies and brands can review content"
        )
    
    try:
        result = await campaign_service.review_content(
            db, current_user, deliverable_id, review_data
        )
        
        return {"success": True, "message": "Content reviewed successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error reviewing content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to review content"
        )