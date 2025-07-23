# app/models/analytics.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, Decimal
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base  # Import Base properly


class DashboardAnalytics(Base):
    __tablename__ = "dashboard_analytics"
    __table_args__ = {'schema': 'analytics'}  # Add schema

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    date_snapshot = Column(DateTime, default=func.now())
    
    # KPI metrics
    total_gmv = Column(Decimal(12, 2), default=0.00)
    total_views = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    active_campaigns = Column(Integer, default=0)
    active_creators = Column(Integer, default=0)
    
    # Growth metrics
    gmv_growth = Column(Decimal(5, 2), default=0.00)
    views_growth = Column(Decimal(5, 2), default=0.00)
    engagement_growth = Column(Decimal(5, 2), default=0.00)
    creator_growth = Column(Decimal(5, 2), default=0.00)
    
    # Performance indicators
    avg_engagement_rate = Column(Decimal(5, 2), default=0.00)
    conversion_rate = Column(Decimal(5, 2), default=0.00)
    roi = Column(Decimal(5, 2), default=0.00)
    
    created_at = Column(DateTime, default=func.now())


class CreatorPerformance(Base):
    __tablename__ = "creator_performance"
    __table_args__ = {'schema': 'analytics'}  # Add schema

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"))
    
    # Performance metrics
    total_posts = Column(Integer, default=0)
    total_gmv = Column(Decimal(12, 2), default=0.00)
    total_views = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    
    # Rates
    engagement_rate = Column(Decimal(5, 2), default=0.00)
    conversion_rate = Column(Decimal(5, 2), default=0.00)
    consistency_score = Column(Decimal(5, 2), default=0.00)
    
    # Rankings
    gmv_rank = Column(Integer)
    engagement_rank = Column(Integer)
    consistency_rank = Column(Integer)
    
    # Period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    last_calculated = Column(DateTime, default=func.now())
    
    # Relationships - only if User model has these back_populates defined
    # creator = relationship("User", back_populates="performance_metrics")
    # campaign = relationship("Campaign")