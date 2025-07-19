# app/models/analytics.py
import uuid
import datetime
from decimal import Decimal

from sqlalchemy import Column, String, Date, DateTime, Integer, DECIMAL, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class CampaignPerformanceDaily(Base):
    __tablename__ = "campaign_performance_daily"
    __table_args__ = {'schema': 'analytics'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), nullable=False)  # Reference to campaigns.campaigns.id
    date_snapshot = Column(Date, nullable=False)
    
    # Creator metrics
    total_creators = Column(Integer, default=0)
    active_creators = Column(Integer, default=0)
    new_applications = Column(Integer, default=0)
    approved_applications = Column(Integer, default=0)
    
    # Content metrics
    posts_submitted = Column(Integer, default=0)
    posts_approved = Column(Integer, default=0)
    total_views = Column(BigInteger, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    
    # Financial metrics
    total_gmv = Column(DECIMAL(12,2), default=0.00)
    total_commissions = Column(DECIMAL(10,2), default=0.00)
    total_payouts = Column(DECIMAL(10,2), default=0.00)
    
    # Performance indicators
    avg_engagement_rate = Column(DECIMAL(5,2), default=0.00)
    conversion_rate = Column(DECIMAL(5,2), default=0.00)
    cost_per_acquisition = Column(DECIMAL(10,2), default=0.00)
    
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<CampaignPerformanceDaily(campaign_id={self.campaign_id}, date={self.date_snapshot})>"


class CreatorPerformance(Base):
    __tablename__ = "creator_performance"
    __table_args__ = {'schema': 'analytics'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False)  # Reference to users.users.id
    campaign_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to campaigns.campaigns.id (optional for overall performance)
    
    # Performance metrics
    total_posts = Column(Integer, default=0)
    completed_deliverables = Column(Integer, default=0)
    on_time_deliverables = Column(Integer, default=0)
    total_gmv = Column(DECIMAL(12,2), default=0.00)
    avg_views_per_post = Column(DECIMAL(12,2), default=0.00)
    avg_engagement_rate = Column(DECIMAL(5,2), default=0.00)
    
    # Consistency scoring
    consistency_score = Column(DECIMAL(3,2), default=0.00)  # 0.0 to 1.0
    reliability_rating = Column(DECIMAL(2,1), default=0.0)  # 0.0 to 5.0
    
    # Calculated at
    last_calculated = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<CreatorPerformance(creator_id={self.creator_id}, campaign_id={self.campaign_id})>"