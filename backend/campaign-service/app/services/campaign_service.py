# app/services/campaign_service.py - Async version with proper async patterns
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, select, cast, String
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
from fastapi import HTTPException, status

from app.models.user import User
from app.models.campaign import (
    Campaign, CampaignApplication, Deliverable, 
    CampaignStatus, ApplicationStatus, DeliverableStatus,
    PayoutModel, TrackingMethod
)

from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    CampaignListResponse,  # ADD THIS LINE
    CampaignSegmentCreate, CampaignSegmentResponse,
    GMVBonusTierCreate, GMVBonusTierResponse,
    LeaderboardBonusCreate, LeaderboardBonusResponse
)

from app.crud import campaign as crud_campaign

logger = logging.getLogger(__name__)


class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_new_campaign(self, campaign_data: CampaignCreate, agency_id: uuid.UUID) -> CampaignResponse:
        """Create a new campaign with proper validation and error handling"""
        try:
            logger.info(f"Creating campaign with data: {campaign_data}")
            
            # Convert the Pydantic model to dict
            campaign_dict = campaign_data.model_dump()
            
            # Additional cleaning for database
            # Handle JSONB field
            if 'tiktok_product_links' in campaign_dict:
                links = campaign_dict['tiktok_product_links']
                if links is None or links == [] or links == ['']:
                    campaign_dict['tiktok_product_links'] = None
            
            # Ensure numeric fields are proper float/Decimal for database
            numeric_fields = [
                'budget', 'total_budget', 'base_payout_per_post', 
                'gmv_commission_rate', 'retainer_amount', 'target_gmv',
                'current_gmv', 'spent_amount', 'referral_bonus_amount'
            ]
            for field in numeric_fields:
                if field in campaign_dict and campaign_dict[field] is not None:
                    campaign_dict[field] = float(campaign_dict[field])
            
            # Set defaults for required numeric fields
            campaign_dict.setdefault('spent_amount', 0.0)
            campaign_dict.setdefault('current_gmv', 0.0)
            campaign_dict.setdefault('current_posts', 0)
            campaign_dict.setdefault('current_creators', 0)
            campaign_dict.setdefault('total_views', 0)
            campaign_dict.setdefault('total_engagement', 0)
            
            # Ensure status is set
            campaign_dict.setdefault('status', 'draft')
            
            # Handle dates
            date_fields = ['start_date', 'end_date']
            for field in date_fields:
                if field in campaign_dict and isinstance(campaign_dict[field], str):
                    try:
                        campaign_dict[field] = datetime.fromisoformat(campaign_dict[field].replace('Z', '+00:00'))
                    except:
                        campaign_dict[field] = None
            
            # Ensure agency_id is a UUID
            if isinstance(agency_id, str):
                agency_id = uuid.UUID(agency_id)
            
            logger.info(f"Processed campaign dict: {campaign_dict}")
            
            # Create campaign using SQLAlchemy model
            db_campaign = Campaign(**campaign_dict, agency_id=agency_id)
            
            # Add to session and commit
            self.db.add(db_campaign)
            await self.db.commit()
            await self.db.refresh(db_campaign)
            
            logger.info(f"Campaign created successfully with ID: {db_campaign.id}")
            
            return CampaignResponse.model_validate(db_campaign)
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create campaign: {str(e)}"
            )

    async def get_all_campaigns(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        agency_id: Optional[uuid.UUID] = None,
        brand_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None
    ) -> List[CampaignResponse]:
        """Get campaigns with filtering"""
        try:
            campaigns = await crud_campaign.get_campaigns(
                self.db, 
                skip=skip, 
                limit=limit, 
                agency_id=agency_id,
                brand_id=brand_id,
                status_filter=status_filter
            )
            
            return [CampaignResponse.model_validate(campaign) for campaign in campaigns]
            
        except Exception as e:
            logger.error(f"Error fetching campaigns: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch campaigns: {str(e)}"
            )

    async def get_campaign_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID"""
        result = await self.db.execute(select(Campaign).where(Campaign.id == campaign_id))
        return result.scalar_one_or_none()

    async def update_campaign(self, campaign_id: uuid.UUID, campaign_update: CampaignUpdate) -> CampaignResponse:
        """Update a campaign"""
        try:
            # Check if campaign exists
            existing_campaign = await crud_campaign.get_campaign(self.db, campaign_id)
            if not existing_campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found"
                )
            
            # Update campaign
            updated_campaign = await crud_campaign.update_campaign(self.db, campaign_id, campaign_update)
            
            return CampaignResponse.model_validate(updated_campaign)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update campaign: {str(e)}"
            )

    async def delete_campaign(self, campaign_id: uuid.UUID) -> bool:
        """Delete a campaign"""
        try:
            campaign = await crud_campaign.get_campaign(self.db, campaign_id)
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found"
                )
            
            # Check if campaign can be deleted (no active applications, etc.)
            result = await self.db.execute(
                select(func.count()).select_from(CampaignApplication).where(
                    and_(
                        CampaignApplication.campaign_id == campaign_id,
                        cast(CampaignApplication.status, String) == "approved"
                    )
                )
            )
            active_applications = result.scalar()
            
            if active_applications > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete campaign with active applications"
                )
            
            deleted_campaign = await crud_campaign.delete_campaign(self.db, campaign_id)
            return deleted_campaign is not None
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete campaign: {str(e)}"
            )

    async def get_available_campaigns(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = "active",
        search: Optional[str] = None
    ) -> CampaignListResponse:
        """Get campaigns available for creators to apply to"""
        try:
            query = select(Campaign)
            
            # Filter by status
            if status:
                query = query.where(cast(Campaign.status, String) == status)
            
            # Filter campaigns that still have room for creators
            query = query.where(
                or_(
                    Campaign.max_creators.is_(None),
                    Campaign.current_creators < Campaign.max_creators
                )
            )
            
            # Search filter
            if search:
                query = query.where(
                    or_(
                        Campaign.name.ilike(f"%{search}%"),
                        Campaign.description.ilike(f"%{search}%"),
                        Campaign.hashtag.ilike(f"%{search}%")
                    )
                )
            
            # Get total count - use direct count query to avoid subquery issues
            count_conditions = []
            if status:
                count_conditions.append(cast(Campaign.status, String) == status)
            
            count_conditions.append(
                or_(
                    Campaign.max_creators.is_(None),
                    Campaign.current_creators < Campaign.max_creators
                )
            )
            
            if search:
                count_conditions.append(
                    or_(
                        Campaign.name.ilike(f"%{search}%"),
                        Campaign.description.ilike(f"%{search}%"),
                        Campaign.hashtag.ilike(f"%{search}%")
                    )
                )
            
            count_query = select(func.count(Campaign.id)).where(and_(*count_conditions))
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            paginated_query = query.offset(offset).limit(limit)
            result = await self.db.execute(paginated_query)
            campaigns = result.scalars().all()
            
            return CampaignListResponse(
                campaigns=campaigns,
                total=total,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logger.error(f"Error fetching available campaigns: {str(e)}")
            raise

    async def create_campaign_segment(self, campaign_id: uuid.UUID, segment_data: CampaignSegmentCreate) -> CampaignSegmentResponse:
        """Create a campaign segment"""
        try:
            # Verify campaign exists
            campaign = await crud_campaign.get_campaign(self.db, campaign_id)
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found"
                )
            
            segment = await crud_campaign.create_campaign_segment(self.db, segment_data, campaign_id)
            return CampaignSegmentResponse.model_validate(segment)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating campaign segment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create campaign segment: {str(e)}"
            )

    async def get_campaign_segments(self, campaign_id: uuid.UUID) -> List[CampaignSegmentResponse]:
        """Get all segments for a campaign"""
        try:
            segments = await crud_campaign.get_campaign_segments(self.db, campaign_id)
            return [CampaignSegmentResponse.model_validate(segment) for segment in segments]
        except Exception as e:
            logger.error(f"Error fetching segments: {str(e)}")
            raise

    async def create_gmv_bonus_tier(self, campaign_id: uuid.UUID, bonus_tier_data: GMVBonusTierCreate) -> GMVBonusTierResponse:
        """Create a GMV bonus tier"""
        try:
            # Verify campaign exists
            campaign = await crud_campaign.get_campaign(self.db, campaign_id)
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found"
                )
            
            bonus_tier = await crud_campaign.create_gmv_bonus_tier(self.db, bonus_tier_data, campaign_id)
            return GMVBonusTierResponse.model_validate(bonus_tier)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating GMV bonus tier: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create GMV bonus tier: {str(e)}"
            )

    async def get_gmv_bonus_tiers(self, campaign_id: uuid.UUID) -> List[GMVBonusTierResponse]:
        """Get all GMV bonus tiers for a campaign"""
        try:
            tiers = await crud_campaign.get_gmv_bonus_tiers(self.db, campaign_id)
            return [GMVBonusTierResponse.model_validate(tier) for tier in tiers]
        except Exception as e:
            logger.error(f"Error fetching bonus tiers: {str(e)}")
            raise

    async def create_leaderboard_bonus(self, campaign_id: uuid.UUID, leaderboard_data: LeaderboardBonusCreate) -> LeaderboardBonusResponse:
        """Create a leaderboard bonus"""
        try:
            # Verify campaign exists
            campaign = await crud_campaign.get_campaign(self.db, campaign_id)
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found"
                )
            
            leaderboard_bonus = await crud_campaign.create_leaderboard_bonus(self.db, leaderboard_data, campaign_id)
            return LeaderboardBonusResponse.model_validate(leaderboard_bonus)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating leaderboard bonus: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create leaderboard bonus: {str(e)}"
            )

    async def get_leaderboard_bonuses(self, campaign_id: uuid.UUID) -> List[LeaderboardBonusResponse]:
        """Get all leaderboard bonuses for a campaign"""
        try:
            bonuses = await crud_campaign.get_leaderboard_bonuses(self.db, campaign_id)
            return [LeaderboardBonusResponse.model_validate(bonus) for bonus in bonuses]
        except Exception as e:
            logger.error(f"Error fetching leaderboard bonuses: {str(e)}")
            raise
    
    async def get_campaigns_by_user(
        self,
        user_id: str,
        role: str,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> CampaignListResponse:
        """Get campaigns for a specific user based on their role"""
        try:
            query = select(Campaign)
            
            # Filter by role
            if role == "agency":
                query = query.where(Campaign.agency_id == user_id)
            elif role == "brand":
                query = query.where(Campaign.brand_id == user_id)
            
            # Filter by status
            if status:
                query = query.where(cast(Campaign.status, String) == status)
            
            # Search filter
            if search:
                query = query.where(
                    or_(
                        Campaign.name.ilike(f"%{search}%"),
                        Campaign.description.ilike(f"%{search}%"),
                        Campaign.hashtag.ilike(f"%{search}%")
                    )
                )
            
            # Get total count - use direct count query to avoid subquery issues
            count_conditions = []
            
            # Add role filter to count
            if role == "agency":
                count_conditions.append(Campaign.agency_id == user_id)
            elif role == "brand":
                count_conditions.append(Campaign.brand_id == user_id)
            
            # Add status filter to count
            if status:
                count_conditions.append(cast(Campaign.status, String) == status)
            
            # Add search filter to count
            if search:
                count_conditions.append(
                    or_(
                        Campaign.name.ilike(f"%{search}%"),
                        Campaign.description.ilike(f"%{search}%"),
                        Campaign.hashtag.ilike(f"%{search}%")
                    )
                )
            
            count_query = select(func.count(Campaign.id)).where(and_(*count_conditions)) if count_conditions else select(func.count(Campaign.id))
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            paginated_query = query.offset(offset).limit(limit)
            result = await self.db.execute(paginated_query)
            campaigns = result.scalars().all()
            
            return CampaignListResponse(
                campaigns=campaigns,
                total=total,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logger.error(f"Error fetching campaigns by user: {str(e)}")
            raise

