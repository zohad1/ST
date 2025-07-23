# app/services/earnings_service.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from decimal import Decimal, ROUND_HALF_UP
import logging

from app.crud import creator_earnings as crud_earnings
from app.schemas.creator_earnings import CreatorEarningsCreate, CreatorEarningsUpdate
from app.models.creator_earnings import CreatorEarnings
from app.external.campaign_service_client import CampaignServiceClient
from app.utils.calculations import (
    calculate_gmv_commission,
    calculate_bonus_tier_amount,
    calculate_leaderboard_bonus,
    round_currency
)

logger = logging.getLogger(__name__)

class EarningsCalculationService:
    def __init__(self, db: Session):
        self.db = db
        self.campaign_client = CampaignServiceClient()

    async def calculate_creator_earnings(
        self, 
        creator_id: UUID, 
        campaign_id: UUID, 
        application_id: UUID,
        deliverables_completed: int = 0,
        gmv_generated: float = 0.0,
        force_recalculate: bool = False
    ) -> CreatorEarnings:
        """
        Calculate total earnings for a creator in a specific campaign
        """
        try:
            # Get existing earnings record or create new one
            existing_earnings = crud_earnings.get_by_application_id(self.db, application_id)
            
            if existing_earnings and not force_recalculate:
                # Update existing record
                await self._update_existing_earnings(
                    existing_earnings, deliverables_completed, gmv_generated
                )
                return existing_earnings
            
            # Get campaign details for calculation
            campaign_data = await self.campaign_client.get_campaign(campaign_id)
            if not campaign_data:
                raise ValueError(f"Campaign {campaign_id} not found")

            # Calculate all earnings components
            earnings_breakdown = await self._calculate_earnings_breakdown(
                campaign_data, deliverables_completed, gmv_generated, creator_id
            )

            if existing_earnings:
                # Update existing record
                update_data = CreatorEarningsUpdate(**earnings_breakdown)
                return crud_earnings.update(self.db, existing_earnings.id, update_data)
            else:
                # Create new earnings record
                earnings_data = CreatorEarningsCreate(
                    creator_id=creator_id,
                    campaign_id=campaign_id,
                    application_id=application_id,
                    **earnings_breakdown
                )
                return crud_earnings.create(self.db, earnings_data)

        except Exception as e:
            logger.error(f"Error calculating earnings for creator {creator_id}: {str(e)}")
            raise

    async def _calculate_earnings_breakdown(
        self, 
        campaign_data: Dict, 
        deliverables_completed: int, 
        gmv_generated: float,
        creator_id: UUID
    ) -> Dict[str, float]:
        """
        Calculate breakdown of different earning types
        """
        earnings = {
            "base_earnings": 0.0,
            "gmv_commission": 0.0,
            "bonus_earnings": 0.0,
            "referral_earnings": 0.0
        }

        # 1. Calculate base earnings (per deliverable)
        earnings["base_earnings"] = self._calculate_base_earnings(
            campaign_data, deliverables_completed
        )

        # 2. Calculate GMV commission
        earnings["gmv_commission"] = self._calculate_gmv_commission_earnings(
            campaign_data, gmv_generated
        )

        # 3. Calculate bonus earnings (tiers + leaderboard)
        earnings["bonus_earnings"] = await self._calculate_bonus_earnings(
            campaign_data, gmv_generated, creator_id
        )

        # 4. Calculate referral earnings
        earnings["referral_earnings"] = await self._calculate_referral_earnings(
            creator_id, campaign_data["id"]
        )

        return earnings

    def _calculate_base_earnings(self, campaign_data: Dict, deliverables_completed: int) -> float:
        """
        Calculate base earnings based on deliverables completed
        """
        payout_model = campaign_data.get("payout_model", "fixed_per_post")
        base_payout_per_post = float(campaign_data.get("base_payout_per_post", 0))
        
        if payout_model in ["fixed_per_post", "hybrid"]:
            return round_currency(base_payout_per_post * deliverables_completed)
        
        return 0.0

    def _calculate_gmv_commission_earnings(self, campaign_data: Dict, gmv_generated: float) -> float:
        """
        Calculate GMV commission earnings
        """
        payout_model = campaign_data.get("payout_model", "fixed_per_post")
        commission_rate = float(campaign_data.get("gmv_commission_rate", 0))
        
        if payout_model in ["gmv_commission", "hybrid", "retainer_gmv"] and commission_rate > 0:
            return calculate_gmv_commission(gmv_generated, commission_rate)
        
        return 0.0

    async def _calculate_bonus_earnings(
        self, 
        campaign_data: Dict, 
        gmv_generated: float, 
        creator_id: UUID
    ) -> float:
        """
        Calculate bonus earnings from tiers and leaderboards
        """
        total_bonus = 0.0

        # GMV bonus tiers
        gmv_bonus_tiers = campaign_data.get("gmv_bonus_tiers", [])
        tier_bonus = calculate_bonus_tier_amount(gmv_generated, gmv_bonus_tiers)
        total_bonus += tier_bonus

        # Leaderboard bonuses
        leaderboard_bonuses = campaign_data.get("leaderboard_bonuses", [])
        if leaderboard_bonuses:
            creator_position = await self._get_creator_leaderboard_position(
                creator_id, campaign_data["id"], gmv_generated
            )
            leaderboard_bonus = calculate_leaderboard_bonus(creator_position, leaderboard_bonuses)
            total_bonus += leaderboard_bonus

        return round_currency(total_bonus)

    async def _calculate_referral_earnings(self, creator_id: UUID, campaign_id: UUID) -> float:
        """
        Calculate referral earnings for this creator
        """
        # This would typically involve checking if this creator referred others
        # and calculating bonuses based on their performance
        # Implementation depends on referral system rules
        return 0.0

    async def _get_creator_leaderboard_position(
        self, 
        creator_id: UUID, 
        campaign_id: UUID, 
        current_gmv: float
    ) -> int:
        """
        Get creator's position in campaign leaderboard by GMV
        """
        try:
            # Get all creators' GMV for this campaign
            all_earnings = crud_earnings.get_by_campaign_id(self.db, campaign_id)
            
            # Create leaderboard sorted by GMV (assuming we track GMV in earnings)
            leaderboard = []
            for earning in all_earnings:
                # You might need to get actual GMV from TikTok Shop integration
                creator_gmv = await self._get_creator_gmv_for_campaign(
                    earning.creator_id, campaign_id
                )
                leaderboard.append((earning.creator_id, creator_gmv))
            
            # Add current creator if not in list yet
            if not any(creator[0] == creator_id for creator in leaderboard):
                leaderboard.append((creator_id, current_gmv))
            
            # Sort by GMV descending
            leaderboard.sort(key=lambda x: x[1], reverse=True)
            
            # Find position (1-indexed)
            for i, (c_id, _) in enumerate(leaderboard):
                if c_id == creator_id:
                    return i + 1
            
            return len(leaderboard) + 1  # Default to last position
            
        except Exception as e:
            logger.error(f"Error calculating leaderboard position: {str(e)}")
            return 999  # Default high position if error

    async def _get_creator_gmv_for_campaign(self, creator_id: UUID, campaign_id: UUID) -> float:
        """
        Get creator's actual GMV from TikTok Shop integration
        This would typically call the Integration Service
        """
        # Placeholder - this should call TikTok Shop API through Integration Service
        return 0.0

    async def _update_existing_earnings(
        self, 
        earnings: CreatorEarnings, 
        deliverables_completed: int, 
        gmv_generated: float
    ):
        """
        Update existing earnings record with new data
        """
        # Get campaign data for recalculation
        campaign_data = await self.campaign_client.get_campaign(earnings.campaign_id)
        
        # Recalculate earnings
        new_breakdown = await self._calculate_earnings_breakdown(
            campaign_data, deliverables_completed, gmv_generated, earnings.creator_id
        )
        
        # Update the record
        update_data = CreatorEarningsUpdate(**new_breakdown)
        crud_earnings.update(self.db, earnings.id, update_data)

    async def calculate_campaign_total_payouts(self, campaign_id: UUID) -> Dict[str, float]:
        """
        Calculate total payouts for entire campaign
        """
        all_earnings = crud_earnings.get_by_campaign_id(self.db, campaign_id)
        
        totals = {
            "total_base_earnings": 0.0,
            "total_gmv_commission": 0.0,
            "total_bonus_earnings": 0.0,
            "total_referral_earnings": 0.0,
            "total_earnings": 0.0,
            "total_paid": 0.0,
            "total_pending": 0.0
        }
        
        for earning in all_earnings:
            totals["total_base_earnings"] += float(earning.base_earnings)
            totals["total_gmv_commission"] += float(earning.gmv_commission)
            totals["total_bonus_earnings"] += float(earning.bonus_earnings)
            totals["total_referral_earnings"] += float(earning.referral_earnings)
            totals["total_earnings"] += earning.calculated_total_earnings
            totals["total_paid"] += float(earning.total_paid)
            totals["total_pending"] += earning.calculated_pending_payment
        
        return totals

    async def process_deliverable_completion(
        self, 
        creator_id: UUID, 
        campaign_id: UUID, 
        application_id: UUID
    ):
        """
        Process earnings when a deliverable is completed
        """
        try:
            # Get current deliverable count from Campaign Service
            deliverable_data = await self.campaign_client.get_creator_deliverables(
                application_id
            )
            completed_count = deliverable_data.get("completed_count", 0)
            
            # Get GMV data from Integration Service (placeholder)
            gmv_data = 0.0  # This should come from TikTok Shop integration
            
            # Calculate/update earnings
            await self.calculate_creator_earnings(
                creator_id, campaign_id, application_id, 
                completed_count, gmv_data, force_recalculate=True
            )
            
            logger.info(f"Processed deliverable completion for creator {creator_id} in campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error processing deliverable completion: {str(e)}")
            raise

    async def process_gmv_update(
        self, 
        creator_id: UUID, 
        campaign_id: UUID, 
        new_gmv_amount: float
    ):
        """
        Process earnings when GMV is updated from TikTok Shop
        """
        try:
            # Find the application_id for this creator/campaign
            earnings = crud_earnings.get_by_creator_and_campaign(
                self.db, creator_id, campaign_id
            )
            
            if not earnings:
                logger.warning(f"No earnings record found for creator {creator_id} in campaign {campaign_id}")
                return
            
            # Get current deliverable count
            deliverable_data = await self.campaign_client.get_creator_deliverables(
                earnings.application_id
            )
            completed_count = deliverable_data.get("completed_count", 0)
            
            # Recalculate earnings with new GMV
            await self.calculate_creator_earnings(
                creator_id, campaign_id, earnings.application_id,
                completed_count, new_gmv_amount, force_recalculate=True
            )
            
            logger.info(f"Processed GMV update for creator {creator_id}: ${new_gmv_amount}")
            
        except Exception as e:
            logger.error(f"Error processing GMV update: {str(e)}")
            raise

