
# app/crud/referral.py
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.referral import Referral
from app.schemas.referral import ReferralCreate, ReferralUpdate

def get(db: Session, referral_id: UUID) -> Optional[Referral]:
    """Get referral by ID"""
    return db.query(Referral).filter(Referral.id == referral_id).first()

def get_by_referrer_id(db: Session, referrer_id: UUID) -> List[Referral]:
    """Get all referrals by a specific referrer"""
    return db.query(Referral).filter(Referral.referrer_id == referrer_id).all()

def get_by_referred_id(db: Session, referred_id: UUID) -> List[Referral]:
    """Get all referrals for a specific referred user"""
    return db.query(Referral).filter(Referral.referred_id == referred_id).all()

def get_by_referral_code(db: Session, referral_code: str) -> Optional[Referral]:
    """Get referral by referral code"""
    return db.query(Referral).filter(Referral.referral_code == referral_code).first()

def get_by_referrer_and_campaign(
    db: Session, referrer_id: UUID, campaign_id: UUID
) -> List[Referral]:
    """Get referrals by referrer for a specific campaign"""
    return db.query(Referral).filter(
        Referral.referrer_id == referrer_id,
        Referral.campaign_id == campaign_id
    ).all()

def get_multi_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    referrer_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None
) -> List[Referral]:
    """Get referrals with filtering"""
    query = db.query(Referral)
    
    if referrer_id:
        query = query.filter(Referral.referrer_id == referrer_id)
    if campaign_id:
        query = query.filter(Referral.campaign_id == campaign_id)
    
    return query.offset(skip).limit(limit).all()

def get_pending_bonuses(db: Session) -> List[Referral]:
    """Get referrals with pending bonuses"""
    return db.query(Referral).filter(
        Referral.bonus_earned > Referral.bonus_paid
    ).all()

def create(db: Session, referral: ReferralCreate) -> Referral:
    """Create new referral"""
    db_referral = Referral(**referral.model_dump())
    db.add(db_referral)
    db.commit()
    db.refresh(db_referral)
    return db_referral

def update(
    db: Session, referral_id: UUID, referral_update: ReferralUpdate
) -> Optional[Referral]:
    """Update referral"""
    db_referral = get(db, referral_id)
    if not db_referral:
        return None
    
    update_data = referral_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_referral, key, value)
    
    db.add(db_referral)
    db.commit()
    db.refresh(db_referral)
    return db_referral

def remove(db: Session, referral_id: UUID) -> bool:
    """Delete referral"""
    db_referral = get(db, referral_id)
    if not db_referral:
        return False
    
    db.delete(db_referral)
    db.commit()
    return True