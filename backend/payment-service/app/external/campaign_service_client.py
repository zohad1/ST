
# app/external/campaign_service_client.py
import httpx
import logging
from typing import Dict, Optional, List
from uuid import UUID
from app.core.config import settings

logger = logging.getLogger(__name__)

class CampaignServiceClient:
    def __init__(self):
        self.base_url = settings.CAMPAIGN_SERVICE_URL

    async def get_campaign(self, campaign_id: UUID) -> Optional[Dict]:
        """Get campaign details"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/campaigns/{campaign_id}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting campaign {campaign_id}: {str(e)}")
            return None

    async def get_creator_application(self, application_id: UUID) -> Optional[Dict]:
        """Get creator application details"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/applications/{application_id}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting application {application_id}: {str(e)}")
            return None

    async def get_creator_deliverables(self, application_id: UUID) -> Dict:
        """Get deliverable information for a creator application"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/applications/{application_id}/deliverables"
                )
                response.raise_for_status()
                data = response.json()
                
                # Calculate completed count
                completed_count = sum(1 for d in data if d.get("status") == "approved")
                
                return {
                    "deliverables": data,
                    "completed_count": completed_count,
                    "total_count": len(data)
                }
        except httpx.HTTPError as e:
            logger.error(f"Error getting deliverables for application {application_id}: {str(e)}")
            return {"deliverables": [], "completed_count": 0, "total_count": 0}

    async def get_campaign_creators(self, campaign_id: UUID) -> List[Dict]:
        """Get all creators in a campaign"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/campaigns/{campaign_id}/applications"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting campaign creators {campaign_id}: {str(e)}")
            return []

    async def update_campaign_spent_amount(self, campaign_id: UUID, amount: float):
        """Update campaign spent amount after payment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/campaigns/{campaign_id}/spent",
                    json={"amount": amount}
                )
                response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Error updating campaign spent amount: {str(e)}")

