# app/crud/campaign.py - Async version
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, String
from app.models.campaign import Campaign, CampaignSegment, GMVBonusTier, LeaderboardBonus
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignSegmentCreate,
    GMVBonusTierCreate, LeaderboardBonusCreate
)
from uuid import UUID
from typing import List, Optional


async def get_campaign(db: AsyncSession, campaign_id: UUID):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    return result.scalar_one_or_none()


async def get_campaigns(db: AsyncSession, skip: int = 0, limit: int = 100, agency_id: Optional[UUID] = None,
                  brand_id: Optional[UUID] = None, status_filter: Optional[str] = None):
    query = select(Campaign)
    if agency_id:
        query = query.where(Campaign.agency_id == agency_id)
    if brand_id:
        query = query.where(Campaign.brand_id == brand_id)
    if status_filter:
        query = query.where(cast(Campaign.status, String) == status_filter)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_campaign(db: AsyncSession, campaign: CampaignCreate, agency_id: UUID):
    db_campaign = Campaign(**campaign.model_dump(), agency_id=agency_id)
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign


async def update_campaign(db: AsyncSession, campaign_id: UUID, campaign_update: CampaignUpdate):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    db_campaign = result.scalar_one_or_none()
    if db_campaign:
        update_data = campaign_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_campaign, key, value)
        db.add(db_campaign)
        await db.commit()
        await db.refresh(db_campaign)
    return db_campaign


async def delete_campaign(db: AsyncSession, campaign_id: UUID):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    db_campaign = result.scalar_one_or_none()
    if db_campaign:
        await db.delete(db_campaign)
        await db.commit()
    return db_campaign


# CRUD for Campaign Segments
async def create_campaign_segment(db: AsyncSession, segment: CampaignSegmentCreate, campaign_id: UUID):
    db_segment = CampaignSegment(**segment.model_dump(), campaign_id=campaign_id)
    db.add(db_segment)
    await db.commit()
    await db.refresh(db_segment)
    return db_segment


async def get_campaign_segments(db: AsyncSession, campaign_id: UUID):
    result = await db.execute(select(CampaignSegment).where(CampaignSegment.campaign_id == campaign_id))
    return result.scalars().all()


# CRUD for GMV Bonus Tiers
async def create_gmv_bonus_tier(db: AsyncSession, bonus_tier: GMVBonusTierCreate, campaign_id: UUID):
    db_bonus_tier = GMVBonusTier(**bonus_tier.model_dump(), campaign_id=campaign_id)
    db.add(db_bonus_tier)
    await db.commit()
    await db.refresh(db_bonus_tier)
    return db_bonus_tier


async def get_gmv_bonus_tiers(db: AsyncSession, campaign_id: UUID):
    result = await db.execute(select(GMVBonusTier).where(GMVBonusTier.campaign_id == campaign_id))
    return result.scalars().all()


async def delete_gmv_bonus_tier(db: AsyncSession, bonus_tier_id: UUID):
    result = await db.execute(select(GMVBonusTier).where(GMVBonusTier.id == bonus_tier_id))
    db_bonus_tier = result.scalar_one_or_none()
    if db_bonus_tier:
        await db.delete(db_bonus_tier)
        await db.commit()
    return db_bonus_tier


# CRUD for Leaderboard Bonuses
async def create_leaderboard_bonus(db: AsyncSession, leaderboard_bonus: LeaderboardBonusCreate, campaign_id: UUID):
    db_leaderboard_bonus = LeaderboardBonus(**leaderboard_bonus.model_dump(), campaign_id=campaign_id)
    db.add(db_leaderboard_bonus)
    await db.commit()
    await db.refresh(db_leaderboard_bonus)
    return db_leaderboard_bonus


async def get_leaderboard_bonuses(db: AsyncSession, campaign_id: UUID):
    result = await db.execute(select(LeaderboardBonus).where(LeaderboardBonus.campaign_id == campaign_id))
    return result.scalars().all()


async def delete_leaderboard_bonus(db: AsyncSession, leaderboard_bonus_id: UUID):
    result = await db.execute(select(LeaderboardBonus).where(LeaderboardBonus.id == leaderboard_bonus_id))
    db_leaderboard_bonus = result.scalar_one_or_none()
    if db_leaderboard_bonus:
        await db.delete(db_leaderboard_bonus)
        await db.commit()
    return db_leaderboard_bonus