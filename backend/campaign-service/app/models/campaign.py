# app/models/campaign.py - Updated with relationships
from sqlalchemy import Column, String, Text, DateTime, Numeric, Integer, Boolean, ForeignKey, event, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.models.base import Base


# Enums updated for PostgreSQL compatibility
class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active" 
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, enum.Enum):
    PERFORMANCE = "performance"
    AWARENESS = "awareness"
    CONVERSION = "conversion"
    HYBRID = "hybrid"


class PayoutModel(str, enum.Enum):
    FIXED_PER_POST = "fixed_per_post"
    GMV_COMMISSION = "gmv_commission"
    HYBRID = "hybrid"
    RETAINER_GMV = "retainer_gmv"


class TrackingMethod(str, enum.Enum):
    HASHTAG = "hashtag"
    PRODUCT_LINK = "product_link"
    SPARK_CODE = "spark_code"


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WAITLISTED = "waitlisted"


class DeliverableStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERDUE = "overdue"


# Campaign model WITH relationships
class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = {'schema': 'campaigns'}

    # All existing fields remain exactly the same
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id = Column(UUID(as_uuid=True), nullable=False)
    brand_id = Column(UUID(as_uuid=True))
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    thumbnail_url = Column(Text)
    
    status = Column(String(50), default="draft")
    type = Column(String(50), default="performance")
    payout_model = Column(String(50), nullable=False)
    tracking_method = Column(String(50), nullable=False)
    
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    grace_period_days = Column(Integer, default=0)
    is_rolling_30_day = Column(Boolean, default=False)
    
    max_creators = Column(Integer)
    min_deliverables_per_creator = Column(Integer, default=1)
    require_approval = Column(Boolean, default=True)
    require_discord_join = Column(Boolean, default=False)
    discord_server_id = Column(String(100))
    discord_role_name = Column(String(100))
    
    base_payout_per_post = Column(Numeric(10, 2), default=0.00)
    gmv_commission_rate = Column(Numeric(5, 2), default=0.00)
    retainer_amount = Column(Numeric(10, 2), default=0.00)
    
    budget = Column(Numeric(12, 2))
    total_budget = Column(Numeric(12, 2))
    spent_amount = Column(Numeric(12, 2), default=0.00)
    
    hashtag = Column(String(100))
    tiktok_product_links = Column(JSONB)
    
    target_gmv = Column(Numeric(12, 2))
    target_posts = Column(Integer)
    target_views = Column(Integer)
    target_creators = Column(Integer)
    
    current_gmv = Column(Numeric(12, 2), default=0.00)
    current_posts = Column(Integer, default=0)
    current_creators = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    
    referral_bonus_enabled = Column(Boolean, default=False)
    referral_bonus_amount = Column(Numeric(10, 2), default=0.00)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ADD RELATIONSHIPS
    applications = relationship("CampaignApplication", back_populates="campaign", lazy="select")
    segments = relationship("CampaignSegment", back_populates="campaign", lazy="select")
    deliverables = relationship("Deliverable", back_populates="campaign", lazy="select")
    gmv_bonus_tiers = relationship("GMVBonusTier", back_populates="campaign", lazy="select")
    leaderboard_bonuses = relationship("LeaderboardBonus", back_populates="campaign", lazy="select")
    
    def __init__(self, **kwargs):
        """Custom init to handle the 'null' string issue"""
        if 'tiktok_product_links' in kwargs:
            if kwargs['tiktok_product_links'] == 'null' or kwargs['tiktok_product_links'] == '':
                kwargs['tiktok_product_links'] = None
        
        # Set defaults for numeric fields
        numeric_defaults = {
            'spent_amount': 0.00,
            'current_gmv': 0.00,
            'current_posts': 0,
            'current_creators': 0,
            'total_views': 0,
            'total_engagement': 0,
            'base_payout_per_post': 0.00,
            'gmv_commission_rate': 0.00,
            'retainer_amount': 0.00,
            'referral_bonus_amount': 0.00
        }
        
        for field, default in numeric_defaults.items():
            if field not in kwargs or kwargs[field] is None:
                kwargs[field] = default
        
        if 'status' not in kwargs:
            kwargs['status'] = 'draft'
        if 'type' not in kwargs:
            kwargs['type'] = 'performance'
            
        super().__init__(**kwargs)
    
    def __setattr__(self, key, value):
        """Override setattr to catch 'null' string assignments"""
        if key == 'tiktok_product_links' and value == 'null':
            value = None
        super().__setattr__(key, value)


# Event listeners remain the same
@event.listens_for(Campaign, 'before_insert')
@event.listens_for(Campaign, 'before_update')
def clean_campaign_data(mapper, connection, target):
    """Clean up campaign data before saving to database"""
    if hasattr(target, 'tiktok_product_links'):
        if target.tiktok_product_links == 'null' or target.tiktok_product_links == '':
            target.tiktok_product_links = None
    
    if hasattr(target, 'budget') and hasattr(target, 'total_budget'):
        if target.budget is not None and target.total_budget is None:
            target.total_budget = target.budget
        elif target.total_budget is not None and target.budget is None:
            target.budget = target.total_budget


# CampaignApplication model WITH relationships
class CampaignApplication(Base):
    __tablename__ = "creator_applications"
    __table_args__ = {'schema': 'campaigns'}

    # Basic fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)  # Add FK
    segment_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaign_segments.id"))
    
    # Status as STRING
    status = Column(String(50), default="pending")
    applied_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.users.id"))  # Add FK
    
    # Application data
    application_data = Column(JSONB)
    follower_count = Column(Integer, default=0)
    engagement_rate = Column(Numeric(5, 2), default=0.00)
    previous_gmv = Column(Numeric(12, 2), default=0.00)
    application_message = Column(Text)
    response_message = Column(Text)
    rejection_reason = Column(Text)  # Add for frontend compatibility
    review_notes = Column(Text)      # Add for frontend compatibility
    
    # ADD RELATIONSHIPS - THIS IS CRITICAL FOR LOADING CREATOR DATA
    campaign = relationship("Campaign", back_populates="applications")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="campaign_applications")
    reviewer = relationship("User", foreign_keys=[reviewed_by], back_populates="reviewed_applications")
    segment = relationship("CampaignSegment", back_populates="applications")
    deliverables = relationship("Deliverable", back_populates="application", lazy="select")


# Deliverable model WITH relationships
class Deliverable(Base):
    __tablename__ = "deliverables"
    __table_args__ = {'schema': 'campaigns'}

    # Basic fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.creator_applications.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)  # Add FK
    
    deliverable_number = Column(Integer, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    due_date = Column(DateTime)
    status = Column(String(50), default="pending")
    
    content_url = Column(Text)
    content_type = Column(String(50))
    tiktok_post_url = Column(Text)
    post_caption = Column(Text)
    hashtags_used = Column(ARRAY(String))
    
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.users.id"))  # Add FK
    published_at = Column(DateTime)
    
    feedback = Column(Text)
    agency_feedback = Column(Text)
    revision_requested = Column(Boolean, default=False)
    revision_notes = Column(Text)
    
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    gmv_generated = Column(Numeric(12, 2), default=0.00)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ADD RELATIONSHIPS
    campaign = relationship("Campaign", back_populates="deliverables")
    application = relationship("CampaignApplication", back_populates="deliverables")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="deliverables")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_deliverables")


# Event listeners remain the same
@event.listens_for(Deliverable, 'before_insert')
@event.listens_for(Deliverable, 'before_update')
def clean_deliverable_data(mapper, connection, target):
    """Clean up deliverable data before saving to database"""
    # Handle hashtags_used field
    if hasattr(target, 'hashtags_used'):
        if target.hashtags_used is None:
            target.hashtags_used = []
        elif isinstance(target.hashtags_used, str):
            # If it's a string, try to parse it as JSON
            import json
            try:
                if target.hashtags_used == '[]':
                    target.hashtags_used = []
                else:
                    parsed = json.loads(target.hashtags_used)
                    # Ensure it's a list of strings
                    if isinstance(parsed, list):
                        target.hashtags_used = [str(item) for item in parsed]
                    else:
                        target.hashtags_used = []
            except (json.JSONDecodeError, TypeError):
                target.hashtags_used = []
        elif isinstance(target.hashtags_used, list):
            # Ensure all items are strings
            target.hashtags_used = [str(item) for item in target.hashtags_used]
    
    # Handle other fields
    if hasattr(target, 'post_caption') and target.post_caption == '':
        target.post_caption = None


# CampaignSegment model WITH relationships
class CampaignSegment(Base):
    __tablename__ = "campaign_segments"
    __table_args__ = {'schema': 'campaigns'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=False)
    segment_name = Column(String(100), nullable=False)
    segment_description = Column(Text)
    
    gender_filter = Column(JSONB)
    age_min = Column(Integer)
    age_max = Column(Integer)
    min_followers = Column(Integer)
    max_followers = Column(Integer)
    required_niches = Column(JSONB)
    location_filter = Column(JSONB)
    
    max_creators_in_segment = Column(Integer)
    custom_payout_per_post = Column(Numeric(10, 2))
    custom_deliverable_count = Column(Integer)
    
    created_at = Column(DateTime, default=func.now())
    
    # ADD RELATIONSHIPS
    campaign = relationship("Campaign", back_populates="segments")
    applications = relationship("CampaignApplication", back_populates="segment")


# GMVBonusTier model WITH relationships
class GMVBonusTier(Base):
    __tablename__ = "gmv_bonus_tiers"
    __table_args__ = {'schema': 'campaigns'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=False)
    tier_name = Column(String(100), nullable=False)
    min_gmv = Column(Numeric(12, 2), nullable=False)
    max_gmv = Column(Numeric(12, 2))
    bonus_type = Column(String(20), nullable=False)
    bonus_value = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # ADD RELATIONSHIP
    campaign = relationship("Campaign", back_populates="gmv_bonus_tiers")


# LeaderboardBonus model WITH relationships
class LeaderboardBonus(Base):
    __tablename__ = "leaderboard_bonuses"
    __table_args__ = {'schema': 'campaigns'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=False)
    position_start = Column(Integer, nullable=False)
    position_end = Column(Integer, nullable=False)
    bonus_amount = Column(Numeric(10, 2), nullable=False)
    metric_type = Column(String(20), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # ADD RELATIONSHIP
    campaign = relationship("Campaign", back_populates="leaderboard_bonuses")