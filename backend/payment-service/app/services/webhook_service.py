# app/services/webhook_service.py
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime  # Added missing import
import logging

from app.crud import payment as crud_payment
from app.schemas.webhook import WebhookProcessingResult, StripeWebhookPayload, FanbasisWebhookPayload
from app.schemas.payment import PaymentUpdate
from app.models.payment_enums import PaymentStatus
from app.external.campaign_service_client import CampaignServiceClient

logger = logging.getLogger(__name__)

class WebhookProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.campaign_client = CampaignServiceClient()

    async def process_stripe_webhook(self, event: Dict[str, Any]) -> WebhookProcessingResult:
        """Process Stripe webhook events"""
        try:
            event_type = event.get("type")
            event_data = event.get("data", {}).get("object", {})
            
            logger.info(f"Processing Stripe webhook: {event_type}")
            
            if event_type == "payment_intent.succeeded":
                return await self._handle_stripe_payment_success(event_data)
            elif event_type == "payment_intent.payment_failed":
                return await self._handle_stripe_payment_failed(event_data)
            elif event_type == "payment_intent.canceled":
                return await self._handle_stripe_payment_canceled(event_data)
            elif event_type == "transfer.created":
                return await self._handle_stripe_transfer_created(event_data)
            else:
                logger.info(f"Unhandled Stripe event type: {event_type}")
                return WebhookProcessingResult(
                    success=True,
                    message=f"Event type {event_type} acknowledged but not processed"
                )

        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {str(e)}")
            return WebhookProcessingResult(
                success=False,
                message=f"Webhook processing failed: {str(e)}",
                error_details={"error": str(e), "event_type": event.get("type")}
            )

    async def _handle_stripe_payment_success(self, payment_intent: Dict) -> WebhookProcessingResult:
        """Handle successful Stripe payment"""
        try:
            payment_intent_id = payment_intent.get("id")
            
            # Find payment by Stripe ID
            payment = crud_payment.get_by_external_id(self.db, payment_intent_id, "stripe")
            if not payment:
                return WebhookProcessingResult(
                    success=False,
                    message=f"Payment not found for Stripe ID: {payment_intent_id}"
                )

            # Update payment status
            crud_payment.update(
                self.db, payment.id,
                PaymentUpdate(
                    status=PaymentStatus.completed,
                    completed_at=datetime.now()
                )
            )

            # Update earnings and campaign spent amount
            await self._update_payment_completion(payment)

            return WebhookProcessingResult(
                success=True,
                message="Payment marked as completed",
                payment_id=payment.id
            )

        except Exception as e:
            logger.error(f"Error handling Stripe payment success: {str(e)}")
            raise

    async def _handle_stripe_payment_failed(self, payment_intent: Dict) -> WebhookProcessingResult:
        """Handle failed Stripe payment"""
        try:
            payment_intent_id = payment_intent.get("id")
            failure_reason = payment_intent.get("last_payment_error", {}).get("message", "Unknown error")
            
            # Find payment by Stripe ID
            payment = crud_payment.get_by_external_id(self.db, payment_intent_id, "stripe")
            if not payment:
                return WebhookProcessingResult(
                    success=False,
                    message=f"Payment not found for Stripe ID: {payment_intent_id}"
                )

            # Update payment status
            crud_payment.update(
                self.db, payment.id,
                PaymentUpdate(
                    status=PaymentStatus.failed,
                    failure_reason=failure_reason,
                    failed_at=datetime.now()
                )
            )

            return WebhookProcessingResult(
                success=True,
                message="Payment marked as failed",
                payment_id=payment.id
            )

        except Exception as e:
            logger.error(f"Error handling Stripe payment failure: {str(e)}")
            raise

    async def _handle_stripe_payment_canceled(self, payment_intent: Dict) -> WebhookProcessingResult:
        """Handle canceled Stripe payment"""
        try:
            payment_intent_id = payment_intent.get("id")
            
            # Find payment by Stripe ID
            payment = crud_payment.get_by_external_id(self.db, payment_intent_id, "stripe")
            if not payment:
                return WebhookProcessingResult(
                    success=False,
                    message=f"Payment not found for Stripe ID: {payment_intent_id}"
                )

            # Update payment status
            crud_payment.update(
                self.db, payment.id,
                PaymentUpdate(status=PaymentStatus.cancelled)
            )

            return WebhookProcessingResult(
                success=True,
                message="Payment marked as cancelled",
                payment_id=payment.id
            )

        except Exception as e:
            logger.error(f"Error handling Stripe payment cancellation: {str(e)}")
            raise

    async def _handle_stripe_transfer_created(self, transfer: Dict) -> WebhookProcessingResult:
        """Handle Stripe transfer creation"""
        # This would handle direct transfers to creator accounts
        # Implementation depends on specific Stripe setup
        return WebhookProcessingResult(
            success=True,
            message="Transfer event processed"
        )

    async def process_fanbasis_webhook(self, webhook_data: Dict[str, Any]) -> WebhookProcessingResult:
        """Process Fanbasis webhook events"""
        try:
            transaction_id = webhook_data.get("transaction_id")
            status = webhook_data.get("status")
            
            logger.info(f"Processing Fanbasis webhook: {status} for {transaction_id}")
            
            # Find payment by Fanbasis ID
            payment = crud_payment.get_by_external_id(self.db, transaction_id, "fanbasis")
            if not payment:
                return WebhookProcessingResult(
                    success=False,
                    message=f"Payment not found for Fanbasis ID: {transaction_id}"
                )

            # Update payment based on status
            if status == "completed":
                crud_payment.update(
                    self.db, payment.id,
                    PaymentUpdate(
                        status=PaymentStatus.completed,
                        completed_at=datetime.now()
                    )
                )
                await self._update_payment_completion(payment)
                
            elif status == "failed":
                failure_reason = webhook_data.get("failure_reason", "Unknown error")
                crud_payment.update(
                    self.db, payment.id,
                    PaymentUpdate(
                        status=PaymentStatus.failed,
                        failure_reason=failure_reason,
                        failed_at=datetime.now()
                    )
                )
                
            elif status == "cancelled":
                crud_payment.update(
                    self.db, payment.id,
                    PaymentUpdate(status=PaymentStatus.cancelled)
                )

            return WebhookProcessingResult(
                success=True,
                message=f"Payment status updated to {status}",
                payment_id=payment.id
            )

        except Exception as e:
            logger.error(f"Error processing Fanbasis webhook: {str(e)}")
            return WebhookProcessingResult(
                success=False,
                message=f"Webhook processing failed: {str(e)}",
                error_details={"error": str(e), "webhook_data": webhook_data}
            )

    async def _update_payment_completion(self, payment):
        """Update related records when payment is completed"""
        try:
            from app.crud import creator_earnings as crud_earnings
            from app.utils.calculations import round_currency
            
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
                    payment.campaign_id, float(payment.amount)
                )

        except Exception as e:
            logger.error(f"Error updating payment completion records: {str(e)}")