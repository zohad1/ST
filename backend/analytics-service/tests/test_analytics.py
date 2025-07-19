
# tests/test_analytics.py
import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.base import Base
from app.core.database import get_db
from app.schemas.analytics import CampaignPerformanceDailyCreate

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_campaign_id():
    return uuid4()

@pytest.fixture
def test_performance_data(test_campaign_id):
    return CampaignPerformanceDailyCreate(
        campaign_id=test_campaign_id,
        date_snapshot=date.today(),
        total_creators=10,
        active_creators=8,
        new_applications=2,
        approved_applications=2,
        posts_submitted=15,
        posts_approved=12,
        total_views=50000,
        total_likes=2500,
        total_comments=150,
        total_shares=75,
        total_gmv=Decimal('1500.00'),
        total_commissions=Decimal('150.00'),
        total_payouts=Decimal('750.00'),
        avg_engagement_rate=Decimal('5.50'),
        conversion_rate=Decimal('2.25'),
        cost_per_acquisition=Decimal('25.00')
    )

def test_create_campaign_performance(test_campaign_id, test_performance_data):
    response = client.post(
        f"/api/v1/campaigns/{test_campaign_id}/performance/daily",
        json=test_performance_data.model_dump(mode='json')
    )
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == str(test_campaign_id)
    assert data["total_creators"] == 10

def test_get_campaign_performance(test_campaign_id, test_performance_data):
    # First create the performance data
    client.post(
        f"/api/v1/campaigns/{test_campaign_id}/performance/daily",
        json=test_performance_data.model_dump(mode='json')
    )
    
    # Then retrieve it
    response = client.get(
        f"/api/v1/campaigns/{test_campaign_id}/performance/daily",
        params={"date_snapshot": str(date.today())}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == str(test_campaign_id)

def test_get_campaign_performance_range(test_campaign_id, test_performance_data):
    # Create performance data
    client.post(
        f"/api/v1/campaigns/{test_campaign_id}/performance/daily",
        json=test_performance_data.model_dump(mode='json')
    )
    
    start_date = date.today() - timedelta(days=7)
    end_date = date.today()
    
    response = client.get(
        f"/api/v1/campaigns/{test_campaign_id}/performance/range",
        params={
            "start_date": str(start_date),
            "end_date": str(end_date)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_overview_metrics():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_campaigns" in data
    assert "total_creators" in data
    assert "total_gmv" in data

def test_get_creator_leaderboard():
    response = client.get("/api/v1/creators/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_export_campaign_performance_csv(test_campaign_id, test_performance_data):
    # Create performance data
    client.post(
        f"/api/v1/campaigns/{test_campaign_id}/performance/daily",
        json=test_performance_data.model_dump(mode='json')
    )
    
    response = client.get(
        "/api/v1/reports/campaign-performance-csv",
        params={"campaign_id": str(test_campaign_id)}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"