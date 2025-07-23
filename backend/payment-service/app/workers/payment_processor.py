
# app/workers/payment_processor.py
from celery import Celery
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.payment_service import PaymentProcessingService
from app.services.schedule_service import PaymentScheduleService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "payment_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

def get_db():
    """Get database session for Celery tasks"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_payment_task(self, payment_id: str):
    """Celery task to process payment asynchronously"""
    try:
        db = get_db()
        payment_service = PaymentProcessingService(db)
        
        # Process payment
        result = payment_service.process_payment_async(UUID(payment_id))
        
        logger.info(f"Successfully processed payment {payment_id}")
        return {"success": True, "payment_id": payment_id}
        
    except Exception as e:
        logger.error(f"Error processing payment {payment_id}: {str(e)}")
        raise self.retry(exc=e)

@celery_app.task
def process_scheduled_payouts_task():
    """Celery task to process all scheduled payouts"""
    try:
        db = get_db()
        schedule_service = PaymentScheduleService(db)
        
        # Process all scheduled payouts
        total_processed = schedule_service.process_scheduled_payouts()
        
        logger.info(f"Processed {total_processed} scheduled payouts")
        return {"success": True, "total_processed": total_processed}
        
    except Exception as e:
        logger.error(f"Error processing scheduled payouts: {str(e)}")
        return {"success": False, "error": str(e)}

@celery_app.task
def calculate_earnings_task(creator_id: str, campaign_id: str, application_id: str):
    """Celery task to calculate earnings asynchronously"""
    try:
        from app.services.earnings_service import EarningsCalculationService
        
        db = get_db()
        earnings_service = EarningsCalculationService(db)
        
        # Calculate earnings
        earnings = earnings_service.calculate_creator_earnings(
            UUID(creator_id), UUID(campaign_id), UUID(application_id)
        )
        
        logger.info(f"Calculated earnings for creator {creator_id} in campaign {campaign_id}")
        return {"success": True, "earnings_id": str(earnings.id)}
        
    except Exception as e:
        logger.error(f"Error calculating earnings: {str(e)}")
        return {"success": False, "error": str(e)}

# Periodic tasks
celery_app.conf.beat_schedule = {
    'process-scheduled-payouts': {
        'task': 'app.workers.payment_processor.process_scheduled_payouts_task',
        'schedule': 3600.0,  # Run every hour
    },
}
celery_app.conf.timezone = 'UTC'