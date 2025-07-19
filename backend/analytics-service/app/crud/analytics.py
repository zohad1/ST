# app/crud/analytics.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal

from app.models.analytics import CampaignPerformanceDaily, CreatorPerformance
from app.schemas.analytics import (
    CampaignPerformanceDailyCreate, 
    CampaignPerformanceDailyUpdate,
    CreatorPerformanceCreate,
    CreatorPerformanceUpdate,
    AnalyticsFilter
)


class CampaignPerformanceCRUD:
    
    def get_daily_performance(
        self, 
        db: Session, 
        campaign_id: UUID, 
        date_snapshot: date
    ) -> Optional[CampaignPerformanceDaily]:
        return db.query(CampaignPerformanceDaily).filter(
            CampaignPerformanceDaily.campaign_id == campaign_id,
            CampaignPerformanceDaily.date_snapshot == date_snapshot
        ).first()
    
    def get_performance_by_date_range(
        self,
        db: Session,
        campaign_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[CampaignPerformanceDaily]:
        return db.query(CampaignPerformanceDaily).filter(
            CampaignPerformanceDaily.campaign_id == campaign_id,
            CampaignPerformanceDaily.date_snapshot >= start_date,
            CampaignPerformanceDaily.date_snapshot <= end_date
        ).order_by(CampaignPerformanceDaily.date_snapshot).all()
    
    def create_daily_performance(
        self,
        db: Session,
        performance_data: CampaignPerformanceDailyCreate
    ) -> CampaignPerformanceDaily:
        db_performance = CampaignPerformanceDaily(**performance_data.model_dump())
        db.add(db_performance)
        db.commit()
        db.refresh(db_performance)
        return db_performance
    
    def update_daily_performance(
        self,
        db: Session,
        campaign_id: UUID,
        date_snapshot: date,
        update_data: CampaignPerformanceDailyUpdate
    ) -> Optional[CampaignPerformanceDaily]:
        db_performance = self.get_daily_performance(db, campaign_id, date_snapshot)
        if db_performance:
            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(db_performance, key, value)
            db.commit()
            db.refresh(db_performance)
        return db_performance
    
    def get_campaign_summary(
        self,
        db: Session,
        campaign_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        query = db.query(
            func.sum(CampaignPerformanceDaily.total_gmv).label('total_gmv'),
            func.sum(CampaignPerformanceDaily.posts_submitted).label('total_posts'),
            func.sum(CampaignPerformanceDaily.total_views).label('total_views'),
            func.sum(CampaignPerformanceDaily.total_likes).label('total_likes'),
            func.sum(CampaignPerformanceDaily.total_comments).label('total_comments'),
            func.sum(CampaignPerformanceDaily.total_shares).label('total_shares'),
            func.avg(CampaignPerformanceDaily.avg_engagement_rate).label('avg_engagement_rate'),
            func.avg(CampaignPerformanceDaily.conversion_rate).label('avg_conversion_rate'),
            func.max(CampaignPerformanceDaily.total_creators).label('max_creators')
        ).filter(CampaignPerformanceDaily.campaign_id == campaign_id)
        
        if start_date:
            query = query.filter(CampaignPerformanceDaily.date_snapshot >= start_date)
        if end_date:
            query = query.filter(CampaignPerformanceDaily.date_snapshot <= end_date)
            
        result = query.first()
        
        return {
            'total_gmv': result.total_gmv or Decimal('0.00'),
            'total_posts': result.total_posts or 0,
            'total_views': result.total_views or 0,
            'total_likes': result.total_likes or 0,
            'total_comments': result.total_comments or 0,
            'total_shares': result.total_shares or 0,
            'avg_engagement_rate': result.avg_engagement_rate or Decimal('0.00'),
            'avg_conversion_rate': result.avg_conversion_rate or Decimal('0.00'),
            'max_creators': result.max_creators or 0
        }
    
    def get_top_performing_campaigns(
        self,
        db: Session,
        limit: int = 10,
        metric: str = 'total_gmv',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        metric_column = getattr(CampaignPerformanceDaily, metric, CampaignPerformanceDaily.total_gmv)
        
        query = db.query(
            CampaignPerformanceDaily.campaign_id,
            func.sum(metric_column).label('total_metric'),
            func.sum(CampaignPerformanceDaily.total_gmv).label('total_gmv'),
            func.sum(CampaignPerformanceDaily.posts_submitted).label('total_posts'),
            func.avg(CampaignPerformanceDaily.avg_engagement_rate).label('avg_engagement_rate')
        ).group_by(CampaignPerformanceDaily.campaign_id)
        
        if start_date:
            query = query.filter(CampaignPerformanceDaily.date_snapshot >= start_date)
        if end_date:
            query = query.filter(CampaignPerformanceDaily.date_snapshot <= end_date)
            
        results = query.order_by(desc('total_metric')).limit(limit).all()
        
        return [
            {
                'campaign_id': result.campaign_id,
                'total_gmv': result.total_gmv or Decimal('0.00'),
                'total_posts': result.total_posts or 0,
                'avg_engagement_rate': result.avg_engagement_rate or Decimal('0.00'),
                'metric_value': result.total_metric or 0
            }
            for result in results
        ]


class CreatorPerformanceCRUD:
    
    def get_creator_performance(
        self,
        db: Session,
        creator_id: UUID,
        campaign_id: Optional[UUID] = None
    ) -> Optional[CreatorPerformance]:
        query = db.query(CreatorPerformance).filter(
            CreatorPerformance.creator_id == creator_id
        )
        if campaign_id:
            query = query.filter(CreatorPerformance.campaign_id == campaign_id)
        else:
            query = query.filter(CreatorPerformance.campaign_id.is_(None))
        
        return query.first()
    
    def get_creator_campaign_performances(
        self,
        db: Session,
        creator_id: UUID
    ) -> List[CreatorPerformance]:
        return db.query(CreatorPerformance).filter(
            CreatorPerformance.creator_id == creator_id,
            CreatorPerformance.campaign_id.is_not(None)
        ).all()
    
    def create_creator_performance(
        self,
        db: Session,
        performance_data: CreatorPerformanceCreate
    ) -> CreatorPerformance:
        db_performance = CreatorPerformance(**performance_data.model_dump())
        db.add(db_performance)
        db.commit()
        db.refresh(db_performance)
        return db_performance
    
    def update_creator_performance(
        self,
        db: Session,
        creator_id: UUID,
        campaign_id: Optional[UUID],
        update_data: CreatorPerformanceUpdate
    ) -> Optional[CreatorPerformance]:
        db_performance = self.get_creator_performance(db, creator_id, campaign_id)
        if db_performance:
            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(db_performance, key, value)
            db_performance.last_calculated = datetime.utcnow()
            db.commit()
            db.refresh(db_performance)
        return db_performance
    
    def get_top_creators_by_gmv(
        self,
        db: Session,
        limit: int = 10,
        campaign_id: Optional[UUID] = None
    ) -> List[CreatorPerformance]:
        query = db.query(CreatorPerformance)
        
        if campaign_id:
            query = query.filter(CreatorPerformance.campaign_id == campaign_id)
        else:
            query = query.filter(CreatorPerformance.campaign_id.is_(None))
            
        return query.order_by(desc(CreatorPerformance.total_gmv)).limit(limit).all()
    
    def get_creator_leaderboard(
        self,
        db: Session,
        campaign_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        query = db.query(
            CreatorPerformance.creator_id,
            CreatorPerformance.total_gmv,
            CreatorPerformance.total_posts,
            CreatorPerformance.avg_engagement_rate,
            CreatorPerformance.consistency_score,
            CreatorPerformance.reliability_rating
        )
        
        if campaign_id:
            query = query.filter(CreatorPerformance.campaign_id == campaign_id)
        else:
            query = query.filter(CreatorPerformance.campaign_id.is_(None))
            
        results = query.order_by(desc(CreatorPerformance.total_gmv)).limit(limit).all()
        
        return [
            {
                'creator_id': result.creator_id,
                'total_gmv': result.total_gmv,
                'total_posts': result.total_posts,
                'avg_engagement_rate': result.avg_engagement_rate,
                'consistency_score': result.consistency_score,
                'reliability_rating': result.reliability_rating,
                'rank': idx + 1
            }
            for idx, result in enumerate(results)
        ]


class AnalyticsCRUD:
    
    def __init__(self):
        self.campaign_performance = CampaignPerformanceCRUD()
        self.creator_performance = CreatorPerformanceCRUD()
    
    def get_overview_metrics(
        self,
        db: Session,
        filters: Optional[AnalyticsFilter] = None
    ) -> Dict[str, Any]:
        # Base queries
        campaign_query = db.query(CampaignPerformanceDaily)
        creator_query = db.query(CreatorPerformance)
        
        # Apply filters
        if filters:
            if filters.campaign_ids:
                campaign_query = campaign_query.filter(
                    CampaignPerformanceDaily.campaign_id.in_(filters.campaign_ids)
                )
                creator_query = creator_query.filter(
                    CreatorPerformance.campaign_id.in_(filters.campaign_ids)
                )
            
            if filters.creator_ids:
                creator_query = creator_query.filter(
                    CreatorPerformance.creator_id.in_(filters.creator_ids)
                )
            
            if filters.date_range:
                campaign_query = campaign_query.filter(
                    CampaignPerformanceDaily.date_snapshot >= filters.date_range.start_date,
                    CampaignPerformanceDaily.date_snapshot <= filters.date_range.end_date
                )
        
        # Calculate metrics
        campaign_metrics = campaign_query.with_entities(
            func.count(func.distinct(CampaignPerformanceDaily.campaign_id)).label('total_campaigns'),
            func.sum(CampaignPerformanceDaily.total_gmv).label('total_gmv'),
            func.sum(CampaignPerformanceDaily.posts_submitted).label('total_posts'),
            func.sum(CampaignPerformanceDaily.total_views).label('total_views'),
            func.avg(CampaignPerformanceDaily.avg_engagement_rate).label('avg_engagement_rate')
        ).first()
        
        creator_metrics = creator_query.with_entities(
            func.count(func.distinct(CreatorPerformance.creator_id)).label('total_creators')
        ).first()
        
        return {
            'total_campaigns': campaign_metrics.total_campaigns or 0,
            'total_creators': creator_metrics.total_creators or 0,
            'total_gmv': campaign_metrics.total_gmv or Decimal('0.00'),
            'total_posts': campaign_metrics.total_posts or 0,
            'total_views': campaign_metrics.total_views or 0,
            'avg_engagement_rate': campaign_metrics.avg_engagement_rate or Decimal('0.00')
        }


# Create instances
campaign_performance_crud = CampaignPerformanceCRUD()
creator_performance_crud = CreatorPerformanceCRUD()
analytics_crud = AnalyticsCRUD()