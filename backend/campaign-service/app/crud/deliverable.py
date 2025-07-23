# app/crud/deliverable.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.campaign import Deliverable, CampaignApplication
from app.schemas.deliverable import DeliverableCreate, DeliverableUpdate
from uuid import UUID
from typing import List, Optional
import datetime

async def create_deliverable(db: AsyncSession, deliverable: DeliverableCreate):
    # Get the application to extract campaign_id and creator_id
    application = await get_application(db, deliverable.application_id)
    if not application:
        raise ValueError("Application not found")
    
    # Prepare the data
    deliverable_data = deliverable.model_dump()
    
    # Ensure hashtags_used is properly formatted as array of strings
    if 'hashtags_used' in deliverable_data:
        if deliverable_data['hashtags_used'] is None:
            deliverable_data['hashtags_used'] = []
        elif isinstance(deliverable_data['hashtags_used'], str):
            import json
            try:
                if deliverable_data['hashtags_used'] == '[]':
                    deliverable_data['hashtags_used'] = []
                else:
                    parsed = json.loads(deliverable_data['hashtags_used'])
                    if isinstance(parsed, list):
                        deliverable_data['hashtags_used'] = [str(item) for item in parsed]
                    else:
                        deliverable_data['hashtags_used'] = []
            except (json.JSONDecodeError, TypeError):
                deliverable_data['hashtags_used'] = []
        elif isinstance(deliverable_data['hashtags_used'], list):
            # Ensure all items are strings
            deliverable_data['hashtags_used'] = [str(item) for item in deliverable_data['hashtags_used']]
    
    db_deliverable = Deliverable(
        **deliverable_data,
        campaign_id=application.campaign_id,
        creator_id=application.creator_id,
        status="submitted",
        submitted_at=datetime.datetime.now()
    )
    db.add(db_deliverable)
    await db.commit()
    await db.refresh(db_deliverable)
    return db_deliverable

async def get_deliverable(db: AsyncSession, deliverable_id: UUID):
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id))
    return result.scalar_one_or_none()

async def get_application(db: AsyncSession, application_id: UUID):
    result = await db.execute(select(CampaignApplication).where(CampaignApplication.id == application_id))
    return result.scalar_one_or_none()

async def get_deliverables_by_creator(db: AsyncSession, creator_id: UUID, campaign_id: Optional[UUID] = None):
    query = select(Deliverable).join(CampaignApplication).where(
        CampaignApplication.creator_id == creator_id
    )
    if campaign_id:
        query = query.where(CampaignApplication.campaign_id == campaign_id)
    result = await db.execute(query)
    return result.scalars().all()

async def get_deliverables_by_campaign_and_creator(db: AsyncSession, campaign_id: UUID, creator_id: UUID):
    """Get deliverables for a specific campaign that belong to a specific creator"""
    result = await db.execute(
        select(Deliverable).join(CampaignApplication).where(
            and_(
                CampaignApplication.campaign_id == campaign_id,
                CampaignApplication.creator_id == creator_id
            )
        )
    )
    return result.scalars().all()

async def get_deliverables_by_campaign(db: AsyncSession, campaign_id: UUID, status_filter: Optional[str] = None):
    query = select(Deliverable).where(Deliverable.campaign_id == campaign_id)
    if status_filter:
        query = query.where(Deliverable.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()

async def update_deliverable(db: AsyncSession, deliverable_id: UUID, deliverable_update: DeliverableUpdate, reviewer_id: UUID):
    db_deliverable = await get_deliverable(db, deliverable_id)
    if db_deliverable:
        update_data = deliverable_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_deliverable, key, value)
        
        if deliverable_update.status == "approved":
            db_deliverable.approved_at = datetime.datetime.now()
            db_deliverable.approved_by = reviewer_id
        
        db.add(db_deliverable)
        await db.commit()
        await db.refresh(db_deliverable)
    return db_deliverable