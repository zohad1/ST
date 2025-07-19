# app/api/endpoints/campaigns.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    CampaignPerformanceDailyCreate,
    CampaignPerformanceDailyResponse,
    CampaignAnalyticsSummary,
    CampaignProgressResponse,
    AnalyticsFilter,
    DateRangeFilter
)

router = APIRouter()

@router.get("/{campaign_id}/performance/daily", response_model=CampaignPerformanceDailyResponse)
async def get_campaign_daily_performance(
    campaign_id: UUID,
    date_snapshot: date = Query(default_factory=lambda: date.today()),
    db: Session = Depends(get_db)
):
    """Get daily performance metrics for a specific campaign"""
    service = AnalyticsService(db)
    performance = service.get_campaign_daily_performance(campaign_id, date_snapshot)
    
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No performance data found for campaign {campaign_id} on {date_snapshot}"
        )
    
    return performance


@router.get("/{campaign_id}/performance/range", response_model=List[CampaignPerformanceDailyResponse])
async def get_campaign_performance_range(
    campaign_id: UUID,
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today()),
    db: Session = Depends(get_db)
):
    """Get performance metrics for a campaign over a date range"""
    service = AnalyticsService(db)
    return service.get_campaign_performance_range(campaign_id, start_date, end_date)


@router.post("/{campaign_id}/performance/daily", response_model=CampaignPerformanceDailyResponse)
async def create_or_update_daily_performance(
    campaign_id: UUID,
    performance_data: CampaignPerformanceDailyCreate,
    db: Session = Depends(get_db)
):
    """Create or update daily performance metrics for a campaign"""
    # Ensure campaign_id matches
    if performance_data.campaign_id != campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign ID in URL does not match campaign ID in data"
        )
    
    service = AnalyticsService(db)
    return service.create_or_update_daily_performance(performance_data)


@router.get("/{campaign_id}/summary", response_model=CampaignAnalyticsSummary)
async def get_campaign_summary(
    campaign_id: UUID,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get campaign analytics summary"""
    service = AnalyticsService(db)
    return service.get_campaign_summary(campaign_id, start_date, end_date)


@router.get("/{campaign_id}/progress", response_model=CampaignProgressResponse)
async def get_campaign_progress(
    campaign_id: UUID,
    db: Session = Depends(get_db)
):
    """Get campaign progress against targets"""
    service = AnalyticsService(db)
    try:
        return service.get_campaign_progress(campaign_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )



