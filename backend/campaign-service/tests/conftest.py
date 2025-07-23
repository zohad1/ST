# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.models.base import Base
from app.core.database import get_db
from app.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def mock_user_token():
    """Mock JWT token for testing"""
    return "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"

# tests/test_campaign_service.py
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from app.services.campaign_service import CampaignService
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.models.campaign import PayoutModel, TrackingMethod
from app.core.exceptions import ValidationException
from fastapi import HTTPException

class TestCampaignService:
    
    def test_create_campaign_success(self, db_session):
        """Test successful campaign creation"""
        service = CampaignService(db_session)
        agency_id = uuid4()
        
        campaign_data = CampaignCreate(
            name="Test Campaign",
            description="Test Description",
            payout_model=PayoutModel.fixed_per_post,
            tracking_method=TrackingMethod.hashtag,
            base_payout_per_post=50.0,
            hashtag="#test",
            start_date=datetime.now() + timedelta(days=1),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        result = service.create_new_campaign(campaign_data, agency_id)
        
        assert result.name == "Test Campaign"
        assert result.agency_id == agency_id
        assert result.payout_model == PayoutModel.fixed_per_post
        assert result.hashtag == "#test"
    
    def test_create_campaign_invalid_payout_model(self, db_session):
        """Test campaign creation with invalid payout model"""
        service = CampaignService(db_session)
        agency_id = uuid4()
        
        campaign_data = CampaignCreate(
            name="Test Campaign",
            payout_model=PayoutModel.gmv_commission,
            tracking_method=TrackingMethod.hashtag,
            hashtag="#test",
            # Missing gmv_commission_rate
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_new_campaign(campaign_data, agency_id)
        
        assert exc_info.value.status_code == 400
        assert "GMV commission rate is required" in str(exc_info.value.detail)
    
    def test_create_campaign_invalid_tracking_method(self, db_session):
        """Test campaign creation with invalid tracking method"""
        service = CampaignService(db_session)
        agency_id = uuid4()
        
        campaign_data = CampaignCreate(
            name="Test Campaign",
            payout_model=PayoutModel.fixed_per_post,
            tracking_method=TrackingMethod.hashtag,
            base_payout_per_post=50.0,
            # Missing hashtag
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_new_campaign(campaign_data, agency_id)
        
        assert exc_info.value.status_code == 400
        assert "Hashtag is required" in str(exc_info.value.detail)
    
    def test_get_campaign_not_found(self, db_session):
        """Test getting non-existent campaign"""
        service = CampaignService(db_session)
        campaign_id = uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_campaign_by_id(campaign_id)
        
        assert exc_info.value.status_code == 404
        assert "Campaign not found" in str(exc_info.value.detail)
    
    def test_update_campaign_success(self, db_session):
        """Test successful campaign update"""
        service = CampaignService(db_session)
        agency_id = uuid4()
        
        # Create campaign first
        campaign_data = CampaignCreate(
            name="Test Campaign",
            payout_model=PayoutModel.fixed_per_post,
            tracking_method=TrackingMethod.hashtag,
            base_payout_per_post=50.0,
            hashtag="#test"
        )
        
        created_campaign = service.create_new_campaign(campaign_data, agency_id)
        
        # Update campaign
        update_data = CampaignUpdate(
            name="Updated Campaign",
            description="Updated Description"
        )
        
        updated_campaign = service.update_existing_campaign(created_campaign.id, update_data)
        
        assert updated_campaign.name == "Updated Campaign"
        assert updated_campaign.description == "Updated Description"
    
    def test_invalid_status_transition(self, db_session):
        """Test invalid status transition"""
        service = CampaignService(db_session)
        agency_id = uuid4()
        
        # Create and complete campaign
        campaign_data = CampaignCreate(
            name="Test Campaign",
            payout_model=PayoutModel.fixed_per_post,
            tracking_method=TrackingMethod.hashtag,
            base_payout_per_post=50.0,
            hashtag="#test"
        )
        
        created_campaign = service.create_new_campaign(campaign_data, agency_id)
        
        # Try to transition from draft to completed (invalid)
        update_data = CampaignUpdate(status="completed")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_existing_campaign(created_campaign.id, update_data)
        
        assert exc_info.value.status_code == 400
