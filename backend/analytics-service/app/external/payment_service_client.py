
# app/external/payment_service_client.py
import httpx
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaymentServiceClient:
    def __init__(self, base_url: str = "http://payment-service:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_creator_earnings(self, creator_id: UUID, campaign_id: Optional[UUID] = None) -> Optional[Dict[str, Any]]:
        """Get creator earnings from payment service"""
        try:
            url = f"{self.base_url}/api/v1/earnings/creator/{creator_id}"
            if campaign_id:
                url += f"?campaign_id={campaign_id}"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error fetching creator earnings: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error connecting to payment service: {e}")
            return None
    
    async def get_campaign_payouts(self, campaign_id: UUID) -> List[Dict[str, Any]]:
        """Get all payouts for a campaign"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/payments/campaign/{campaign_id}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching campaign payouts: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error connecting to payment service: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
