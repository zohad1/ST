# app/schemas/campaign.py - COMPLETE FIXED VERSION
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Union, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
import json

from app.models.campaign import CampaignStatus, PayoutModel, TrackingMethod, CampaignType


class CampaignBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    payout_model: str  # Always use string
    tracking_method: str  # Always use string
    type: str = "performance"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    grace_period_days: int = 0
    is_rolling_30_day: bool = False
    max_creators: Optional[int] = None
    min_deliverables_per_creator: int = 1
    require_approval: bool = True
    require_discord_join: bool = False
    discord_server_id: Optional[str] = None
    discord_role_name: Optional[str] = None
    base_payout_per_post: Optional[Decimal] = Decimal('0.00')
    gmv_commission_rate: Optional[Decimal] = Decimal('0.00')
    retainer_amount: Optional[Decimal] = Decimal('0.00')
    budget: Optional[Decimal] = None
    total_budget: Optional[Decimal] = None
    hashtag: Optional[str] = None
    tiktok_product_links: Optional[Union[List[str], str]] = None
    target_gmv: Optional[Decimal] = None
    target_posts: Optional[int] = None
    target_views: Optional[int] = None
    target_creators: Optional[int] = None
    referral_bonus_enabled: bool = False
    referral_bonus_amount: Optional[Decimal] = Decimal('0.00')
    
    @field_validator('payout_model', mode='before')
    def validate_payout_model(cls, v):
        if v is None:
            raise ValueError("payout_model is required")
        if hasattr(v, 'value'):  # If it's an enum
            v = v.value
        allowed_values = ['fixed_per_post', 'gmv_commission', 'hybrid', 'retainer_gmv']
        if v not in allowed_values:
            raise ValueError(f"payout_model must be one of {allowed_values}")
        return v
    
    @field_validator('tracking_method', mode='before')
    def validate_tracking_method(cls, v):
        if v is None:
            raise ValueError("tracking_method is required")
        if hasattr(v, 'value'):  # If it's an enum
            v = v.value
        allowed_values = ['hashtag', 'product_link', 'spark_code']
        if v not in allowed_values:
            raise ValueError(f"tracking_method must be one of {allowed_values}")
        return v
    
    @field_validator('type', mode='before')
    def validate_type(cls, v):
        if hasattr(v, 'value'):
            v = v.value
        if v is None or v == '':
            return 'performance'
        return v
    
    @field_validator('tiktok_product_links', mode='before')
    def clean_tiktok_product_links(cls, v):
        # Handle all the various ways this field might come in
        if v is None:
            return None
        if isinstance(v, str):
            if v.lower() in ['null', '', '[]', 'none']:
                return None
            # Try to parse as JSON first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    v = parsed
                else:
                    v = [v]  # Single URL as string
            except:
                # Not JSON, treat as single URL
                v = [v] if v.strip() else None
        if isinstance(v, list):
            # Clean the list
            cleaned = []
            for link in v:
                if link and isinstance(link, str) and link.strip() and link.lower() != 'null':
                    cleaned.append(link.strip())
            return cleaned if cleaned else None
        return None
    
    @field_validator('budget', 'total_budget', 'base_payout_per_post', 'gmv_commission_rate', 
                     'retainer_amount', 'target_gmv', 'referral_bonus_amount', mode='before')
    def coerce_decimal_fields(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                return Decimal(v)
            except:
                return None
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v
    
    @field_validator('grace_period_days', 'max_creators', 'min_deliverables_per_creator',
                     'target_posts', 'target_views', 'target_creators', mode='before')
    def coerce_integer_fields(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except:
                return None
        return v
    
    @model_validator(mode='after')
    def sync_budget_fields(self):
        # Ensure budget fields are synchronized
        if self.budget is not None and self.total_budget is None:
            self.total_budget = self.budget
        elif self.total_budget is not None and self.budget is None:
            self.budget = self.total_budget
        elif self.budget is None and self.total_budget is None:
            # Set default budget if both are None
            self.budget = Decimal('0.00')
            self.total_budget = Decimal('0.00')
        return self
    
    def model_dump(self, **kwargs):
        """Override to ensure proper serialization"""
        data = super().model_dump(**kwargs)
        
        # Clean up the tiktok_product_links for database
        if 'tiktok_product_links' in data:
            if data['tiktok_product_links'] is None or data['tiktok_product_links'] == []:
                data['tiktok_product_links'] = None
            
        return data
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v else None
        }
        validate_assignment = True
        use_enum_values = True
        arbitrary_types_allowed = True


class CampaignCreate(CampaignBase):
    brand_id: Optional[UUID] = None
    
    @field_validator('brand_id', mode='before')
    def validate_brand_id(cls, v):
        if v is None or v == '' or v == 'null':
            return None
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                return None
        return v


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign - all fields optional"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    payout_model: Optional[str] = None
    tracking_method: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    grace_period_days: Optional[int] = None
    is_rolling_30_day: Optional[bool] = None
    max_creators: Optional[int] = None
    min_deliverables_per_creator: Optional[int] = None
    require_approval: Optional[bool] = None
    require_discord_join: Optional[bool] = None
    discord_server_id: Optional[str] = None
    discord_role_name: Optional[str] = None
    base_payout_per_post: Optional[Decimal] = None
    gmv_commission_rate: Optional[Decimal] = None
    retainer_amount: Optional[Decimal] = None
    budget: Optional[Decimal] = None
    total_budget: Optional[Decimal] = None
    hashtag: Optional[str] = None
    tiktok_product_links: Optional[Union[List[str], str]] = None
    target_gmv: Optional[Decimal] = None
    target_posts: Optional[int] = None
    target_views: Optional[int] = None
    target_creators: Optional[int] = None
    referral_bonus_enabled: Optional[bool] = None
    referral_bonus_amount: Optional[Decimal] = None
    
    @field_validator('status', mode='before')
    def validate_status(cls, v):
        if v is None:
            return None
        if hasattr(v, 'value'):
            v = v.value
        allowed_values = ['draft', 'active', 'paused', 'completed', 'cancelled']
        if v not in allowed_values:
            raise ValueError(f"status must be one of {allowed_values}")
        return v
    
    @field_validator('payout_model', mode='before')
    def validate_payout_model(cls, v):
        if v is None:
            return None
        if hasattr(v, 'value'):
            v = v.value
        allowed_values = ['fixed_per_post', 'gmv_commission', 'hybrid', 'retainer_gmv']
        if v not in allowed_values:
            raise ValueError(f"payout_model must be one of {allowed_values}")
        return v
    
    @field_validator('tracking_method', mode='before')
    def validate_tracking_method(cls, v):
        if v is None:
            return None
        if hasattr(v, 'value'):
            v = v.value
        allowed_values = ['hashtag', 'product_link', 'spark_code']
        if v not in allowed_values:
            raise ValueError(f"tracking_method must be one of {allowed_values}")
        return v
    
    @field_validator('type', mode='before')
    def validate_type(cls, v):
        if v is None:
            return None
        if hasattr(v, 'value'):
            v = v.value
        allowed_values = ['performance', 'awareness', 'conversion', 'hybrid']
        if v not in allowed_values:
            raise ValueError(f"type must be one of {allowed_values}")
        return v
    
    @field_validator('tiktok_product_links', mode='before')
    def clean_tiktok_product_links(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            if v.lower() in ['null', '', '[]', 'none']:
                return None
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    v = parsed
                else:
                    v = [v]
            except:
                v = [v] if v.strip() else None
        if isinstance(v, list):
            cleaned = []
            for link in v:
                if link and isinstance(link, str) and link.strip() and link.lower() != 'null':
                    cleaned.append(link.strip())
            return cleaned if cleaned else None
        return None
    
    @field_validator('budget', 'total_budget', 'base_payout_per_post', 'gmv_commission_rate', 
                     'retainer_amount', 'target_gmv', 'referral_bonus_amount', mode='before')
    def coerce_decimal_fields(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                return Decimal(v)
            except:
                return None
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True
        arbitrary_types_allowed = True


class CampaignResponse(CampaignBase):
    """Response schema for campaigns"""
    id: UUID
    agency_id: UUID
    brand_id: Optional[UUID] = None
    status: str = "draft"
    spent_amount: Decimal = Decimal('0.00')
    current_gmv: Decimal = Decimal('0.00')
    current_posts: int = 0
    current_creators: int = 0
    total_views: int = 0
    total_engagement: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v else None
        }


# Campaign Segment Schemas
class CampaignSegmentBase(BaseModel):
    segment_name: str = Field(..., max_length=100)
    segment_description: Optional[str] = None
    gender_filter: Optional[List[str]] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    required_niches: Optional[List[str]] = None
    location_filter: Optional[List[str]] = None
    max_creators_in_segment: Optional[int] = None
    custom_payout_per_post: Optional[Decimal] = None
    custom_deliverable_count: Optional[int] = None


class CampaignSegmentCreate(CampaignSegmentBase):
    pass


class CampaignSegmentResponse(CampaignSegmentBase):
    id: UUID
    campaign_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# GMV Bonus Tier Schemas
class GMVBonusTierBase(BaseModel):
    tier_name: str = Field(..., max_length=100)
    min_gmv: Decimal
    max_gmv: Optional[Decimal] = None
    bonus_type: str  # 'flat' or 'percentage'
    bonus_value: Decimal
    
    @field_validator('bonus_type', mode='before')
    def validate_bonus_type(cls, v):
        if v not in ['flat', 'percentage']:
            raise ValueError("bonus_type must be 'flat' or 'percentage'")
        return v


class GMVBonusTierCreate(GMVBonusTierBase):
    pass


class GMVBonusTierResponse(GMVBonusTierBase):
    id: UUID
    campaign_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Leaderboard Bonus Schemas
class LeaderboardBonusBase(BaseModel):
    position_start: int = Field(..., ge=1)
    position_end: int = Field(..., ge=1)
    bonus_amount: Decimal
    metric_type: str  # 'gmv', 'posts', 'engagement'
    description: Optional[str] = None
    
    @field_validator('metric_type', mode='before')
    def validate_metric_type(cls, v):
        if v not in ['gmv', 'posts', 'engagement']:
            raise ValueError("metric_type must be 'gmv', 'posts', or 'engagement'")
        return v
    
    @model_validator(mode='after')
    def validate_positions(self):
        if self.position_end < self.position_start:
            raise ValueError("position_end must be greater than or equal to position_start")
        return self


class LeaderboardBonusCreate(LeaderboardBonusBase):
    pass


class LeaderboardBonusResponse(LeaderboardBonusBase):
    id: UUID
    campaign_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class CampaignListResponse(BaseModel):
    """Response schema for paginated campaign list"""
    campaigns: List[CampaignResponse]
    total: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v else None
        }
