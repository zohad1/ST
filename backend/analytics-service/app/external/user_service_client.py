
# app/external/user_service_client.py
import httpx
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

logger = logging.getLogger(__name__)

class UserServiceClient:
    def __init__(self, base_url: str = "http://user-service:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user details from user service"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error fetching user {user_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error connecting to user service: {e}")
            return None
    
    async def get_users(self, user_ids: List[UUID]) -> List[Dict[str, Any]]:
        """Get multiple users by IDs"""
        try:
            # Convert UUIDs to strings for the request
            user_ids_str = [str(uid) for uid in user_ids]
            response = await self.client.post(
                f"{self.base_url}/api/v1/users/batch",
                json={"user_ids": user_ids_str}
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching batch users: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error connecting to user service: {e}")
            return []
    
    async def get_creator_profile(self, creator_id: UUID) -> Optional[Dict[str, Any]]:
        """Get creator-specific profile data"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/creators/{creator_id}/profile")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error fetching creator profile {creator_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error connecting to user service: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
