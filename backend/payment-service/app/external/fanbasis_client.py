# app/external/fanbasis_client.py
import httpx
import hashlib
import hmac
import logging
from typing import Dict, Optional, Any
from uuid import UUID
from app.core.config import settings

logger = logging.getLogger(__name__)

class FanbasisClient:
    def __init__(self):
        self.api_key = settings.FANBASIS_API_KEY
        self.webhook_secret = settings.FANBASIS_WEBHOOK_SECRET
        self.base_url = settings.FANBASIS_BASE_URL if hasattr(settings, 'FANBASIS_BASE_URL') else "https://api.fanbasis.com"

    async def create_payout(
        self, 
        amount: float, 
        creator_id: UUID, 
        creator_email: str,
        description: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a payout request through Fanbasis
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "amount": amount,
                "creator_id": str(creator_id),
                "email": creator_email,
                "description": description or f"Payout for creator {creator_id}",
                "metadata": metadata or {}
            }
            
            # In production, this would make an actual API call
            # For testing, return mock response
            if settings.TESTING_MODE:
                return {
                    "transaction_id": f"fb_test_{UUID.uuid4()}",
                    "status": "completed",
                    "amount": amount,
                    "currency": "USD"
                }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payouts",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Fanbasis API error: {str(e)}")
            raise Exception(f"Fanbasis payout creation failed: {str(e)}")

    async def get_payout_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get the status of a payout
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Mock response for testing
            if settings.TESTING_MODE:
                return {
                    "transaction_id": transaction_id,
                    "status": "completed",
                    "amount": 100.00,
                    "currency": "USD"
                }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/payouts/{transaction_id}",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error getting payout status: {str(e)}")
            raise Exception(f"Status retrieval failed: {str(e)}")

    async def cancel_payout(self, transaction_id: str) -> Dict[str, Any]:
        """
        Cancel a pending payout
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Mock response for testing
            if settings.TESTING_MODE:
                return {
                    "transaction_id": transaction_id,
                    "status": "cancelled",
                    "message": "Payout cancelled successfully"
                }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payouts/{transaction_id}/cancel",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error cancelling payout: {str(e)}")
            raise Exception(f"Cancellation failed: {str(e)}")

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Fanbasis webhook signature
        """
        try:
            # Generate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False