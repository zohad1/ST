

# app/services/analytics_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.models.user import User
from app.models.campaign import Campaign, CampaignApplication
from app.models.analytics import CreatorPerformance
from app.schemas.dashboard import (
    CreatorPerformanceResponse, LeaderboardResponse, CreatorSummary,
    AnalyticsTimeframe
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    async def get_creator_performance(
        self, 
        db: Session, 
        user: User, 
        campaign_id: Optional[str] = None,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
        limit: int = 10
    ) -> List[CreatorPerformanceResponse]:
        """Get creator performance metrics."""
        
        # Calculate date range
        end_date = datetime.utcnow()
        if timeframe == AnalyticsTimeframe.LAST_7_DAYS:
            start_date = end_date - timedelta(days=7)
        elif timeframe == AnalyticsTimeframe.LAST_30_DAYS:
            start_date = end_date - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.LAST_90_DAYS:
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        query = db.query(CreatorPerformance).join(User)
        
        # Filter by user role
        if user.role == "agency":
            # Get creators from agency's campaigns
            campaign_ids = db.query(Campaign.id).filter(Campaign.agency_id == user.id).subquery()
            query = query.filter(CreatorPerformance.campaign_id.in_(campaign_ids))
        elif user.role == "brand":
            # Get creators from brand's campaigns
            campaign_ids = db.query(Campaign.id).filter(Campaign.brand_id == user.id).subquery()
            query = query.filter(CreatorPerformance.campaign_id.in_(campaign_ids))
        elif user.role == "creator":
            # Get creator's own performance
            query = query.filter(CreatorPerformance.creator_id == user.id)
        
        # Apply filters
        if campaign_id:
            query = query.filter(CreatorPerformance.campaign_id == campaign_id)
        
        # Filter by date range
        query = query.filter(
            and_(
                CreatorPerformance.period_start >= start_date,
                CreatorPerformance.period_end <= end_date
            )
        )
        
        performances = query.order_by(desc(CreatorPerformance.total_gmv)).limit(limit).all()
        
        # Convert to response models
        responses = []
        for perf in performances:
            creator = perf.creator
            responses.append(CreatorPerformanceResponse(
                creator_id=str(perf.creator_id),
                campaign_id=str(perf.campaign_id) if perf.campaign_id else None,
                total_posts=perf.total_posts,
                total_gmv=perf.total_gmv,
                total_views=perf.total_views,
                total_engagement=perf.total_engagement,
                engagement_rate=float(perf.engagement_rate),
                conversion_rate=float(perf.conversion_rate),
                consistency_score=float(perf.consistency_score),
                gmv_rank=perf.gmv_rank,
                engagement_rank=perf.engagement_rank,
                period_start=perf.period_start,
                period_end=perf.period_end,
                last_calculated=perf.last_calculated,
                creator=CreatorSummary(
                    id=str(creator.id),
                    first_name=creator.first_name,
                    last_name=creator.last_name,
                    username=creator.username,
                    avatar_url=getattr(creator, 'avatar_url', None),
                    total_gmv=perf.total_gmv,
                    total_posts=perf.total_posts,
                    engagement_rate=float(perf.engagement_rate),
                    consistency_score=float(perf.consistency_score),
                    rank=perf.gmv_rank
                )
            ))
        
        return responses

    async def get_creator_leaderboard(
        self, 
        db: Session, 
        user: User, 
        metric: str = "gmv",
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
        limit: int = 50
    ) -> LeaderboardResponse:
        """Get creator leaderboard."""
        
        # Get creator performance data
        performances = await self.get_creator_performance(
            db, user, None, timeframe, limit
        )
        
        # Sort by specified metric
        if metric == "engagement":
            performances.sort(key=lambda x: x.engagement_rate, reverse=True)
        elif metric == "consistency":
            performances.sort(key=lambda x: x.consistency_score, reverse=True)
        else:  # default to GMV
            performances.sort(key=lambda x: x.total_gmv, reverse=True)
        
        # Update ranks
        for i, perf in enumerate(performances):
            perf.creator.rank = i + 1
        
        return LeaderboardResponse(
            creators=performances,
            total_count=len(performances),
            timeframe=timeframe.value,
            last_updated=datetime.utcnow()
        )


# Create service instances

analytics_service = AnalyticsService()