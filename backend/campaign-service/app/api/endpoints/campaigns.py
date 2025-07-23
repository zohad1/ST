# app/api/endpoints/campaigns.py - Complete fixed version
from fastapi import APIRouter, Depends, status, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
import traceback
import uuid

from app.core.database import get_db
from app.core.security import verify_token
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    CampaignSegmentCreate, CampaignSegmentResponse,
    GMVBonusTierCreate, GMVBonusTierResponse,
    LeaderboardBonusCreate, LeaderboardBonusResponse
)
from app.services.campaign_service import CampaignService
from app.models.campaign import Campaign, CampaignApplication

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Define the list response model here if not in schemas
class CampaignListResponse:
    def __init__(self, campaigns: List[CampaignResponse], total: int, limit: int, offset: int):
        self.campaigns = campaigns
        self.total = total
        self.limit = limit
        self.offset = offset

# List campaigns endpoint
@router.get("/")
@router.get("")
async def list_campaigns(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    search: Optional[str] = None,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    List campaigns based on user role and filters
    """
    try:
        logger.info(f"Fetching campaigns for user {current_user.get('id', current_user.get('sub'))} with role {current_user['role']}")
        logger.info(f"Parameters - limit: {limit}, offset: {offset}, status: {status}, search: {search}")
        
        # Initialize service with database session
        service = CampaignService(db)
        
        user_id = current_user.get('id', current_user.get('sub'))
        
        # Get campaigns based on user role
        if current_user["role"] == "creator":
            # Show only active campaigns that creators can apply to
            response = service.get_available_campaigns(
                db=db,
                limit=limit,
                offset=offset,
                status=status or "active",
                search=search
            )
        else:
            # For agencies/brands, show their own campaigns
            response = service.get_campaigns_by_user(
                db=db,
                user_id=user_id,
                role=current_user["role"],
                limit=limit,
                offset=offset,
                status=status,
                search=search
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaigns"
        )

# Create campaign endpoint - with multiple decorators for trailing slash handling
@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate = Body(...),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new campaign"""
    try:
        logger.info(f"Creating campaign with data: {campaign_data}")
        
        # Only agencies can create campaigns
        if current_user["role"] not in ["agency", "brand", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only agencies and brands can create campaigns"
            )
        
        user_id = current_user.get('id', current_user.get('sub'))
        
        # Initialize service with database session
        service = CampaignService(db)
        
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            agency_id = UUID(user_id)
        else:
            agency_id = user_id
            
        new_campaign = service.create_new_campaign(
            campaign_data=campaign_data,
            agency_id=agency_id
        )
        
        return new_campaign
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

# Get specific campaign
@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get a specific campaign"""
    try:
        service = CampaignService(db)
        campaign = service.get_campaign_by_id(db, campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        user_id = current_user.get('id', current_user.get('sub'))
        
        # Check access permissions
        if current_user["role"] == "agency" and str(campaign.agency_id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this campaign"
            )
        
        return CampaignResponse.model_validate(campaign)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaign"
        )

# Update campaign
@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update a campaign"""
    try:
        service = CampaignService(db)
        
        # Check if user owns the campaign
        campaign = service.get_campaign_by_id(db, campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        user_id = current_user.get('id', current_user.get('sub'))
        
        if current_user["role"] == "agency" and str(campaign.agency_id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this campaign"
            )
        
        updated_campaign = service.update_campaign(
            campaign_id=UUID(campaign_id),
            campaign_update=campaign_update
        )
        
        return updated_campaign
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campaign"
        )

# Delete campaign
@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a campaign"""
    try:
        service = CampaignService(db)
        
        # Check if user owns the campaign
        campaign = service.get_campaign_by_id(db, campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        user_id = current_user.get('id', current_user.get('sub'))
        
        if current_user["role"] == "agency" and str(campaign.agency_id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this campaign"
            )
        
        # Only allow deletion of draft or cancelled campaigns
        if campaign.status not in ["draft", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or cancelled campaigns can be deleted"
            )
        
        success = service.delete_campaign(UUID(campaign_id))
        
        if success:
            return {"message": "Campaign deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete campaign"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign"
        )
# Add this debug version to your campaigns.py temporarily to see what's happening

@router.get("/my-campaigns-debug")
async def debug_my_campaigns(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Debug endpoint to check creator's campaign data"""
    try:
        from app.models.campaign import CampaignApplication, Campaign
        
        user_id = current_user.get("id", current_user.get("sub"))
        
        # Get ALL applications for this creator (not just approved)
        all_applications = db.query(CampaignApplication).filter(
            CampaignApplication.creator_id == user_id
        ).all()
        
        # Get approved applications
        approved_applications = db.query(CampaignApplication).filter(
            CampaignApplication.creator_id == user_id,
            CampaignApplication.status == "approved"
        ).all()
        
        return {
            "user_id": user_id,
            "role": current_user["role"],
            "total_applications": len(all_applications),
            "approved_applications": len(approved_applications),
            "application_statuses": [
                {
                    "id": str(app.id),
                    "campaign_id": str(app.campaign_id),
                    "status": app.status,
                    "applied_at": app.applied_at.isoformat() if app.applied_at else None
                }
                for app in all_applications
            ]
        }
        
    except Exception as e:
        logger.error(f"Debug error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "traceback": traceback.format_exc()}

# Campaign Segments
@router.post("/{campaign_id}/segments", response_model=CampaignSegmentResponse)
async def create_campaign_segment(
    campaign_id: str,
    segment: CampaignSegmentCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a campaign segment"""
    try:
        # Check permissions
        if current_user["role"] not in ["agency", "brand", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only agencies and brands can create segments"
            )
        
        service = CampaignService(db)
        return service.create_campaign_segment(UUID(campaign_id), segment)
        
    except Exception as e:
        logger.error(f"Error creating segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create segment: {str(e)}"
        )

@router.get("/{campaign_id}/segments", response_model=List[CampaignSegmentResponse])
async def get_campaign_segments(
    campaign_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get campaign segments"""
    try:
        service = CampaignService(db)
        return service.get_campaign_segments(UUID(campaign_id))
        
    except Exception as e:
        logger.error(f"Error fetching segments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch segments: {str(e)}"
        )

# GMV Bonus Tiers
@router.post("/{campaign_id}/bonus-tiers", response_model=GMVBonusTierResponse)
async def create_bonus_tier(
    campaign_id: str,
    bonus_tier: GMVBonusTierCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a GMV bonus tier"""
    try:
        if current_user["role"] not in ["agency", "brand", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only agencies and brands can create bonus tiers"
            )
        
        service = CampaignService(db)
        return service.create_gmv_bonus_tier(UUID(campaign_id), bonus_tier)
        
    except Exception as e:
        logger.error(f"Error creating bonus tier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bonus tier: {str(e)}"
        )

@router.get("/{campaign_id}/bonus-tiers", response_model=List[GMVBonusTierResponse])
async def get_bonus_tiers(
    campaign_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get GMV bonus tiers"""
    try:
        service = CampaignService(db)
        return service.get_gmv_bonus_tiers(UUID(campaign_id))
        
    except Exception as e:
        logger.error(f"Error fetching bonus tiers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bonus tiers: {str(e)}"
        )

# Test endpoint
@router.get("/test")
async def test_campaigns_endpoint():
    """Test endpoint to verify the campaigns router is loaded"""
    return {
        "message": "Campaigns router is working!",
        "endpoint": "/api/v1/campaigns",
        "service": "campaign-service",
        "status": "operational"
    }

# Log that the router was created successfully
logger.info("✅ Campaigns router created successfully with all endpoints")


# Add this test endpoint to your campaigns.py to verify POST is working

@router.post("/test-post")
async def test_post_endpoint(data: dict = Body(...)):
    """Test POST endpoint to verify router is working"""
    return {
        "message": "POST endpoint is working!",
        "received_data": data,
        "status": "success"
    }