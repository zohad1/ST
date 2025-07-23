# app/schemas/dashboard.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApplicationStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class DeliverableStatusEnum(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_NEEDED = "revision_needed"


# Dashboard Analytics Schemas
class KPIMetric(BaseModel):
    value: float
    growth: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"


class DashboardKPIs(BaseModel):
    total_gmv: KPIMetric
    total_views: KPIMetric
    total_engagement: KPIMetric
    active_campaigns: KPIMetric
    active_creators: KPIMetric
    avg_engagement_rate: KPIMetric
    conversion_rate: KPIMetric
    roi: KPIMetric


class CampaignSummary(BaseModel):
    id: str
    name: str
    status: CampaignStatusEnum
    progress: float  # 0-100
    target_gmv: Optional[Decimal] = None
    current_gmv: Optional[Decimal] = None
    target_creators: Optional[int] = None
    current_creators: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CreatorSummary(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    total_gmv: Optional[Decimal] = None
    total_posts: Optional[int] = None
    engagement_rate: Optional[float] = None
    consistency_score: Optional[float] = None
    rank: Optional[int] = None
    rank_change: Optional[int] = None


class DashboardAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    kpis: DashboardKPIs
    recent_campaigns: List[CampaignSummary]
    top_creators: List[CreatorSummary]
    period_start: datetime
    period_end: datetime
    last_updated: datetime


# Campaign Schemas
class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: Optional[str] = None
    status: CampaignStatusEnum
    type: str
    budget: Optional[Decimal] = None
    target_gmv: Optional[Decimal] = None
    current_gmv: Optional[Decimal] = None
    target_creators: Optional[int] = None
    current_creators: Optional[int] = None
    target_posts: Optional[int] = None
    current_posts: Optional[int] = None
    total_views: Optional[int] = None
    total_engagement: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CampaignCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = "performance"
    budget: Optional[Decimal] = None
    target_gmv: Optional[Decimal] = None
    target_creators: Optional[int] = None
    target_posts: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    requirements: Optional[Dict[str, Any]] = None
    products: Optional[Dict[str, Any]] = None
    brand_guidelines: Optional[Dict[str, Any]] = None


class CampaignUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatusEnum] = None
    budget: Optional[Decimal] = None
    target_gmv: Optional[Decimal] = None
    target_creators: Optional[int] = None
    target_posts: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    requirements: Optional[Dict[str, Any]] = None
    products: Optional[Dict[str, Any]] = None
    brand_guidelines: Optional[Dict[str, Any]] = None


# Application Schemas
class CampaignApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    campaign_id: str
    creator_id: str
    status: ApplicationStatusEnum
    application_message: Optional[str] = None
    response_message: Optional[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[Decimal] = None
    previous_gmv: Optional[Decimal] = None
    applied_at: datetime
    reviewed_at: Optional[datetime] = None
    
    # Related data
    creator: CreatorSummary
    campaign: CampaignSummary


class ApplicationReviewRequest(BaseModel):
    status: ApplicationStatusEnum = Field(..., regex="^(approved|rejected)$")
    response_message: Optional[str] = None


# Deliverable Schemas
class DeliverableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    campaign_id: str
    creator_id: str
    title: str
    description: Optional[str] = None
    status: DeliverableStatusEnum
    content_url: Optional[str] = None
    content_type: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    gmv_generated: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    creator: CreatorSummary
    campaign: CampaignSummary


class DeliverableCreateRequest(BaseModel):
    campaign_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class DeliverableUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DeliverableStatusEnum] = None
    content_url: Optional[str] = None
    content_type: Optional[str] = None
    due_date: Optional[datetime] = None
    feedback: Optional[str] = None
    revision_notes: Optional[str] = None


class ContentSubmissionRequest(BaseModel):
    content_url: str = Field(..., regex="^https?://")
    content_type: str = "video"
    content_duration: Optional[int] = None


class ContentReviewRequest(BaseModel):
    status: DeliverableStatusEnum = Field(..., regex="^(approved|rejected|revision_needed)$")
    feedback: Optional[str] = None
    revision_notes: Optional[str] = None


# Analytics Schemas
class AnalyticsTimeframe(str, Enum):
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"


class AnalyticsRequest(BaseModel):
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    campaign_id: Optional[str] = None
    creator_id: Optional[str] = None


class CreatorPerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    creator_id: str
    campaign_id: Optional[str] = None
    total_posts: int
    total_gmv: Decimal
    total_views: int
    total_engagement: int
    engagement_rate: float
    conversion_rate: float
    consistency_score: float
    gmv_rank: Optional[int] = None
    engagement_rank: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    last_calculated: datetime
    
    # Creator info
    creator: CreatorSummary


class LeaderboardResponse(BaseModel):
    creators: List[CreatorPerformanceResponse]
    total_count: int
    timeframe: str
    last_updated: datetime


# Response wrapper
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None