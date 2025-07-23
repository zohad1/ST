# app/external/campaign_service_client.py
import httpx
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

logger = logging.getLogger(__name__)

class CampaignServiceClient:
    def __init__(self, base_url: str = "http://campaign-service:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_campaign(self, campaign_id: UUID) -> Optional[Dict[str, Any]]:
        """Get campaign details from campaign service"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/campaigns/{campaign_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error fetching campaign {campaign_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error connecting to campaign service: {e}")
            return None
    
    async def get_campaign_deliverables(self, campaign_id: UUID) -> List[Dict[str, Any]]:
        """Get all deliverables for a campaign"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/campaigns/{campaign_id}/deliverables")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching deliverables for campaign {campaign_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error connecting to campaign service: {e}")
            return []
    
    async def get_creator_deliverables(self, creator_id: UUID, campaign_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get deliverables for a specific creator"""
        try:
            url = f"{self.base_url}/api/v1/deliverables/creator/{creator_id}"
            if campaign_id:
                url += f"?campaign_id={campaign_id}"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching creator deliverables: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error connecting to campaign service: {e}")
            return []
    
    async def get_campaign_applications(self, campaign_id: UUID) -> List[Dict[str, Any]]:
        """Get all applications for a campaign"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/campaigns/{campaign_id}/applications")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching applications for campaign {campaign_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error connecting to campaign service: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()



