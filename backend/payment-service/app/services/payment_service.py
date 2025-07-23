# app/services/payment_service.py
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
from uuid import UUID
import logging
from datetime import datetime, timedelta

from app.crud import payment as crud_payment, creator_earnings as crud_earnings
from app.schemas.payment import PaymentCreate, PaymentUpdate, BulkPaymentCreate
from app.models.standalone_models import Payment  # Updated import
from app.models.payment_enums import PaymentStatus, PaymentType, PayoutMethod
from app.external.stripe_client import StripeClient
from app.external.fanbasis_client import FanbasisClient
from app.external.user_service_client import UserServiceClient
from app.external.campaign_service_client import CampaignServiceClient
from app.core.exceptions import PaymentProcessingError, InsufficientFundsError
from app.utils.calculations import round_currency

logger = logging.getLogger(__name__)

class PaymentProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.stripe_client = StripeClient()
        self.fanbasis_client = FanbasisClient()
        self.user_client = UserServiceClient()
        self.campaign_client = CampaignServiceClient()

    async def create_manual_payment(self, payment_data: PaymentCreate) -> Payment:
        """Create a manual payment initiated by agency/admin"""
        try:
            # Validate creator exists
            creator = await self.user_client.get_user(payment_data.creator_id)
            if not creator:
                raise ValueError(f"Creator {payment_data.creator_id} not found")

            # Validate campaign if provided
            if payment_data.campaign_id:
                campaign = await self.campaign_client.get_campaign(payment_data.campaign_id)
                if not campaign:
                    raise ValueError(f"Campaign {payment_data.campaign_id} not found")

            # Create payment record
            payment = crud_payment.create(self.db, payment_data)
            
            logger.info(f"Created manual payment {payment.id} for creator {payment_data.creator_id}")
            return payment

        except Exception as e:
            logger.error(f"Error creating manual payment: {str(e)}")
            raise PaymentProcessingError(f"Failed to create payment: {str(e)}")

    async def create_bulk_payments(self, bulk_data: BulkPaymentCreate) -> List[Payment]:
        """Create multiple payments at once"""
        payments = []
        
        try:
            # Validate all creators exist
            creators = await self.user_client.get_users_batch(bulk_data.creator_ids)
            
            for creator_id in bulk_data.creator_ids:
                if creator_id not in creators:
                    raise ValueError(f"Creator {creator_id} not found")
                
                payment_data = PaymentCreate(
                    creator_id=creator_id,
                    amount=bulk_data.amount_per_creator,
                    payment_type=bulk_data.payment_type,
                    payment_method=bulk_data.payment_method,
                    description=bulk_data.description
                )
                
                payment = crud_payment.create(self.db, payment_data)
                payments.append(payment)
            
            logger.info(f"Created {len(payments)} bulk payments")
            return payments

        except Exception as e:
            logger.error(f"Error creating bulk payments: {str(e)}")
            raise PaymentProcessingError(f"Failed to create bulk payments: {str(e)}")

    async def process_payment_async(self, payment_id: UUID):
        """Process payment asynchronously"""
        try:
            payment = crud_payment.get(self.db, payment_id)
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            if payment.status != PaymentStatus.pending:
                logger.warning(f"Payment {payment_id} is not pending, skipping processing")
                return

            # Update status to processing
            crud_payment.update(
                self.db, payment_id, 
                PaymentUpdate(status=PaymentStatus.processing, processed_at=datetime.now())
            )

            # Process based on payment method
            if payment.payment_method == PayoutMethod.stripe:
                await self._process_stripe_payment(payment)
            elif payment.payment_method == PayoutMethod.fanbasis:
                await self._process_fanbasis_payment(payment)
            elif payment.payment_method == PayoutMethod.manual:
                await self._process_manual_payment(payment)
            else:
                raise ValueError(f"Unsupported payment method: {payment.payment_method}")

        except Exception as e:
            logger.error(f"Error processing payment {payment_id}: {str(e)}")
            # Mark payment as failed
            crud_payment.update(
                self.db, payment_id,
                PaymentUpdate(
                    status=PaymentStatus.failed,
                    failure_reason=str(e),
                    failed_at=datetime.now()
                )
            )

    async def _process_stripe_payment(self, payment: Payment):
        """Process payment through Stripe"""
        try:
            # Get creator details for payment
            creator = await self.user_client.get_creator_details(UUID(payment.creator_id))
            if not creator:
                raise ValueError("Creator details not found")

            # Create Stripe payment intent
            stripe_result = await self.stripe_client.create_payment_intent(
                amount=float(payment.amount),
                creator_id=UUID(payment.creator_id),
                description=payment.description,
                metadata={
                    "payment_id": str(payment.id),
                    "campaign_id": str(payment.campaign_id) if payment.campaign_id else None
                }
            )

            # Update payment with Stripe details
            crud_payment.update(
                self.db, payment.id,
                PaymentUpdate(
                    stripe_payment_intent_id=stripe_result["payment_intent_id"],
                    external_transaction_id=stripe_result["payment_intent_id"]
                )
            )

            # For automatic confirmation, mark as completed
            # In real implementation, this would be handled by webhooks
            if stripe_result["status"] == "succeeded":
                await self._complete_payment(payment.id)

        except Exception as e:
            raise PaymentProcessingError(f"Stripe processing failed: {str(e)}")

    async def _process_fanbasis_payment(self, payment: Payment):
        """Process payment through Fanbasis"""
        try:
            # Get creator details
            creator = await self.user_client.get_creator_details(UUID(payment.creator_id))
            if not creator:
                raise ValueError("Creator details not found")

            # Create Fanbasis payout
            fanbasis_result = await self.fanbasis_client.create_payout(
                amount=float(payment.amount),
                creator_id=UUID(payment.creator_id),
                creator_email=creator["email"],
                description=payment.description,
                metadata={
                    "payment_id": str(payment.id),
                    "campaign_id": str(payment.campaign_id) if payment.campaign_id else None
                }
            )

            # Update payment with Fanbasis details
            crud_payment.update(
                self.db, payment.id,
                PaymentUpdate(
                    fanbasis_transaction_id=fanbasis_result["transaction_id"],
                    external_transaction_id=fanbasis_result["transaction_id"]
                )
            )

            # Mark as completed if successful
            if fanbasis_result["status"] == "completed":
                await self._complete_payment(payment.id)

        except Exception as e:
            raise PaymentProcessingError(f"Fanbasis processing failed: {str(e)}")

    async def _process_manual_payment(self, payment: Payment):
        """Process manual payment (requires manual confirmation)"""
        # For manual payments, just mark as completed
        # In real scenarios, this might require additional approval steps
        await self._complete_payment(payment.id)

    async def _complete_payment(self, payment_id: UUID):
        """Mark payment as completed and update related records"""
        try:
            payment = crud_payment.get(self.db, payment_id)
            if not payment:
                return

            # Mark payment as completed
            crud_payment.update(
                self.db, payment_id,
                PaymentUpdate(
                    status=PaymentStatus.completed,
                    completed_at=datetime.now()
                )
            )

            # Update earnings record if linked
            if payment.earning_id:
                earning = crud_earnings.get(self.db, payment.earning_id)
                if earning:
                    new_total_paid = float(earning.total_paid) + float(payment.amount)
                    crud_earnings.update(
                        self.db, earning.id,
                        {"total_paid": round_currency(new_total_paid)}
                    )

            # Update campaign spent amount
            if payment.campaign_id:
                await self.campaign_client.update_campaign_spent_amount(
                    UUID(payment.campaign_id), float(payment.amount)
                )

            logger.info(f"Payment {payment_id} completed successfully")

        except Exception as e:
            logger.error(f"Error completing payment {payment_id}: {str(e)}")

    async def cancel_payment(self, payment_id: UUID) -> Dict[str, Any]:
        """Cancel a pending payment"""
        try:
            payment = crud_payment.get(self.db, payment_id)
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            if payment.status not in [PaymentStatus.pending, PaymentStatus.processing]:
                raise ValueError(f"Cannot cancel payment with status: {payment.status}")

            # Cancel with external provider if applicable
            result = {"cancelled": True}
            
            if payment.stripe_payment_intent_id:
                # Cancel Stripe payment intent if possible
                try:
                    stripe_result = await self.stripe_client.cancel_payment(
                        payment.stripe_payment_intent_id
                    )
                    result["stripe_result"] = stripe_result
                except Exception as e:
                    logger.warning(f"Could not cancel Stripe payment: {str(e)}")

            elif payment.fanbasis_transaction_id:
                # Cancel Fanbasis payout if possible
                try:
                    fanbasis_result = await self.fanbasis_client.cancel_payout(
                        payment.fanbasis_transaction_id
                    )
                    result["fanbasis_result"] = fanbasis_result
                except Exception as e:
                    logger.warning(f"Could not cancel Fanbasis payout: {str(e)}")

            # Update payment status
            crud_payment.update(
                self.db, payment_id,
                PaymentUpdate(status=PaymentStatus.cancelled)
            )

            return result

        except Exception as e:
            logger.error(f"Error cancelling payment {payment_id}: {str(e)}")
            raise PaymentProcessingError(f"Failed to cancel payment: {str(e)}")

    async def process_automatic_payout(self, earning_id: UUID) -> Optional[Payment]:
        """Process automatic payout based on earnings"""
        try:
            earning = crud_earnings.get(self.db, earning_id)
            if not earning:
                return None

            pending_amount = earning.calculated_pending_payment
            if pending_amount <= 0:
                return None

            # Check if there's a payment schedule for this campaign
            from app.services.schedule_service import PaymentScheduleService
            schedule_service = PaymentScheduleService(self.db)
            
            should_payout = await schedule_service.should_trigger_payout(
                UUID(earning.campaign_id), UUID(earning.creator_id)
            )
            
            if not should_payout:
                return None

            # Create automatic payment
            payment_data = PaymentCreate(
                creator_id=UUID(earning.creator_id),
                campaign_id=UUID(earning.campaign_id) if earning.campaign_id else None,
                earning_id=earning.id,
                amount=pending_amount,
                payment_type=PaymentType.base_payout,  # Default type
                payment_method=PayoutMethod.stripe,  # Default method
                description=f"Automatic payout for campaign {earning.campaign_id}"
            )

            payment = crud_payment.create(self.db, payment_data)
            
            # Process payment asynchronously
            await self.process_payment_async(payment.id)
            
            return payment

        except Exception as e:
            logger.error(f"Error processing automatic payout: {str(e)}")
            return None