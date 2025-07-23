
# app/crud/gmv_bonus.py
from sqlalchemy.orm import Session
from app.models.campaign import GMVBonusTier
from app.schemas.gmv_bonus import GMVBonusTierCreate
from uuid import UUID

def create_gmv_bonus_tier(db: Session, bonus_tier: GMVBonusTierCreate, campaign_id: UUID):
    db_bonus_tier = GMVBonusTier(**bonus_tier.model_dump(), campaign_id=campaign_id)
    db.add(db_bonus_tier)
    db.commit()
    db.refresh(db_bonus_tier)
    return db_bonus_tier

def get_gmv_bonus_tiers(db: Session, campaign_id: UUID):
    return db.query(GMVBonusTier).filter(GMVBonusTier.campaign_id == campaign_id).all()
