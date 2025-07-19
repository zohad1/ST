
# app/tasks/analytics_tasks.py
import asyncio
from datetime import date, timedelta
from uuid import UUID
from typing import Optional

from app.tasks.celery_app import celery_app
from app.services.aggregation_service import DataAggregationService


@celery_app.task(name="aggregate_daily_performance")
def aggregate_daily_performance_task(target_date_str: Optional[str] = None):
    """Celery task for daily performance aggregation"""
    target_date = None
    if target_date_str:
        target_date = date.fromisoformat(target_date_str)
    
    async def run_aggregation():
        service = DataAggregationService()
        try:
            await service.aggregate_daily_campaign_performance(target_date)
        finally:
            await service.close_clients()
    
    # Run the async function
    asyncio.run(run_aggregation())
    return f"Daily aggregation completed for {target_date or 'yesterday'}"


@celery_app.task(name="update_creator_performance")
def update_creator_performance_task(creator_id_str: str, campaign_id_str: Optional[str] = None):
    """Celery task for updating creator performance"""
    creator_id = UUID(creator_id_str)
    campaign_id = UUID(campaign_id_str) if campaign_id_str else None
    
    async def run_update():
        service = DataAggregationService()
        try:
            await service.update_creator_performance(creator_id, campaign_id)
        finally:
            await service.close_clients()
    
    asyncio.run(run_update())
    return f"Creator performance updated for {creator_id}"


@celery_app.task(name="cleanup_old_data")
def cleanup_old_data_task(days_to_keep: int = 365):
    """Clean up old analytics data"""
    from app.core.database import SessionLocal
    from app.models.analytics import CampaignPerformanceDaily
    from sqlalchemy import delete
    
    cutoff_date = date.today() - timedelta(days=days_to_keep)
    
    db = SessionLocal()
    try:
        # Delete old performance data
        delete_stmt = delete(CampaignPerformanceDaily).where(
            CampaignPerformanceDaily.date_snapshot < cutoff_date
        )
        result = db.execute(delete_stmt)
        db.commit()
        
        return f"Cleaned up {result.rowcount} old performance records"
        
    finally:
        db.close()


# Periodic tasks configuration
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'daily-performance-aggregation': {
        'task': 'aggregate_daily_performance',
        'schedule': crontab(hour=1, minute=0),  # Run daily at 1:00 AM
    },
    'cleanup-old-data': {
        'task': 'cleanup_old_data',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Run weekly on Sunday at 2:00 AM
    },
}