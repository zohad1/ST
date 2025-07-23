# app/external/stripe_client.py
import stripe
import logging
from typing import Dict, Optional, Any
from uuid import UUID
from app.core.config import settings
from app.models.payment_enums import PaymentStatus

logger = logging.getLogger(__name__)

class StripeClient:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    async def create_payment_intent(
        self, 
        amount: float, 
        creator_id: UUID, 
        description: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe payment intent for creator payout
        """
        try:
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            # Prepare metadata
            payment_metadata = {
                "creator_id": str(creator_id),
                "service": "payment-service",
                **(metadata or {})
            }

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                payment_method_types=['card'],
                description=description or f"Payout for creator {creator_id}",
                metadata=payment_metadata,
                capture_method='automatic'
            )

            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": amount,
                "currency": intent.currency,
                "client_secret": intent.client_secret
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            raise Exception(f"Payment creation failed: {str(e)}")

    async def create_transfer(
        self, 
        amount: float, 
        destination_account: str, 
        creator_id: UUID,
        description: str = None
    ) -> Dict[str, Any]:
        """
        Create a direct transfer to creator's connected account
        """
        try:
            amount_cents = int(amount * 100)
            
            transfer = stripe.Transfer.create(
                amount=amount_cents,
                currency='usd',
                destination=destination_account,
                description=description or f"Payout for creator {creator_id}",
                metadata={
                    "creator_id": str(creator_id),
                    "service": "payment-service"
                }
            )

            return {
                "transfer_id": transfer.id,
                "status": "succeeded" if transfer.amount > 0 else "failed",
                "amount": amount,
                "destination": destination_account
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating transfer: {str(e)}")
            raise Exception(f"Transfer creation failed: {str(e)}")

    async def get_payment_status(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Get current status of a payment intent
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,  # Convert back from cents
                "currency": intent.currency,
                "charges": [
                    {
                        "charge_id": charge.id,
                        "status": charge.status,
                        "failure_code": charge.failure_code,
                        "failure_message": charge.failure_message
                    }
                    for charge in intent.charges.data
                ]
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving payment status: {str(e)}")
            raise Exception(f"Status retrieval failed: {str(e)}")

    async def cancel_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Cancel a payment intent
        """
        try:
            # Cancel the payment intent
            intent = stripe.PaymentIntent.cancel(payment_intent_id)
            
            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "cancellation_reason": intent.cancellation_reason,
                "canceled_at": intent.canceled_at
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error canceling payment: {str(e)}")
            raise Exception(f"Payment cancellation failed: {str(e)}")

    async def refund_payment(self, payment_intent_id: str, amount: float = None) -> Dict[str, Any]:
        """
        Refund a payment (partial or full)
        """
        try:
            # Get the charge ID from payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if not intent.charges.data:
                raise Exception("No charges found for this payment intent")
            
            charge_id = intent.charges.data[0].id
            refund_amount = int(amount * 100) if amount else None
            
            refund = stripe.Refund.create(
                charge=charge_id,
                amount=refund_amount
            )

            return {
                "refund_id": refund.id,
                "status": refund.status,
                "amount": refund.amount / 100,
                "currency": refund.currency
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating refund: {str(e)}")
            raise Exception(f"Refund failed: {str(e)}")

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature
        """
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except ValueError:
            logger.error("Invalid payload in webhook")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in webhook")
            return False

    def parse_webhook_event(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """
        Parse and validate Stripe webhook event
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except Exception as e:
            logger.error(f"Error parsing webhook: {str(e)}")
            return None