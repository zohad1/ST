# app/api/endpoints/dashboard.py - Working version without relationship dependencies
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
import logging
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.models.campaign import Campaign, CampaignApplication, Deliverable
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dashboard"])


@router.get("/analytics")
async def get_dashboard_analytics(
    timeframe: str = Query("last_30_days"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics data from database."""
    try:
        logger.info(f"Fetching real analytics for timeframe: {timeframe}")
        
        # Calculate date range
        end_date_calc = datetime.utcnow()
        if timeframe == "last_7_days":
            start_date_calc = end_date_calc - timedelta(days=7)
        elif timeframe == "last_30_days":
            start_date_calc = end_date_calc - timedelta(days=30)
        elif timeframe == "last_90_days":
            start_date_calc = end_date_calc - timedelta(days=90)
        else:
            start_date_calc = start_date or (end_date_calc - timedelta(days=30))
            end_date_calc = end_date or end_date_calc

        # Previous period for growth calculation
        period_duration = end_date_calc - start_date_calc
        previous_start = start_date_calc - period_duration
        previous_end = start_date_calc

        # Get current period campaigns
        current_campaigns = db.query(Campaign).filter(
            Campaign.created_at >= start_date_calc,
            Campaign.created_at <= end_date_calc
        ).all()

        # Get previous period campaigns
        previous_campaigns = db.query(Campaign).filter(
            Campaign.created_at >= previous_start,
            Campaign.created_at <= previous_end
        ).all()

        # Calculate current metrics
        current_total_gmv = sum(float(c.current_gmv or 0) for c in current_campaigns)
        current_total_views = sum(c.total_views or 0 for c in current_campaigns)
        current_total_engagement = sum(c.total_engagement or 0 for c in current_campaigns)
        current_active_campaigns = len([c for c in current_campaigns if c.status == "active"])

        # Calculate previous metrics
        previous_total_gmv = sum(float(c.current_gmv or 0) for c in previous_campaigns)
        previous_total_views = sum(c.total_views or 0 for c in previous_campaigns)
        previous_total_engagement = sum(c.total_engagement or 0 for c in previous_campaigns)
        previous_active_campaigns = len([c for c in previous_campaigns if c.status == "active"])

        # Get active creators count
        current_active_creators = 0
        if current_campaigns:
            campaign_ids = [c.id for c in current_campaigns]
            current_active_creators = db.query(CampaignApplication.creator_id).filter(
                CampaignApplication.campaign_id.in_(campaign_ids),
                CampaignApplication.status == "approved"
            ).distinct().count()

        previous_active_creators = 0
        if previous_campaigns:
            prev_campaign_ids = [c.id for c in previous_campaigns]
            previous_active_creators = db.query(CampaignApplication.creator_id).filter(
                CampaignApplication.campaign_id.in_(prev_campaign_ids),
                CampaignApplication.status == "approved"
            ).distinct().count()

        # Helper function to calculate growth
        def calculate_growth(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return ((current - previous) / previous) * 100

        def get_trend(growth):
            if growth > 5:
                return "up"
            elif growth < -5:
                return "down"
            else:
                return "stable"

        # Calculate rates
        current_engagement_rate = (current_total_engagement / current_total_views * 100) if current_total_views > 0 else 0
        previous_engagement_rate = (previous_total_engagement / previous_total_views * 100) if previous_total_views > 0 else 0

        # Build KPIs with growth
        gmv_growth = calculate_growth(current_total_gmv, previous_total_gmv)
        views_growth = calculate_growth(current_total_views, previous_total_views)
        engagement_growth = calculate_growth(current_total_engagement, previous_total_engagement)
        campaigns_growth = calculate_growth(current_active_campaigns, previous_active_campaigns)
        creators_growth = calculate_growth(current_active_creators, previous_active_creators)
        engagement_rate_growth = calculate_growth(current_engagement_rate, previous_engagement_rate)

        # Get recent campaigns for display
        recent_campaigns = []
        for campaign in db.query(Campaign).order_by(desc(Campaign.created_at)).limit(5).all():
            progress = 0
            if campaign.target_gmv and campaign.target_gmv > 0:
                progress = min(100, (float(campaign.current_gmv or 0) / float(campaign.target_gmv)) * 100)
            
            recent_campaigns.append({
                "id": str(campaign.id),
                "name": campaign.name,
                "status": campaign.status,
                "progress": progress,
                "target_gmv": float(campaign.target_gmv) if campaign.target_gmv else None,
                "current_gmv": float(campaign.current_gmv) if campaign.current_gmv else None,
                "target_creators": campaign.target_creators,
                "current_creators": campaign.current_creators,
                "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                "end_date": campaign.end_date.isoformat() if campaign.end_date else None
            })

        # Get top creators with manual join
        top_creators = []
        # Query applications with creator info
        applications_with_creators = db.query(
            CampaignApplication,
            User
        ).join(
            User, CampaignApplication.creator_id == User.id
        ).filter(
            CampaignApplication.status == "approved"
        ).order_by(
            desc(CampaignApplication.previous_gmv)
        ).limit(10).all()

        for i, (app, creator) in enumerate(applications_with_creators):
            if creator:
                top_creators.append({
                    "id": str(creator.id),
                    "first_name": getattr(creator, 'first_name', 'Unknown'),
                    "last_name": getattr(creator, 'last_name', ''),
                    "username": creator.username,
                    "total_gmv": float(app.previous_gmv) if app.previous_gmv else 0,
                    "total_posts": 0,
                    "engagement_rate": float(app.engagement_rate) if app.engagement_rate else 0,
                    "consistency_score": 0,
                    "rank": i + 1
                })

        result = {
            "kpis": {
                "total_gmv": {
                    "value": current_total_gmv,
                    "growth": gmv_growth,
                    "trend": get_trend(gmv_growth)
                },
                "total_views": {
                    "value": current_total_views,
                    "growth": views_growth,
                    "trend": get_trend(views_growth)
                },
                "total_engagement": {
                    "value": current_total_engagement,
                    "growth": engagement_growth,
                    "trend": get_trend(engagement_growth)
                },
                "active_campaigns": {
                    "value": current_active_campaigns,
                    "growth": campaigns_growth,
                    "trend": get_trend(campaigns_growth)
                },
                "active_creators": {
                    "value": current_active_creators,
                    "growth": creators_growth,
                    "trend": get_trend(creators_growth)
                },
                "avg_engagement_rate": {
                    "value": current_engagement_rate,
                    "growth": engagement_rate_growth,
                    "trend": get_trend(engagement_rate_growth)
                },
                "conversion_rate": {
                    "value": 0,
                    "growth": 0,
                    "trend": "stable"
                },
                "roi": {
                    "value": 0,
                    "growth": 0,
                    "trend": "stable"
                }
            },
            "recent_campaigns": recent_campaigns,
            "top_creators": top_creators,
            "period_start": start_date_calc.isoformat(),
            "period_end": end_date_calc.isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }

        logger.info(f"Returning real analytics: {len(recent_campaigns)} campaigns, {len(top_creators)} creators")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard analytics: {str(e)}"
        )


@router.get("/campaigns")
async def get_dashboard_campaigns(
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get real campaigns from database."""
    try:
        logger.info(f"Fetching real campaigns with status: {status}, limit: {limit}, offset: {offset}")
        
        # Build query
        query = db.query(Campaign)
        
        # Filter by status if provided
        if status:
            query = query.filter(Campaign.status == status)

        # Apply pagination and ordering
        campaigns = query.order_by(desc(Campaign.created_at)).offset(offset).limit(limit).all()

        # Convert to response format
        result = []
        for campaign in campaigns:
            result.append({
                "id": str(campaign.id),
                "name": campaign.name,
                "description": campaign.description,
                "status": campaign.status,
                "type": getattr(campaign, 'type', 'performance'),
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

        logger.info(f"Returning {len(result)} real campaigns from database")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )


@router.get("/creator-performance")
async def get_creator_performance(
    campaign_id: Optional[str] = Query(None),
    timeframe: str = Query("last_30_days"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get real creator performance metrics from database."""
    try:
        logger.info(f"Fetching real creator performance for campaign: {campaign_id}, timeframe: {timeframe}")
        
        # Calculate date range
        end_date = datetime.utcnow()
        if timeframe == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif timeframe == "last_30_days":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "last_90_days":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)

        # Build query for applications with creator info
        query = db.query(
            CampaignApplication,
            User
        ).join(
            User, CampaignApplication.creator_id == User.id
        ).filter(
            CampaignApplication.status == "approved",
            CampaignApplication.applied_at >= start_date
        )

        # Filter by campaign if provided
        if campaign_id:
            try:
                campaign_uuid = UUID(campaign_id)
                query = query.filter(CampaignApplication.campaign_id == campaign_uuid)
            except ValueError:
                logger.warning(f"Invalid campaign_id format: {campaign_id}")
                return []

        # Get applications and order by GMV
        applications_with_creators = query.order_by(
            desc(CampaignApplication.previous_gmv)
        ).limit(limit).all()

        result = []
        for i, (app, creator) in enumerate(applications_with_creators):
            if creator:
                # Get deliverables for this creator
                deliverables = db.query(Deliverable).filter(
                    Deliverable.campaign_id == app.campaign_id,
                    Deliverable.creator_id == app.creator_id
                ).all()

                total_posts = len(deliverables)
                total_views = sum(d.views or 0 for d in deliverables)
                total_engagement = sum((d.likes or 0) + (d.comments or 0) + (d.shares or 0) for d in deliverables)
                total_gmv = sum(float(d.gmv_generated or 0) for d in deliverables)

                engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else float(app.engagement_rate or 0)

                result.append({
                    "creator_id": str(creator.id),
                    "campaign_id": str(app.campaign_id) if app.campaign_id else None,
                    "total_posts": total_posts,
                    "total_gmv": total_gmv,
                    "total_views": total_views,
                    "total_engagement": total_engagement,
                    "engagement_rate": engagement_rate,
                    "conversion_rate": 0,
                    "consistency_score": 0,
                    "gmv_rank": i + 1,
                    "engagement_rank": None,
                    "last_calculated": datetime.utcnow().isoformat(),
                    "creator": {
                        "id": str(creator.id),
                        "first_name": getattr(creator, 'first_name', 'Unknown'),
                        "last_name": getattr(creator, 'last_name', ''),
                        "username": creator.username,
                        "total_gmv": total_gmv,
                        "total_posts": total_posts,
                        "engagement_rate": engagement_rate,
                        "rank": i + 1
                    }
                })

        logger.info(f"Returning {len(result)} real creator performance records from database")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching creator performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch creator performance: {str(e)}"
        )