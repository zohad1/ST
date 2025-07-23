
# app/crud/payment_schedule.py
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.payment_schedule import PaymentSchedule
from app.schemas.payment_schedule import PaymentScheduleCreate, PaymentScheduleUpdate

def get(db: Session, schedule_id: UUID) -> Optional[PaymentSchedule]:
    """Get payment schedule by ID"""
    return db.query(PaymentSchedule).filter(PaymentSchedule.id == schedule_id).first()

def get_by_campaign_id(db: Session, campaign_id: UUID) -> List[PaymentSchedule]:
    """Get all schedules for a campaign"""
    return db.query(PaymentSchedule).filter(
        PaymentSchedule.campaign_id == campaign_id
    ).all()

def get_automated_schedules(db: Session) -> List[PaymentSchedule]:
    """Get all automated schedules"""
    return db.query(PaymentSchedule).filter(
        PaymentSchedule.is_automated == True
    ).all()

def get_multi_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    campaign_id: Optional[UUID] = None
) -> List[PaymentSchedule]:
    """Get schedules with filtering"""
    query = db.query(PaymentSchedule)
    
    if campaign_id:
        query = query.filter(PaymentSchedule.campaign_id == campaign_id)
    
    return query.offset(skip).limit(limit).all()

def create(db: Session, schedule: PaymentScheduleCreate) -> PaymentSchedule:
    """Create new payment schedule"""
    db_schedule = PaymentSchedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update(
    db: Session, schedule_id: UUID, schedule_update: PaymentScheduleUpdate
) -> Optional[PaymentSchedule]:
    """Update payment schedule"""
    db_schedule = get(db, schedule_id)
    if not db_schedule:
        return None
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def remove(db: Session, schedule_id: UUID) -> bool:
    """Delete payment schedule"""
    db_schedule = get(db, schedule_id)
    if not db_schedule:
        return False
    
    db.delete(db_schedule)
    db.commit()
    return True

