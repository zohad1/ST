# app/services/dashboard_service.py - REAL database implementation
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.campaign import Campaign, CampaignApplication, Deliverable, CampaignStatus
from app.models.user import User

# Create simple enum for timeframe if schemas don't exist
class AnalyticsTimeframe:
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days" 
    LAST_90_DAYS = "last_90_days"
    CUSTOM = "custom"

logger = logging.getLogger(__name__)


class DashboardService:
    def _get_date_range(self, timeframe: AnalyticsTimeframe, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Get start and end dates based on timeframe."""
        now = datetime.utcnow()
        
        if timeframe == AnalyticsTimeframe.CUSTOM:
            if not start_date or not end_date:
                raise ValueError("Start and end dates required for custom timeframe")
            return start_date, end_date
        
        elif timeframe == AnalyticsTimeframe.LAST_7_DAYS:
            start = now - timedelta(days=7)
            return start, now
        
        elif timeframe == AnalyticsTimeframe.LAST_30_DAYS:
            start = now - timedelta(days=30)
            return start, now
        
        elif timeframe == AnalyticsTimeframe.LAST_90_DAYS:
            start = now - timedelta(days=90)
            return start, now
        
        else:
            # Default to last 30 days
            start = now - timedelta(days=30)
            return start, now

    def _calculate_growth(self, current_value: float, previous_value: float) -> float:
        """Calculate percentage growth."""
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        return ((current_value - previous_value) / previous_value) * 100

    def _get_trend(self, growth: float) -> str:
        """Get trend direction based on growth."""
        if growth > 5:
            return "up"
        elif growth < -5:
            return "down"
        else:
            return "stable"

    async def get_dashboard_analytics(
        self, 
        db: Session, 
        user_id: str,
        timeframe: str = "last_30_days",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get real dashboard analytics from database."""
        
        try:
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")

            # Calculate date range
            if timeframe == "last_7_days":
                period_start = datetime.utcnow() - timedelta(days=7)
                period_end = datetime.utcnow()
            elif timeframe == "last_30_days":
                period_start = datetime.utcnow() - timedelta(days=30)
                period_end = datetime.utcnow()
            elif timeframe == "last_90_days":
                period_start = datetime.utcnow() - timedelta(days=90)
                period_end = datetime.utcnow()
            else:
                period_start = start_date or (datetime.utcnow() - timedelta(days=30))
                period_end = end_date or datetime.utcnow()

            # Previous period for growth calculation
            period_duration = period_end - period_start
            previous_start = period_start - period_duration
            previous_end = period_start

            # Get campaigns based on user role
            if user.role == "agency":
                campaigns_query = db.query(Campaign).filter(Campaign.agency_id == user.id)
            elif user.role == "brand":
                campaigns_query = db.query(Campaign).filter(Campaign.brand_id == user.id)
            else:
                # For other roles, get all campaigns they have access to
                campaigns_query = db.query(Campaign)

            # Current period campaigns
            current_campaigns = campaigns_query.filter(
                Campaign.created_at >= period_start,
                Campaign.created_at <= period_end
            ).all()

            # Previous period campaigns
            previous_campaigns = campaigns_query.filter(
                Campaign.created_at >= previous_start,
                Campaign.created_at <= previous_end
            ).all()

            # Calculate current metrics
            current_total_gmv = sum(c.current_gmv or 0 for c in current_campaigns)
            current_total_views = sum(c.total_views or 0 for c in current_campaigns)
            current_total_engagement = sum(c.total_engagement or 0 for c in current_campaigns)
            current_active_campaigns = len([c for c in current_campaigns if c.status == CampaignStatus.ACTIVE])

            # Calculate previous metrics
            previous_total_gmv = sum(c.current_gmv or 0 for c in previous_campaigns)
            previous_total_views = sum(c.total_views or 0 for c in previous_campaigns)
            previous_total_engagement = sum(c.total_engagement or 0 for c in previous_campaigns)
            previous_active_campaigns = len([c for c in previous_campaigns if c.status == CampaignStatus.ACTIVE])

            # Get active creators count
            if current_campaigns:
                campaign_ids = [c.id for c in current_campaigns]
                current_active_creators = db.query(CampaignApplication.creator_id).filter(
                    CampaignApplication.campaign_id.in_(campaign_ids),
                    CampaignApplication.status == "approved"
                ).distinct().count()
            else:
                current_active_creators = 0

            if previous_campaigns:
                prev_campaign_ids = [c.id for c in previous_campaigns]
                previous_active_creators = db.query(CampaignApplication.creator_id).filter(
                    CampaignApplication.campaign_id.in_(prev_campaign_ids),
                    CampaignApplication.status == "approved"
                ).distinct().count()
            else:
                previous_active_creators = 0

            # Calculate rates
            current_engagement_rate = (current_total_engagement / current_total_views * 100) if current_total_views > 0 else 0
            previous_engagement_rate = (previous_total_engagement / previous_total_views * 100) if previous_total_views > 0 else 0

            # Build KPIs with growth
            kpis = {
                "total_gmv": {
                    "value": current_total_gmv,
                    "growth": self._calculate_growth(current_total_gmv, previous_total_gmv),
                    "trend": self._get_trend(self._calculate_growth(current_total_gmv, previous_total_gmv))
                },
                "total_views": {
                    "value": current_total_views,
                    "growth": self._calculate_growth(current_total_views, previous_total_views),
                    "trend": self._get_trend(self._calculate_growth(current_total_views, previous_total_views))
                },
                "total_engagement": {
                    "value": current_total_engagement,
                    "growth": self._calculate_growth(current_total_engagement, previous_total_engagement),
                    "trend": self._get_trend(self._calculate_growth(current_total_engagement, previous_total_engagement))
                },
                "active_campaigns": {
                    "value": current_active_campaigns,
                    "growth": self._calculate_growth(current_active_campaigns, previous_active_campaigns),
                    "trend": self._get_trend(self._calculate_growth(current_active_campaigns, previous_active_campaigns))
                },
                "active_creators": {
                    "value": current_active_creators,
                    "growth": self._calculate_growth(current_active_creators, previous_active_creators),
                    "trend": self._get_trend(self._calculate_growth(current_active_creators, previous_active_creators))
                },
                "avg_engagement_rate": {
                    "value": current_engagement_rate,
                    "growth": self._calculate_growth(current_engagement_rate, previous_engagement_rate),
                    "trend": self._get_trend(self._calculate_growth(current_engagement_rate, previous_engagement_rate))
                },
                "conversion_rate": {
                    "value": 0,  # TODO: Implement conversion tracking
                    "growth": 0,
                    "trend": "stable"
                },
                "roi": {
                    "value": 0,  # TODO: Implement ROI calculation
                    "growth": 0,
                    "trend": "stable"
                }
            }

            # Get recent campaigns (limit 5)
            recent_campaigns = []
            for campaign in current_campaigns[:5]:
                progress = 0
                if campaign.target_gmv and campaign.target_gmv > 0:
                    progress = min(100, (float(campaign.current_gmv or 0) / float(campaign.target_gmv)) * 100)
                
                recent_campaigns.append({
                    "id": str(campaign.id),
                    "name": campaign.name,
                    "status": campaign.status.value if campaign.status else "draft",
                    "progress": progress,
                    "target_gmv": float(campaign.target_gmv) if campaign.target_gmv else None,
                    "current_gmv": float(campaign.current_gmv) if campaign.current_gmv else None,
                    "target_creators": campaign.target_creators,
                    "current_creators": campaign.current_creators,
                    "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                    "end_date": campaign.end_date.isoformat() if campaign.end_date else None
                })

            # Get top creators (this would need a proper query, for now simplified)
            top_creators = []
            if current_campaigns:
                campaign_ids = [c.id for c in current_campaigns]
                
                # Get top creators by applications (simplified)
                top_applications = db.query(CampaignApplication).join(User).filter(
                    CampaignApplication.campaign_id.in_(campaign_ids),
                    CampaignApplication.status == "approved"
                ).order_by(desc(CampaignApplication.previous_gmv)).limit(10).all()

                for i, app in enumerate(top_applications):
                    creator = app.creator
                    top_creators.append({
                        "id": str(creator.id),
                        "first_name": getattr(creator, 'first_name', 'Unknown'),
                        "last_name": getattr(creator, 'last_name', ''),
                        "username": creator.username,
                        "total_gmv": float(app.previous_gmv) if app.previous_gmv else 0,
                        "total_posts": 0,  # Would need to calculate from deliverables
                        "engagement_rate": float(app.engagement_rate) if app.engagement_rate else 0,
                        "consistency_score": 0,  # Would need to calculate
                        "rank": i + 1
                    })

            return {
                "kpis": kpis,
                "recent_campaigns": recent_campaigns,
                "top_creators": top_creators,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching dashboard analytics: {str(e)}")
            raise

    async def get_campaigns(
        self,
        db: Session,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get real campaigns from database."""
        
        try:
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")

            # Build query based on user role
            if user.role == "agency":
                query = db.query(Campaign).filter(Campaign.agency_id == user.id)
            elif user.role == "brand":
                query = db.query(Campaign).filter(Campaign.brand_id == user.id)
            else:
                # For creators, get campaigns they're approved for
                approved_campaign_ids = db.query(CampaignApplication.campaign_id).filter(
                    CampaignApplication.creator_id == user.id,
                    CampaignApplication.status == "approved"
                ).subquery()
                query = db.query(Campaign).filter(Campaign.id.in_(approved_campaign_ids))

            # Filter by status if provided
            if status:
                try:
                    status_enum = CampaignStatus(status)
                    query = query.filter(Campaign.status == status_enum)
                except ValueError:
                    # Invalid status, return empty
                    return []

            # Apply pagination and ordering
            campaigns = query.order_by(desc(Campaign.created_at)).offset(offset).limit(limit).all()

            # Convert to response format
            result = []
            for campaign in campaigns:
                result.append({
                    "id": str(campaign.id),
                    "name": campaign.name,
                    "description": campaign.description,
                    "status": campaign.status.value if campaign.status else "draft",
                    "type": campaign.type.value if campaign.type else "performance",
                    "budget": float(campaign.budget) if campaign.budget else None,
                    "target_gmv": float(campaign.target_gmv) if campaign.target_gmv else None,
                    "current_gmv": float(campaign.current_gmv) if campaign.current_gmv else None,
                    "target_creators": campaign.target_creators,
                    "current_creators": campaign.current_creators,
                    "target_posts": campaign.target_posts,
                    "current_posts": campaign.current_posts,
                    "total_views": campaign.total_views,
                    "total_engagement": campaign.total_engagement,
                    "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                    "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                    "created_at": campaign.created_at.isoformat(),
                    "updated_at": campaign.updated_at.isoformat()
                })

            return result

        except Exception as e:
            logger.error(f"Error fetching campaigns: {str(e)}")
            raise

    async def get_creator_performance(
        self,
        db: Session,
        user_id: str,
        campaign_id: Optional[str] = None,
        timeframe: str = "last_30_days",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get real creator performance from database."""
        
        try:
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")

            # Calculate date range
            if timeframe == "last_7_days":
                start_date = datetime.utcnow() - timedelta(days=7)
            elif timeframe == "last_30_days":
                start_date = datetime.utcnow() - timedelta(days=30)
            elif timeframe == "last_90_days":
                start_date = datetime.utcnow() - timedelta(days=90)
            else:
                start_date = datetime.utcnow() - timedelta(days=30)

            # Get campaigns user has access to
            if user.role == "agency":
                campaign_ids_query = db.query(Campaign.id).filter(Campaign.agency_id == user.id)
            elif user.role == "brand":
                campaign_ids_query = db.query(Campaign.id).filter(Campaign.brand_id == user.id)
            else:
                campaign_ids_query = db.query(CampaignApplication.campaign_id).filter(
                    CampaignApplication.creator_id == user.id,
                    CampaignApplication.status == "approved"
                )

            if campaign_id:
                campaign_ids_query = campaign_ids_query.filter(Campaign.id == campaign_id)

            campaign_ids = [row[0] for row in campaign_ids_query.all()]

            if not campaign_ids:
                return []

            # Get creators with applications in these campaigns
            creators_query = db.query(CampaignApplication).join(User).filter(
                CampaignApplication.campaign_id.in_(campaign_ids),
                CampaignApplication.status == "approved",
                CampaignApplication.applied_at >= start_date
            ).order_by(desc(CampaignApplication.previous_gmv)).limit(limit)

            applications = creators_query.all()

            result = []
            for i, app in enumerate(applications):
                creator = app.creator
                
                # Get deliverables for this creator in this campaign
                deliverables = db.query(Deliverable).filter(
                    Deliverable.campaign_id == app.campaign_id,
                    Deliverable.creator_id == app.creator_id
                ).all()

                total_posts = len(deliverables)
                total_views = sum(d.views or 0 for d in deliverables)
                total_engagement = sum((d.likes or 0) + (d.comments or 0) + (d.shares or 0) for d in deliverables)
                total_gmv = sum(d.gmv_generated or 0 for d in deliverables)

                engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0

                result.append({
                    "creator_id": str(creator.id),
                    "campaign_id": str(app.campaign_id) if app.campaign_id else None,
                    "total_posts": total_posts,
                    "total_gmv": float(total_gmv),
                    "total_views": total_views,
                    "total_engagement": total_engagement,
                    "engagement_rate": engagement_rate,
                    "conversion_rate": 0,  # TODO: Calculate conversion rate
                    "consistency_score": 0,  # TODO: Calculate consistency
                    "gmv_rank": i + 1,
                    "engagement_rank": None,
                    "last_calculated": datetime.utcnow().isoformat(),
                    "creator": {
                        "id": str(creator.id),
                        "first_name": getattr(creator, 'first_name', 'Unknown'),
                        "last_name": getattr(creator, 'last_name', ''),
                        "username": creator.username,
                        "total_gmv": float(total_gmv),
                        "total_posts": total_posts,
                        "engagement_rate": engagement_rate,
                        "rank": i + 1
                    }
                })

            return result

        except Exception as e:
            logger.error(f"Error fetching creator performance: {str(e)}")
            raise


# Create service instance
dashboard_service = DashboardService()