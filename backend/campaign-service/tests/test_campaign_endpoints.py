
# tests/test_campaign_endpoints.py
import pytest
from uuid import uuid4
from fastapi import status

class TestCampaignEndpoints:
    
    def test_create_campaign_endpoint(self, client, mock_user_token):
        """Test campaign creation endpoint"""
        campaign_data = {
            "name": "API Test Campaign",
            "description": "Test Description",
            "payout_model": "fixed_per_post",
            "tracking_method": "hashtag",
            "base_payout_per_post": 50.0,
            "hashtag": "#apitest"
        }
        
        response = client.post(
            "/campaigns/",
            json=campaign_data,
            headers={"Authorization": mock_user_token}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "API Test Campaign"
        assert data["hashtag"] == "#apitest"
    
    def test_get_campaign_endpoint(self, client, mock_user_token):
        """Test get campaign endpoint"""
        # First create a campaign
        campaign_data = {
            "name": "API Test Campaign",
            "payout_model": "fixed_per_post",
            "tracking_method": "hashtag",
            "base_payout_per_post": 50.0,
            "hashtag": "#apitest"
        }
        
        create_response = client.post(
            "/campaigns/",
            json=campaign_data,
            headers={"Authorization": mock_user_token}
        )
        
        campaign_id = create_response.json()["id"]
        
        # Get the campaign
        response = client.get(
            f"/campaigns/{campaign_id}",
            headers={"Authorization": mock_user_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == campaign_id
        assert data["name"] == "API Test Campaign"
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints"""
        response = client.get("/campaigns/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
