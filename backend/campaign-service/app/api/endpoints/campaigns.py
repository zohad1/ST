# app/api/endpoints/campaigns.py - Complete async version
from fastapi import APIRouter, Depends, status, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
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
    db: AsyncSession = Depends(get_db)
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
            response = await service.get_available_campaigns(
                limit=limit,
                offset=offset,
                status=status or "active",
                search=search
            )
        else:
            # For agencies/brands, show their own campaigns
            response = await service.get_campaigns_by_user(
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
    db: AsyncSession = Depends(get_db)
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
            
        new_campaign = await service.create_new_campaign(
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
    db: AsyncSession = Depends(get_db)
):
    """Get a specific campaign"""
    try:
        service = CampaignService(db)
        
        campaign = await service.get_campaign_by_id(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
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
    db: AsyncSession = Depends(get_db)
):
    """Update a campaign"""
    try:
        if current_user["role"] not in ["agency", "brand", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only agencies and brands can update campaigns"
            )
        
        service = CampaignService(db)
        
        updated_campaign = await service.update_campaign(
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
    db: AsyncSession = Depends(get_db)
):
    """Delete a campaign"""
    try:
        if current_user["role"] not in ["agency", "brand", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only agencies and brands can delete campaigns"
            )
        
        service = CampaignService(db)
        
        success = await service.delete_campaign(UUID(campaign_id))
        
        if success:
            return {"message": "Campaign deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign"
        )

# Campaign segments endpoints
@router.post("/{campaign_id}/segments", response_model=CampaignSegmentResponse)
async def create_campaign_segment(
    campaign_id: str,
    segment_data: CampaignSegmentCreate,
    current_user: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Create a campaign segment"""
    try:
        service = CampaignService(db)
        
        segment = await service.create_campaign_segment(
            campaign_id=UUID(campaign_id),
            segment_data=segment_data
        )
        
        return segment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign segment"
        )

@router.get("/{campaign_id}/segments", response_model=List[CampaignSegmentResponse])
async def get_campaign_segments(
    campaign_id: str,
    current_user: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all segments for a campaign"""
    try:
        service = CampaignService(db)
        
        segments = await service.get_campaign_segments(UUID(campaign_id))
        
        return segments
        
    except Exception as e:
        logger.error(f"Error fetching segments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaign segments"
        )

# GMV bonus tiers endpoints
@router.post("/{campaign_id}/gmv-tiers", response_model=GMVBonusTierResponse)
async def create_gmv_bonus_tier(
    campaign_id: str,
    tier_data: GMVBonusTierCreate,
    current_user: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Create a GMV bonus tier"""
    try:
        service = CampaignService(db)
        
        tier = await service.create_gmv_bonus_tier(
            campaign_id=UUID(campaign_id),
            bonus_tier_data=tier_data
        )
        
        return tier
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating GMV tier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create GMV bonus tier"
        )

@router.get("/{campaign_id}/gmv-tiers", response_model=List[GMVBonusTierResponse])
async def get_gmv_bonus_tiers(
    campaign_id: str,
    current_user: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all GMV bonus tiers for a campaign"""
    try:
        service = CampaignService(db)
        
        tiers = await service.get_gmv_bonus_tiers(UUID(campaign_id))
        
        return tiers
        
    except Exception as e:
        logger.error(f"Error fetching GMV tiers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch GMV bonus tiers"
        )

# Leaderboard bonus endpoints
@router.post("/{campaign_id}/leaderboard-bonuses", response_model=LeaderboardBonusResponse)
async def create_leaderboard_bonus(
    campaign_id: str,
    bonus_data: LeaderboardBonusCreate,
    current_user: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Create a leaderboard bonus"""
    try:
        service = CampaignService(db)
        
        bonus = await service.create_leaderboard_bonus(
            campaign_id=UUID(campaign_id),
            leaderboard_data=bonus_data
        )
        
        return bonus
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating leaderboard bonus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create leaderboard bonus"
        )

@router.get("/{campaign_id}/leaderboard-bonuses", response_model=List[LeaderboardBonusResponse])
async def get_leaderboard_bonuses(
    campaign_id: str,
    current_user: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all leaderboard bonuses for a campaign"""
    try:
        service = CampaignService(db)
        
        bonuses = await service.get_leaderboard_bonuses(UUID(campaign_id))
        
        return bonuses
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard bonuses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leaderboard bonuses"
        )