# app/services/analytics_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal
import logging

from app.crud.analytics import analytics_crud, campaign_performance_crud, creator_performance_crud
from app.schemas.analytics import (
    CampaignPerformanceDailyCreate,
    CampaignPerformanceDailyUpdate,
    CampaignPerformanceDailyResponse,
    CreatorPerformanceCreate,
    CreatorPerformanceUpdate,
    CreatorPerformanceResponse,
    CampaignAnalyticsSummary,
    CreatorLeaderboard,
    PerformanceMetrics,
    AnalyticsFilter,
    CampaignProgressResponse,
    EngagementAnalytics,
    GMVAnalytics
)
from app.external.campaign_service_client import CampaignServiceClient
from app.external.user_service_client import UserServiceClient

logger = logging.getLogger(__name__)


class AnalyticsService:
    
    def __init__(self, db: Session):
        self.db = db
        self.campaign_client = CampaignServiceClient()
        self.user_client = UserServiceClient()
    
    # Campaign Performance Methods
    def get_campaign_daily_performance(
        self,
        campaign_id: UUID,
        date_snapshot: date
    ) -> Optional[CampaignPerformanceDailyResponse]:
        performance = campaign_performance_crud.get_daily_performance(
            self.db, campaign_id, date_snapshot
        )
        if performance:
            return CampaignPerformanceDailyResponse.model_validate(performance)
        return None
    
    def get_campaign_performance_range(
        self,
        campaign_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[CampaignPerformanceDailyResponse]:
        performances = campaign_performance_crud.get_performance_by_date_range(
            self.db, campaign_id, start_date, end_date
        )
        return [CampaignPerformanceDailyResponse.model_validate(p) for p in performances]
    
    def create_or_update_daily_performance(
        self,
        performance_data: CampaignPerformanceDailyCreate
    ) -> CampaignPerformanceDailyResponse:
        # Check if performance already exists
        existing = campaign_performance_crud.get_daily_performance(
            self.db, performance_data.campaign_id, performance_data.date_snapshot
        )
        
        if existing:
            # Update existing record
            update_data = CampaignPerformanceDailyUpdate(**performance_data.model_dump())
            updated = campaign_performance_crud.update_daily_performance(
                self.db, performance_data.campaign_id, performance_data.date_snapshot, update_data
            )
            return CampaignPerformanceDailyResponse.model_validate(updated)
        else:
            # Create new record
            created = campaign_performance_crud.create_daily_performance(self.db, performance_data)
            return CampaignPerformanceDailyResponse.model_validate(created)
    
    def get_campaign_summary(
        self,
        campaign_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> CampaignAnalyticsSummary:
        # Get campaign details from campaign service
        campaign_details = self.campaign_client.get_campaign(campaign_id)
        
        # Get performance summary
        summary = campaign_performance_crud.get_campaign_summary(
            self.db, campaign_id, start_date, end_date
        )
        
        return CampaignAnalyticsSummary(
            campaign_id=campaign_id,
            campaign_name=campaign_details.get('name') if campaign_details else None,
            total_gmv=summary['total_gmv'],
            total_creators=summary['max_creators'],
            total_posts=summary['total_posts'],
            avg_engagement_rate=summary['avg_engagement_rate'],
            conversion_rate=summary['avg_conversion_rate'],
            date_range={
                'start_date': start_date or date.today() - timedelta(days=30),
                'end_date': end_date or date.today()
            }
        )
    
    def get_campaign_progress(
        self,
        campaign_id: UUID
    ) -> CampaignProgressResponse:
        # Get campaign details from campaign service
        campaign = self.campaign_client.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Get current performance
        summary = campaign_performance_crud.get_campaign_summary(self.db, campaign_id)
        
        # Calculate progress
        target_gmv = campaign.get('target_gmv', 0) or 0
        target_posts = campaign.get('target_posts', 0) or 0
        current_gmv = summary['total_gmv']
        current_posts = summary['total_posts']
        
        # Calculate progress percentage (weighted average if both targets exist)
        progress_percentage = 0.0
        if target_gmv > 0 and target_posts > 0:
            gmv_progress = min(float(current_gmv / target_gmv), 1.0) * 100
            posts_progress = min(current_posts / target_posts, 1.0) * 100
            progress_percentage = (gmv_progress + posts_progress) / 2
        elif target_gmv > 0:
            progress_percentage = min(float(current_gmv / target_gmv), 1.0) * 100
        elif target_posts > 0:
            progress_percentage = min(current_posts / target_posts, 1.0) * 100
        
        # Determine status
        if progress_percentage >= 100:
            status = "completed"
        elif progress_percentage >= 80:
            status = "ahead"
        elif progress_percentage >= 60:
            status = "on_track"
        else:
            status = "behind"
        
        # Calculate days remaining
        end_date = campaign.get('end_date')
        days_remaining = None
        if end_date:
            end_date_obj = datetime.fromisoformat(end_date).date()
            days_remaining = (end_date_obj - date.today()).days
        
        return CampaignProgressResponse(
            campaign_id=campaign_id,
            target_gmv=Decimal(str(target_gmv)) if target_gmv else None,
            current_gmv=current_gmv,
            target_posts=target_posts if target_posts else None,
            current_posts=current_posts,
            progress_percentage=progress_percentage,
            status=status,
            days_remaining=days_remaining
        )
    
    # Creator Performance Methods
    def get_creator_performance(
        self,
        creator_id: UUID,
        campaign_id: Optional[UUID] = None
    ) -> Optional[CreatorPerformanceResponse]:
        performance = creator_performance_crud.get_creator_performance(
            self.db, creator_id, campaign_id
        )
        if performance:
            return CreatorPerformanceResponse.model_validate(performance)
        return None
    
    def update_creator_performance(
        self,
        creator_id: UUID,
        campaign_id: Optional[UUID],
        performance_data: CreatorPerformanceUpdate
    ) -> CreatorPerformanceResponse:
        # Check if performance record exists
        existing = creator_performance_crud.get_creator_performance(
            self.db, creator_id, campaign_id
        )
        
        if existing:
            updated = creator_performance_crud.update_creator_performance(
                self.db, creator_id, campaign_id, performance_data
            )
            return CreatorPerformanceResponse.model_validate(updated)
        else:
            # Create new record
            create_data = CreatorPerformanceCreate(
                creator_id=creator_id,
                campaign_id=campaign_id,
                **performance_data.model_dump(exclude_unset=True)
            )
            created = creator_performance_crud.create_creator_performance(self.db, create_data)
            return CreatorPerformanceResponse.model_validate(created)
    
    def get_creator_leaderboard(
        self,
        campaign_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[CreatorLeaderboard]:
        leaderboard_data = creator_performance_crud.get_creator_leaderboard(
            self.db, campaign_id, limit
        )
        
        leaderboard = []
        for creator_data in leaderboard_data:
            # Get creator details from user service
            creator_details = self.user_client.get_user(creator_data['creator_id'])
            creator_name = None
            if creator_details:
                creator_name = f"{creator_details.get('first_name', '')} {creator_details.get('last_name', '')}".strip()
                if not creator_name:
                    creator_name = creator_details.get('username')
            
            leaderboard.append(CreatorLeaderboard(
                creator_id=creator_data['creator_id'],
                creator_name=creator_name,
                total_gmv=creator_data['total_gmv'],
                total_posts=creator_data['total_posts'],
                avg_engagement_rate=creator_data['avg_engagement_rate'],
                rank=creator_data['rank']
            ))
        
        return leaderboard
    
    # Analytics Dashboard Methods
    def get_overview_metrics(
        self,
        filters: Optional[AnalyticsFilter] = None
    ) -> PerformanceMetrics:
        # Get basic metrics
        overview = analytics_crud.get_overview_metrics(self.db, filters)
        
        # Get top performing campaigns
        top_campaigns_data = campaign_performance_crud.get_top_performing_campaigns(
            self.db, 
            limit=5, 
            start_date=filters.date_range.start_date if filters and filters.date_range else None,
            end_date=filters.date_range.end_date if filters and filters.date_range else None
        )
        
        top_campaigns = []
        for campaign_data in top_campaigns_data:
            campaign_details = self.campaign_client.get_campaign(campaign_data['campaign_id'])
            top_campaigns.append(CampaignAnalyticsSummary(
                campaign_id=campaign_data['campaign_id'],
                campaign_name=campaign_details.get('name') if campaign_details else None,
                total_gmv=campaign_data['total_gmv'],
                total_creators=0,  # This would need to be calculated separately
                total_posts=campaign_data['total_posts'],
                avg_engagement_rate=campaign_data['avg_engagement_rate'],
                conversion_rate=Decimal('0.00'),  # This would need to be calculated
                date_range={}
            ))
        
        # Get top performing creators
        top_creators = self.get_creator_leaderboard(limit=5)
        
        return PerformanceMetrics(
            total_campaigns=overview['total_campaigns'],
            total_creators=overview['total_creators'],
            total_gmv=overview['total_gmv'],
            total_posts=overview['total_posts'],
            avg_engagement_rate=overview['avg_engagement_rate'],
            top_performing_campaigns=top_campaigns,
            top_performing_creators=top_creators
        )
    
    def get_engagement_analytics(
        self,
        campaign_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> EngagementAnalytics:
        if campaign_id:
            summary = campaign_performance_crud.get_campaign_summary(
                self.db, campaign_id, start_date, end_date
            )
        else:
            # Get overall metrics with filters
            filters = AnalyticsFilter()
            if start_date and end_date:
                from app.schemas.analytics import DateRangeFilter
                filters.date_range = DateRangeFilter(start_date=start_date, end_date=end_date)
            summary = analytics_crud.get_overview_metrics(self.db, filters)
        
        total_views = summary.get('total_views', 0)
        total_likes = summary.get('total_likes', 0)
        total_comments = summary.get('total_comments', 0)
        total_shares = summary.get('total_shares', 0)
        
        # Calculate engagement rate
        engagement_rate = Decimal('0.00')
        if total_views > 0:
            total_engagement = total_likes + total_comments + total_shares
            engagement_rate = Decimal(str(total_engagement / total_views * 100))
        
        # Calculate view to like ratio
        view_to_like_ratio = Decimal('0.00')
        if total_likes > 0:
            view_to_like_ratio = Decimal(str(total_views / total_likes))
        
        return EngagementAnalytics(
            total_views=total_views,
            total_likes=total_likes,
            total_comments=total_comments,
            total_shares=total_shares,
            engagement_rate=engagement_rate,
            view_to_like_ratio=view_to_like_ratio
        )
    
    def get_gmv_analytics(
        self,
        campaign_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> GMVAnalytics:
        if campaign_id:
            summary = campaign_performance_crud.get_campaign_summary(
                self.db, campaign_id, start_date, end_date
            )
            
            # Get daily data for growth calculation
            if not start_date:
                start_date = date.today() - timedelta(days=30)
            if not end_date:
                end_date = date.today()
                
            daily_data = campaign_performance_crud.get_performance_by_date_range(
                self.db, campaign_id, start_date, end_date
            )
        else:
            # Get overall metrics
            filters = AnalyticsFilter()
            if start_date and end_date:
                from app.schemas.analytics import DateRangeFilter
                filters.date_range = DateRangeFilter(start_date=start_date, end_date=end_date)
            summary = analytics_crud.get_overview_metrics(self.db, filters)
            daily_data = []  # Would need to implement overall daily data retrieval
        
        total_gmv = summary.get('total_gmv', Decimal('0.00'))
        total_posts = summary.get('total_posts', 0)
        max_creators = summary.get('max_creators', 0)
        
        # Calculate averages
        avg_gmv_per_creator = Decimal('0.00')
        if max_creators > 0:
            avg_gmv_per_creator = total_gmv / max_creators
        
        avg_gmv_per_post = Decimal('0.00')
        if total_posts > 0:
            avg_gmv_per_post = total_gmv / total_posts
        
        # Calculate growth rate
        gmv_growth_rate = Decimal('0.00')
        if len(daily_data) > 1:
            first_period_gmv = sum(d.total_gmv for d in daily_data[:len(daily_data)//2])
            second_period_gmv = sum(d.total_gmv for d in daily_data[len(daily_data)//2:])
            if first_period_gmv > 0:
                gmv_growth_rate = ((second_period_gmv - first_period_gmv) / first_period_gmv) * 100
        
        # Get top GMV days
        top_gmv_days = []
        if daily_data:
            sorted_days = sorted(daily_data, key=lambda x: x.total_gmv, reverse=True)[:5]
            top_gmv_days = [
                {
                    'date': day.date_snapshot.isoformat(),
                    'gmv': float(day.total_gmv),
                    'posts': day.posts_submitted
                }
                for day in sorted_days
            ]
        
        return GMVAnalytics(
            total_gmv=total_gmv,
            gmv_growth_rate=gmv_growth_rate,
            avg_gmv_per_creator=avg_gmv_per_creator,
            avg_gmv_per_post=avg_gmv_per_post,
            top_gmv_days=top_gmv_days
        )
    
    def calculate_creator_consistency_score(
        self,
        creator_id: UUID,
        campaign_id: Optional[UUID] = None
    ) -> Decimal:
        """Calculate creator consistency score based on deliverable completion"""
        # This would typically call the campaign service to get deliverable data
        # For now, return a placeholder calculation
        
        try:
            deliverable_data = self.campaign_client.get_creator_deliverables(creator_id, campaign_id)
            if not deliverable_data:
                return Decimal('0.00')
            
            total_deliverables = len(deliverable_data)
            on_time_deliverables = len([d for d in deliverable_data if d.get('on_time', False)])
            
            if total_deliverables == 0:
                return Decimal('0.00')
            
            consistency_score = Decimal(str(on_time_deliverables / total_deliverables))
            return min(consistency_score, Decimal('1.00'))
            
        except Exception as e:
            logger.error(f"Error calculating consistency score for creator {creator_id}: {e}")
            return Decimal('0.00')