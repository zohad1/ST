import httpx
from uuid import UUID
from app.core.config import settings  # Assuming you have a base URL for user service


class UserServiceClient:
    def __init__(self):
        self.base_url = "http://localhost:8001/users"  # Replace with actual User Service URL
        # self.base_url = settings.USER_SERVICE_URL # Better practice

    async def check_user_exists_and_role(self, user_id: UUID, expected_role: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/{user_id}")
                response.raise_for_status()  # Raise an exception for 4xx/5xx responses
                user_data = response.json()
                return user_data.get("id") == str(user_id) and user_data.get("role") == expected_role
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False  # User not found
            raise  # Re-raise other HTTP errors
        except httpx.RequestError as e:
            # Handle network errors, service unavailability etc.
            raise ConnectionError(f"Could not connect to User Service: {e}") from e

    # Add other methods as needed, e.g., get_creator_profile, get_agency_details
