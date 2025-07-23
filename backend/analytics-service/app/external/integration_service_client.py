
# app/external/integration_service_client.py
import httpx
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

logger = logging.getLogger(__name__)

class IntegrationServiceClient:
    def __init__(self, base_url: str = "http://integration-service:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_tiktok_gmv_data(self, campaign_id: UUID, creator_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get TikTok Shop GMV data"""
        try:
            url = f"{self.base_url}/api/v1/tiktok/gmv/{campaign_id}"
            if creator_id:
                url += f"?creator_id={creator_id}"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching TikTok GMV data: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error connecting to integration service: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()