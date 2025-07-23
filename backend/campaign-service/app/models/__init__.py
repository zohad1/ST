# app/models/__init__.py
"""
Models package initialization.
Import all models to ensure they are registered with SQLAlchemy.
"""

# Import base first
from app.models.base import Base

# Import User model before Campaign models (to resolve circular dependencies)
from app.models.user import User, UserRole, GenderType

# Import Campaign models
from app.models.campaign import (
    Campaign,
    CampaignApplication,
    Deliverable,
    CampaignSegment,
    GMVBonusTier,
    LeaderboardBonus,
    CampaignStatus,
    CampaignType,
    PayoutModel,
    TrackingMethod,
    ApplicationStatus,
    DeliverableStatus
)

# Import analytics if exists
try:
    from app.models.analytics import (
        DashboardAnalytics,
        CreatorPerformance
    )
except ImportError:
    # Analytics model might not be implemented yet
    DashboardAnalytics = None
    CreatorPerformance = None

# Make all models available at package level
__all__ = [
    'Base',
    'User',
    'UserRole',
    'GenderType',
    'Campaign',
    'CampaignApplication',
    'Deliverable',
    'CampaignSegment',
    'GMVBonusTier',
    'LeaderboardBonus',
    'CampaignStatus',
    'CampaignType',
    'PayoutModel',
    'TrackingMethod',
    'ApplicationStatus',
    'DeliverableStatus',
    'DashboardAnalytics',
    'CreatorPerformance'
]

# Remove None values from __all__
__all__ = [item for item in __all__ if item is not None and globals().get(item) is not None]