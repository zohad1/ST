
# app/external/user_service_client.py
import httpx
import logging
from typing import Dict, Optional, List
from uuid import UUID
from app.core.config import settings

logger = logging.getLogger(__name__)

class UserServiceClient:
    def __init__(self):
        self.base_url = settings.USER_SERVICE_URL

    async def get_user(self, user_id: UUID) -> Optional[Dict]:
        """Get user details from User Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/users/{user_id}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None

    async def check_user_exists_and_role(self, user_id: UUID, expected_role: str) -> bool:
        """Check if user exists and has expected role"""
        user_data = await self.get_user(user_id)
        if not user_data:
            return False
        return user_data.get("role") == expected_role

    async def get_creator_details(self, creator_id: UUID) -> Optional[Dict]:
        """Get creator-specific details including payment info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/creators/{creator_id}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting creator details {creator_id}: {str(e)}")
            return None

    async def get_users_batch(self, user_ids: List[UUID]) -> Dict[UUID, Dict]:
        """Get multiple users in a single request"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/users/batch",
                    json={"user_ids": [str(uid) for uid in user_ids]}
                )
                response.raise_for_status()
                data = response.json()
                
                # Convert back to UUID keys
                return {UUID(k): v for k, v in data.items()}
        except httpx.HTTPError as e:
            logger.error(f"Error getting users batch: {str(e)}")
            return {}

