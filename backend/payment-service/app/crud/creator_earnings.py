
# Update app/crud/creator_earnings.py to work with string IDs
# app/crud/creator_earnings.py
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.standalone_models import CreatorEarnings
from app.schemas.creator_earnings import CreatorEarningsCreate, CreatorEarningsUpdate

def get(db: Session, earning_id: UUID) -> Optional[CreatorEarnings]:
    """Get earnings by ID"""
    return db.query(CreatorEarnings).filter(CreatorEarnings.id == earning_id).first()

def get_by_application_id(db: Session, application_id: UUID) -> Optional[CreatorEarnings]:
    """Get earnings by application ID"""
    return db.query(CreatorEarnings).filter(
        CreatorEarnings.application_id == str(application_id)
    ).first()

def get_by_creator_id(db: Session, creator_id: UUID) -> List[CreatorEarnings]:
    """Get all earnings for a creator"""
    return db.query(CreatorEarnings).filter(
        CreatorEarnings.creator_id == str(creator_id)
    ).all()

def get_by_campaign_id(db: Session, campaign_id: UUID) -> List[CreatorEarnings]:
    """Get all earnings for a campaign"""
    return db.query(CreatorEarnings).filter(
        CreatorEarnings.campaign_id == str(campaign_id)
    ).all()

def get_by_creator_and_campaign(
    db: Session, creator_id: UUID, campaign_id: UUID
) -> Optional[CreatorEarnings]:
    """Get earnings for a specific creator in a specific campaign"""
    return db.query(CreatorEarnings).filter(
        CreatorEarnings.creator_id == str(creator_id),
        CreatorEarnings.campaign_id == str(campaign_id)
    ).first()

def get_multi_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    creator_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None
) -> List[CreatorEarnings]:
    """Get earnings with filtering"""
    query = db.query(CreatorEarnings)
    
    if creator_id:
        query = query.filter(CreatorEarnings.creator_id == str(creator_id))
    if campaign_id:
        query = query.filter(CreatorEarnings.campaign_id == str(campaign_id))
    
    return query.offset(skip).limit(limit).all()

def create(db: Session, earnings: CreatorEarningsCreate) -> CreatorEarnings:
    """Create new earnings record"""
    earnings_dict = earnings.model_dump()
    # Convert UUID fields to strings
    earnings_dict['creator_id'] = str(earnings_dict['creator_id'])
    earnings_dict['campaign_id'] = str(earnings_dict['campaign_id'])
    earnings_dict['application_id'] = str(earnings_dict['application_id'])
    
    db_earnings = CreatorEarnings(**earnings_dict)
    db.add(db_earnings)
    db.commit()
    db.refresh(db_earnings)
    return db_earnings

def update(
    db: Session, earning_id: UUID, earnings_update: CreatorEarningsUpdate
) -> Optional[CreatorEarnings]:
    """Update earnings record"""
    db_earnings = get(db, earning_id)
    if not db_earnings:
        return None
    
    update_data = earnings_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_earnings, key, value)
    
    db.add(db_earnings)
    db.commit()
    db.refresh(db_earnings)
    return db_earnings

def remove(db: Session, earning_id: UUID) -> bool:
    """Delete earnings record"""
    db_earnings = get(db, earning_id)
    if not db_earnings:
        return False
    
    db.delete(db_earnings)
    db.commit()
    return True
