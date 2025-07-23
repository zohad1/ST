# app/crud/campaign.py - Complete version
from sqlalchemy.orm import Session
from app.models.campaign import Campaign, CampaignSegment, GMVBonusTier, LeaderboardBonus
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignSegmentCreate,
    GMVBonusTierCreate, LeaderboardBonusCreate
)
from uuid import UUID
from typing import List, Optional


def get_campaign(db: Session, campaign_id: UUID):
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()


def get_campaigns(db: Session, skip: int = 0, limit: int = 100, agency_id: Optional[UUID] = None,
                  brand_id: Optional[UUID] = None, status_filter: Optional[str] = None):
    query = db.query(Campaign)
    if agency_id:
        query = query.filter(Campaign.agency_id == agency_id)
    if brand_id:
        query = query.filter(Campaign.brand_id == brand_id)
    if status_filter:
        query = query.filter(Campaign.status == status_filter)
    return query.offset(skip).limit(limit).all()


def create_campaign(db: Session, campaign: CampaignCreate, agency_id: UUID):
    db_campaign = Campaign(**campaign.model_dump(), agency_id=agency_id)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def update_campaign(db: Session, campaign_id: UUID, campaign_update: CampaignUpdate):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if db_campaign:
        update_data = campaign_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_campaign, key, value)
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
    return db_campaign


def delete_campaign(db: Session, campaign_id: UUID):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if db_campaign:
        db.delete(db_campaign)
        db.commit()
    return db_campaign


# CRUD for Campaign Segments
def create_campaign_segment(db: Session, segment: CampaignSegmentCreate, campaign_id: UUID):
    db_segment = CampaignSegment(**segment.model_dump(), campaign_id=campaign_id)
    db.add(db_segment)
    db.commit()
    db.refresh(db_segment)
    return db_segment


def get_campaign_segments(db: Session, campaign_id: UUID):
    return db.query(CampaignSegment).filter(CampaignSegment.campaign_id == campaign_id).all()


# CRUD for GMV Bonus Tiers
def create_gmv_bonus_tier(db: Session, bonus_tier: GMVBonusTierCreate, campaign_id: UUID):
    db_bonus_tier = GMVBonusTier(**bonus_tier.model_dump(), campaign_id=campaign_id)
    db.add(db_bonus_tier)
    db.commit()
    db.refresh(db_bonus_tier)
    return db_bonus_tier


def get_gmv_bonus_tiers(db: Session, campaign_id: UUID):
    return db.query(GMVBonusTier).filter(GMVBonusTier.campaign_id == campaign_id).all()


def delete_gmv_bonus_tier(db: Session, bonus_tier_id: UUID):
    db_bonus_tier = db.query(GMVBonusTier).filter(GMVBonusTier.id == bonus_tier_id).first()
    if db_bonus_tier:
        db.delete(db_bonus_tier)
        db.commit()
    return db_bonus_tier


# CRUD for Leaderboard Bonuses
def create_leaderboard_bonus(db: Session, leaderboard_bonus: LeaderboardBonusCreate, campaign_id: UUID):
    db_leaderboard_bonus = LeaderboardBonus(**leaderboard_bonus.model_dump(), campaign_id=campaign_id)
    db.add(db_leaderboard_bonus)
    db.commit()
    db.refresh(db_leaderboard_bonus)
    return db_leaderboard_bonus


def get_leaderboard_bonuses(db: Session, campaign_id: UUID):
    return db.query(LeaderboardBonus).filter(LeaderboardBonus.campaign_id == campaign_id).all()


def delete_leaderboard_bonus(db: Session, leaderboard_bonus_id: UUID):
    db_leaderboard_bonus = db.query(LeaderboardBonus).filter(LeaderboardBonus.id == leaderboard_bonus_id).first()
    if db_leaderboard_bonus:
        db.delete(db_leaderboard_bonus)
        db.commit()
    return db_leaderboard_bonus