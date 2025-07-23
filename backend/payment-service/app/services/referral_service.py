
# app/services/referral_service.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from uuid import UUID
import logging
from datetime import datetime

from app.crud import referral as crud_referral
from app.schemas.referral import ReferralCreate, ReferralUpdate, ReferralStats
from app.models.referral import Referral
from app.external.user_service_client import UserServiceClient
from app.external.campaign_service_client import CampaignServiceClient

logger = logging.getLogger(__name__)

class ReferralService:
    def __init__(self, db: Session):
        self.db = db
        self.user_client = UserServiceClient()
        self.campaign_client = CampaignServiceClient()

    async def create_referral(self, referral_data: ReferralCreate) -> Referral:
        """Create a new referral"""
        try:
            # Validate users exist
            referrer = await self.user_client.get_user(referral_data.referrer_id)
            referred = await self.user_client.get_user(referral_data.referred_id)
            
            if not referrer:
                raise ValueError(f"Referrer {referral_data.referrer_id} not found")
            if not referred:
                raise ValueError(f"Referred user {referral_data.referred_id} not found")

            # Create referral
            referral = crud_referral.create(self.db, referral_data)
            
            # Generate referral code if not provided
            if not referral.referral_code:
                referral.generate_referral_code()
                self.db.commit()
                self.db.refresh(referral)

            logger.info(f"Created referral {referral.id} from {referral_data.referrer_id} to {referral_data.referred_id}")
            return referral

        except Exception as e:
            logger.error(f"Error creating referral: {str(e)}")
            raise

    async def generate_referral_code(self, creator_id: UUID, campaign_id: Optional[UUID] = None) -> str:
        """Generate a referral code for a creator"""
        try:
            # Check if referral already exists
            existing_referrals = crud_referral.get_by_referrer_and_campaign(
                self.db, creator_id, campaign_id
            ) if campaign_id else crud_referral.get_by_referrer_id(self.db, creator_id)

            # Generate new referral or return existing code
            if existing_referrals and campaign_id:
                return existing_referrals[0].referral_code

            # Create new referral record for code generation
            referral_data = ReferralCreate(
                referrer_id=creator_id,
                referred_id=creator_id,  # Temporary, will be updated when someone uses the code
                campaign_id=campaign_id
            )
            
            # This is a placeholder referral just for code generation
            # In practice, you might want a separate table for referral codes
            temp_referral = Referral(**referral_data.model_dump())
            code = temp_referral.generate_referral_code()
            
            return code

        except Exception as e:
            logger.error(f"Error generating referral code: {str(e)}")
            raise

    async def process_referral_signup(self, referral_code: str, referred_user_id: UUID) -> Dict:
        """Process a referral when someone signs up with a referral code"""
        try:
            # Find referral by code
            referral = crud_referral.get_by_referral_code(self.db, referral_code)
            if not referral:
                raise ValueError(f"Invalid referral code: {referral_code}")

            # Update referral with actual referred user
            crud_referral.update(
                self.db, referral.id,
                ReferralUpdate(referred_id=referred_user_id)
            )

            # Calculate initial referral bonus if applicable
            bonus_amount = await self._calculate_signup_bonus(referral)
            if bonus_amount > 0:
                crud_referral.update(
                    self.db, referral.id,
                    ReferralUpdate(bonus_earned=bonus_amount)
                )

            logger.info(f"Processed referral signup for code {referral_code}")
            return {
                "referral_id": referral.id,
                "bonus_amount": bonus_amount,
                "referrer_id": referral.referrer_id
            }

        except Exception as e:
            logger.error(f"Error processing referral signup: {str(e)}")
            raise

    async def calculate_and_assign_bonus(self, referral_id: UUID) -> float:
        """Calculate and assign referral bonus based on referred user's performance"""
        try:
            referral = crud_referral.get(self.db, referral_id)
            if not referral:
                raise ValueError(f"Referral {referral_id} not found")

            # Calculate bonus based on referred user's earnings
            bonus_amount = await self._calculate_performance_bonus(referral)
            
            if bonus_amount > 0:
                current_bonus = float(referral.bonus_earned)
                new_bonus = current_bonus + bonus_amount
                
                crud_referral.update(
                    self.db, referral_id,
                    ReferralUpdate(bonus_earned=new_bonus)
                )

            return bonus_amount

        except Exception as e:
            logger.error(f"Error calculating referral bonus: {str(e)}")
            raise

    async def get_referral_stats(self, creator_id: UUID) -> ReferralStats:
        """Get referral statistics for a creator"""
        try:
            referrals = crud_referral.get_by_referrer_id(self.db, creator_id)
            
            total_referrals = len(referrals)
            successful_referrals = len([r for r in referrals if r.first_campaign_joined_at])
            total_bonus_earned = sum(float(r.bonus_earned) for r in referrals)
            total_bonus_paid = sum(float(r.bonus_paid) for r in referrals)
            pending_bonus = total_bonus_earned - total_bonus_paid

            return ReferralStats(
                referrer_id=creator_id,
                total_referrals=total_referrals,
                successful_referrals=successful_referrals,
                total_bonus_earned=total_bonus_earned,
                total_bonus_paid=total_bonus_paid,
                pending_bonus=pending_bonus
            )

        except Exception as e:
            logger.error(f"Error getting referral stats: {str(e)}")
            raise

    async def _calculate_signup_bonus(self, referral: Referral) -> float:
        """Calculate bonus for successful referral signup"""
        # This could be configured per campaign or globally
        # For now, return a fixed amount
        return 5.00  # $5 signup bonus

    async def _calculate_performance_bonus(self, referral: Referral) -> float:
        """Calculate bonus based on referred user's performance"""
        try:
            # Get referred user's earnings
            from app.crud import creator_earnings as crud_earnings
            referred_earnings = crud_earnings.get_by_creator_id(
                self.db, referral.referred_id
            )

            if not referred_earnings:
                return 0.0

            # Calculate percentage of referred user's earnings
            total_earnings = sum(e.calculated_total_earnings for e in referred_earnings)
            bonus_rate = 0.05  # 5% of referred user's earnings
            
            return total_earnings * bonus_rate

        except Exception as e:
            logger.error(f"Error calculating performance bonus: {str(e)}")
            return 0.0

