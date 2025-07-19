# app/services/aggregation_service.py
import asyncio
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.crud.analytics import campaign_performance_crud, creator_performance_crud
from app.schemas.analytics import CampaignPerformanceDailyCreate, CreatorPerformanceUpdate
from app.external.campaign_service_client import CampaignServiceClient
from app.external.user_service_client import UserServiceClient
from app.external.payment_service_client import PaymentServiceClient
from app.external.integration_service_client import IntegrationServiceClient

logger = logging.getLogger(__name__)


class DataAggregationService:
    def __init__(self):
        self.campaign_client = CampaignServiceClient()
        self.user_client = UserServiceClient()
        self.payment_client = PaymentServiceClient()
        self.integration_client = IntegrationServiceClient()
    
    async def aggregate_daily_campaign_performance(self, target_date: Optional[date] = None) -> None:
        """Aggregate daily performance data for all campaigns"""
        if not target_date:
            target_date = date.today() - timedelta(days=1)  # Previous day
        
        logger.info(f"Starting daily campaign performance aggregation for {target_date}")
        
        db = SessionLocal()
        try:
            # Get all active campaigns (this would come from campaign service)
            active_campaigns = await self._get_active_campaigns()
            
            for campaign in active_campaigns:
                try:
                    await self._aggregate_campaign_daily_data(db, campaign['id'], target_date)
                except Exception as e:
                    logger.error(f"Error aggregating data for campaign {campaign['id']}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in daily aggregation: {e}")
        finally:
            db.close()
    
    async def _aggregate_campaign_daily_data(self, db: Session, campaign_id: UUID, target_date: date) -> None:
        """Aggregate daily data for a specific campaign"""
        logger.info(f"Aggregating daily data for campaign {campaign_id} on {target_date}")
        
        # Get campaign applications and deliverables
        applications = await self.campaign_client.get_campaign_applications(campaign_id)
        deliverables = await self.campaign_client.get_campaign_deliverables(campaign_id)
        
        # Filter data for target date
        target_datetime_start = datetime.combine(target_date, datetime.min.time())
        target_datetime_end = datetime.combine(target_date, datetime.max.time())
        
        # Calculate creator metrics
        total_creators = len(applications)
        active_creators = len([app for app in applications if app['status'] == 'approved'])
        new_applications = len([
            app for app in applications 
            if self._is_date_in_range(app.get('applied_at'), target_datetime_start, target_datetime_end)
        ])
        approved_applications = len([
            app for app in applications 
            if app['status'] == 'approved' and 
            self._is_date_in_range(app.get('reviewed_at'), target_datetime_start, target_datetime_end)
        ])
        
        # Calculate content metrics
        posts_submitted = len([
            d for d in deliverables 
            if self._is_date_in_range(d.get('submitted_at'), target_datetime_start, target_datetime_end)
        ])
        posts_approved = len([
            d for d in deliverables 
            if d['status'] == 'approved' and 
            self._is_date_in_range(d.get('approved_at'), target_datetime_start, target_datetime_end)
        ])
        
        # Calculate engagement metrics
        total_views = sum(d.get('views_count', 0) for d in deliverables)
        total_likes = sum(d.get('likes_count', 0) for d in deliverables)
        total_comments = sum(d.get('comments_count', 0) for d in deliverables)
        total_shares = sum(d.get('shares_count', 0) for d in deliverables)
        
        # Calculate financial metrics
        gmv_data = await self.integration_client.get_tiktok_gmv_data(campaign_id)
        daily_gmv = sum(
            Decimal(str(gmv['sale_amount'])) for gmv in gmv_data 
            if self._is_date_in_range(gmv.get('sale_date'), target_datetime_start, target_datetime_end)
        )
        
        payouts = await self.payment_client.get_campaign_payouts(campaign_id)
        daily_payouts = sum(
            Decimal(str(payout['amount'])) for payout in payouts 
            if payout['status'] == 'completed' and 
            self._is_date_in_range(payout.get('completed_at'), target_datetime_start, target_datetime_end)
        )
        
        # Calculate performance indicators
        avg_engagement_rate = Decimal('0.00')
        if total_views > 0:
            total_engagement = total_likes + total_comments + total_shares
            avg_engagement_rate = Decimal(str(total_engagement / total_views * 100))
        
        conversion_rate = Decimal('0.00')
        if total_views > 0 and daily_gmv > 0:
            # This is a simplified conversion rate calculation
            conversion_rate = Decimal(str(len(gmv_data) / total_views * 100))
        
        cost_per_acquisition = Decimal('0.00')
        if len(gmv_data) > 0:
            cost_per_acquisition = daily_payouts / len(gmv_data)
        
        # Create performance record
        performance_data = CampaignPerformanceDailyCreate(
            campaign_id=campaign_id,
            date_snapshot=target_date,
            total_creators=total_creators,
            active_creators=active_creators,
            new_applications=new_applications,
            approved_applications=approved_applications,
            posts_submitted=posts_submitted,
            posts_approved=posts_approved,
            total_views=total_views,
            total_likes=total_likes,
            total_comments=total_comments,
            total_shares=total_shares,
            total_gmv=daily_gmv,
            total_commissions=daily_gmv * Decimal('0.1'),  # Assuming 10% commission
            total_payouts=daily_payouts,
            avg_engagement_rate=avg_engagement_rate,
            conversion_rate=conversion_rate,
            cost_per_acquisition=cost_per_acquisition
        )
        
        # Save to database
        campaign_performance_crud.create_daily_performance(db, performance_data)
        logger.info(f"Successfully aggregated daily data for campaign {campaign_id}")
    
    async def update_creator_performance(self, creator_id: UUID, campaign_id: Optional[UUID] = None) -> None:
        """Update creator performance metrics"""
        logger.info(f"Updating performance for creator {creator_id}, campaign {campaign_id}")
        
        db = SessionLocal()
        try:
            # Get creator deliverables
            deliverables = await self.campaign_client.get_creator_deliverables(creator_id, campaign_id)
            
            # Get creator earnings
            earnings = await self.payment_client.get_creator_earnings(creator_id, campaign_id)
            
            # Calculate metrics
            total_posts = len(deliverables)
            completed_deliverables = len([d for d in deliverables if d['status'] == 'approved'])
            on_time_deliverables = len([
                d for d in deliverables 
                if d['status'] == 'approved' and self._is_deliverable_on_time(d)
            ])
            
            total_gmv = Decimal(str(earnings.get('total_gmv', 0))) if earnings else Decimal('0.00')
            
            avg_views_per_post = Decimal('0.00')
            if total_posts > 0:
                total_views = sum(d.get('views_count', 0) for d in deliverables)
                avg_views_per_post = Decimal(str(total_views / total_posts))
            
            avg_engagement_rate = Decimal('0.00')
            if deliverables:
                engagement_rates = []
                for d in deliverables:
                    views = d.get('views_count', 0)
                    if views > 0:
                        engagement = d.get('likes_count', 0) + d.get('comments_count', 0) + d.get('shares_count', 0)
                        engagement_rates.append(engagement / views * 100)
                
                if engagement_rates:
                    avg_engagement_rate = Decimal(str(sum(engagement_rates) / len(engagement_rates)))
            
            # Calculate consistency score
            consistency_score = Decimal('0.00')
            if total_posts > 0:
                consistency_score = Decimal(str(on_time_deliverables / total_posts))
            
            # Calculate reliability rating (0.0 to 5.0)
            reliability_rating = consistency_score * 5
            
            # Update performance record
            performance_update = CreatorPerformanceUpdate(
                total_posts=total_posts,
                completed_deliverables=completed_deliverables,
                on_time_deliverables=on_time_deliverables,
                total_gmv=total_gmv,
                avg_views_per_post=avg_views_per_post,
                avg_engagement_rate=avg_engagement_rate,
                consistency_score=consistency_score,
                reliability_rating=reliability_rating
            )
            
            creator_performance_crud.update_creator_performance(
                db, creator_id, campaign_id, performance_update
            )
            
            logger.info(f"Successfully updated performance for creator {creator_id}")
            
        except Exception as e:
            logger.error(f"Error updating creator performance: {e}")
        finally:
            db.close()
    
    def _is_date_in_range(self, date_str: Optional[str], start: datetime, end: datetime) -> bool:
        """Check if a date string falls within a range"""
        if not date_str:
            return False
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return start <= date_obj <= end
        except (ValueError, TypeError):
            return False
    
    def _is_deliverable_on_time(self, deliverable: Dict[str, Any]) -> bool:
        """Check if a deliverable was submitted on time"""
        due_date_str = deliverable.get('due_date')
        submitted_at_str = deliverable.get('submitted_at')
        
        if not due_date_str or not submitted_at_str:
            return False
        
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            submitted_at = datetime.fromisoformat(submitted_at_str.replace('Z', '+00:00'))
            return submitted_at <= due_date
        except (ValueError, TypeError):
            return False
    
    async def _get_active_campaigns(self) -> List[Dict[str, Any]]:
        """Get list of active campaigns from campaign service"""
        # This would make an API call to the campaign service
        # For now, return an empty list as placeholder
        try:
            # This would be implemented based on your campaign service API
            return []
        except Exception as e:
            logger.error(f"Error fetching active campaigns: {e}")
            return []
    
    async def close_clients(self):
        """Close all HTTP clients"""
        await self.campaign_client.close()
        await self.user_client.close()
        await self.payment_client.close()
        await self.integration_client.close()



