
# app/services/schedule_service.py
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID
import logging
from datetime import datetime, timedelta

from app.crud import payment_schedule as crud_schedule, creator_earnings as crud_earnings
from app.schemas.payment_schedule import PaymentScheduleCreate, PaymentScheduleUpdate
from app.models.payment_schedule import PaymentSchedule
from app.external.campaign_service_client import CampaignServiceClient
from app.services.payment_service import PaymentProcessingService

logger = logging.getLogger(__name__)

class PaymentScheduleService:
    def __init__(self, db: Session):
        self.db = db
        self.campaign_client = CampaignServiceClient()

    async def create_schedule(self, schedule_data: PaymentScheduleCreate) -> PaymentSchedule:
        """Create a new payment schedule"""
        try:
            # Validate campaign exists
            campaign = await self.campaign_client.get_campaign(schedule_data.campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {schedule_data.campaign_id} not found")

            # Create schedule
            schedule = crud_schedule.create(self.db, schedule_data)
            
            logger.info(f"Created payment schedule {schedule.id} for campaign {schedule_data.campaign_id}")
            return schedule

        except Exception as e:
            logger.error(f"Error creating payment schedule: {str(e)}")
            raise

    async def execute_schedule(self, schedule_id: UUID) -> List[Dict]:
        """Execute a payment schedule manually"""
        try:
            schedule = crud_schedule.get(self.db, schedule_id)
            if not schedule:
                raise ValueError(f"Payment schedule {schedule_id} not found")

            # Get eligible creators
            eligible_creators = await self.get_eligible_creators(schedule.campaign_id)
            
            payment_service = PaymentProcessingService(self.db)
            created_payments = []

            for creator_data in eligible_creators:
                try:
                    # Process automatic payout for this creator
                    payment = await payment_service.process_automatic_payout(
                        creator_data["earning_id"]
                    )
                    
                    if payment:
                        created_payments.append({
                            "creator_id": creator_data["creator_id"],
                            "payment_id": payment.id,
                            "amount": float(payment.amount)
                        })

                except Exception as e:
                    logger.error(f"Error processing payout for creator {creator_data['creator_id']}: {str(e)}")

            logger.info(f"Executed schedule {schedule_id}, created {len(created_payments)} payments")
            return created_payments

        except Exception as e:
            logger.error(f"Error executing payment schedule: {str(e)}")
            raise

    async def get_eligible_creators(self, campaign_id: UUID) -> List[Dict]:
        """Get creators eligible for payout in a campaign"""
        try:
            # Get all earnings for the campaign
            campaign_earnings = crud_earnings.get_by_campaign_id(self.db, campaign_id)
            
            eligible_creators = []
            
            for earning in campaign_earnings:
                pending_amount = earning.calculated_pending_payment
                
                # Check if creator has pending payment above minimum threshold
                if pending_amount > 0:
                    # Get payment schedule for this campaign
                    schedules = crud_schedule.get_by_campaign_id(self.db, campaign_id)
                    min_payout = 0.0
                    
                    if schedules:
                        min_payout = float(schedules[0].minimum_payout_amount)
                    
                    if pending_amount >= min_payout:
                        eligible_creators.append({
                            "creator_id": earning.creator_id,
                            "earning_id": earning.id,
                            "pending_amount": pending_amount,
                            "total_earnings": earning.calculated_total_earnings
                        })
            
            return eligible_creators

        except Exception as e:
            logger.error(f"Error getting eligible creators: {str(e)}")
            return []

    async def should_trigger_payout(self, campaign_id: UUID, creator_id: UUID) -> bool:
        """Check if payout should be triggered based on schedule conditions"""
        try:
            schedules = crud_schedule.get_by_campaign_id(self.db, campaign_id)
            
            if not schedules:
                return False  # No schedule configured
            
            schedule = schedules[0]  # Use first schedule
            
            if not schedule.is_automated:
                return False  # Manual schedule only
            
            # Check deliverable completion trigger
            if schedule.trigger_on_deliverable_completion:
                deliverables = await self.campaign_client.get_creator_deliverables(
                    # Need application_id - would need to get from earnings
                    # This is a simplified check
                )
                # Check if deliverable was just completed
                return True  # Simplified for now
            
            # Check GMV milestone trigger
            if schedule.trigger_on_gmv_milestone and schedule.gmv_milestone_amount:
                # Check if creator reached GMV milestone
                # This would involve checking TikTok Shop integration data
                return True  # Simplified for now
            
            # Check campaign completion trigger
            if schedule.trigger_on_campaign_completion:
                campaign = await self.campaign_client.get_campaign(campaign_id)
                if campaign and campaign.get("status") == "completed":
                    return True
            
            return False

        except Exception as e:
            logger.error(f"Error checking payout trigger: {str(e)}")
            return False

    async def process_scheduled_payouts(self):
        """Process all automated payment schedules (called by background job)"""
        try:
            # Get all automated schedules
            automated_schedules = crud_schedule.get_automated_schedules(self.db)
            
            total_processed = 0
            
            for schedule in automated_schedules:
                try:
                    # Check if schedule should run
                    if await self._should_run_schedule(schedule):
                        payments = await self.execute_schedule(schedule.id)
                        total_processed += len(payments)
                        
                except Exception as e:
                    logger.error(f"Error processing schedule {schedule.id}: {str(e)}")
            
            logger.info(f"Processed {total_processed} scheduled payouts")
            return total_processed

        except Exception as e:
            logger.error(f"Error processing scheduled payouts: {str(e)}")
            return 0

    async def _should_run_schedule(self, schedule: PaymentSchedule) -> bool:
        """Check if a schedule should run based on timing and conditions"""
        # This would implement complex scheduling logic
        # For now, simplified to always return True for automated schedules
        return schedule.is_automated

