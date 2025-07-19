# app/schemas/analytics.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

# Campaign Performance Schemas
class CampaignPerformanceDailyBase(BaseModel):
    campaign_id: UUID
    date_snapshot: date
    total_creators: int = 0
    active_creators: int = 0
    new_applications: int = 0
    approved_applications: int = 0
    posts_submitted: int = 0
    posts_approved: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_gmv: Decimal = Field(default=Decimal('0.00'), max_digits=12, decimal_places=2)
    total_commissions: Decimal = Field(default=Decimal('0.00'), max_digits=10, decimal_places=2)
    total_payouts: Decimal = Field(default=Decimal('0.00'), max_digits=10, decimal_places=2)
    avg_engagement_rate: Decimal = Field(default=Decimal('0.00'), max_digits=5, decimal_places=2)
    conversion_rate: Decimal = Field(default=Decimal('0.00'), max_digits=5, decimal_places=2)
    cost_per_acquisition: Decimal = Field(default=Decimal('0.00'), max_digits=10, decimal_places=2)


class CampaignPerformanceDailyCreate(CampaignPerformanceDailyBase):
    pass


class CampaignPerformanceDailyUpdate(BaseModel):
    total_creators: Optional[int] = None
    active_creators: Optional[int] = None
    new_applications: Optional[int] = None
    approved_applications: Optional[int] = None
    posts_submitted: Optional[int] = None
    posts_approved: Optional[int] = None
    total_views: Optional[int] = None
    total_likes: Optional[int] = None
    total_comments: Optional[int] = None
    total_shares: Optional[int] = None
    total_gmv: Optional[Decimal] = None
    total_commissions: Optional[Decimal] = None
    total_payouts: Optional[Decimal] = None
    avg_engagement_rate: Optional[Decimal] = None
    conversion_rate: Optional[Decimal] = None
    cost_per_acquisition: Optional[Decimal] = None


class CampaignPerformanceDailyResponse(CampaignPerformanceDailyBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Creator Performance Schemas
class CreatorPerformanceBase(BaseModel):
    creator_id: UUID
    campaign_id: Optional[UUID] = None
    total_posts: int = 0
    completed_deliverables: int = 0
    on_time_deliverables: int = 0
    total_gmv: Decimal = Field(default=Decimal('0.00'), max_digits=12, decimal_places=2)
    avg_views_per_post: Decimal = Field(default=Decimal('0.00'), max_digits=12, decimal_places=2)
    avg_engagement_rate: Decimal = Field(default=Decimal('0.00'), max_digits=5, decimal_places=2)
    consistency_score: Decimal = Field(default=Decimal('0.00'), max_digits=3, decimal_places=2)
    reliability_rating: Decimal = Field(default=Decimal('0.0'), max_digits=2, decimal_places=1)


class CreatorPerformanceCreate(CreatorPerformanceBase):
    pass


class CreatorPerformanceUpdate(BaseModel):
    total_posts: Optional[int] = None
    completed_deliverables: Optional[int] = None
    on_time_deliverables: Optional[int] = None
    total_gmv: Optional[Decimal] = None
    avg_views_per_post: Optional[Decimal] = None
    avg_engagement_rate: Optional[Decimal] = None
    consistency_score: Optional[Decimal] = None
    reliability_rating: Optional[Decimal] = None


class CreatorPerformanceResponse(CreatorPerformanceBase):
    id: UUID
    last_calculated: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class CampaignAnalyticsSummary(BaseModel):
    campaign_id: UUID
    campaign_name: Optional[str] = None
    total_gmv: Decimal
    total_creators: int
    total_posts: int
    avg_engagement_rate: Decimal
    conversion_rate: Decimal
    date_range: Dict[str, date]


class CreatorLeaderboard(BaseModel):
    creator_id: UUID
    creator_name: Optional[str] = None
    total_gmv: Decimal
    total_posts: int
    avg_engagement_rate: Decimal
    rank: int


class PerformanceMetrics(BaseModel):
    total_campaigns: int
    total_creators: int
    total_gmv: Decimal
    total_posts: int
    avg_engagement_rate: Decimal
    top_performing_campaigns: List[CampaignAnalyticsSummary]
    top_performing_creators: List[CreatorLeaderboard]


class DateRangeFilter(BaseModel):
    start_date: date
    end_date: date


class AnalyticsFilter(BaseModel):
    campaign_ids: Optional[List[UUID]] = None
    creator_ids: Optional[List[UUID]] = None
    date_range: Optional[DateRangeFilter] = None
    agency_id: Optional[UUID] = None
    brand_id: Optional[UUID] = None


class CampaignProgressResponse(BaseModel):
    campaign_id: UUID
    target_gmv: Optional[Decimal] = None
    current_gmv: Decimal
    target_posts: Optional[int] = None
    current_posts: int
    progress_percentage: float
    status: str  # "ahead", "on_track", "behind"
    days_remaining: Optional[int] = None


class EngagementAnalytics(BaseModel):
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    engagement_rate: Decimal
    view_to_like_ratio: Decimal
    
    
class GMVAnalytics(BaseModel):
    total_gmv: Decimal
    gmv_growth_rate: Decimal
    avg_gmv_per_creator: Decimal
    avg_gmv_per_post: Decimal
    top_gmv_days: List[Dict[str, Any]]