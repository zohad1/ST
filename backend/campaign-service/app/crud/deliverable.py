# app/crud/deliverable.py
from sqlalchemy.orm import Session
from app.models.campaign import Deliverable, CampaignApplication
from app.schemas.deliverable import DeliverableCreate, DeliverableUpdate
from uuid import UUID
from typing import List, Optional
import datetime

def create_deliverable(db: Session, deliverable: DeliverableCreate):
    # Get the application to extract campaign_id and creator_id
    application = get_application(db, deliverable.application_id)
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
    db.commit()
    db.refresh(db_deliverable)
    return db_deliverable

def get_deliverable(db: Session, deliverable_id: UUID):
    return db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()

def get_application(db: Session, application_id: UUID):
    return db.query(CampaignApplication).filter(CampaignApplication.id == application_id).first()

def get_deliverables_by_creator(db: Session, creator_id: UUID, campaign_id: Optional[UUID] = None):
    query = db.query(Deliverable).join(CampaignApplication).filter(
        CampaignApplication.creator_id == creator_id
    )
    if campaign_id:
        query = query.filter(CampaignApplication.campaign_id == campaign_id)
    return query.all()

def get_deliverables_by_campaign_and_creator(db: Session, campaign_id: UUID, creator_id: UUID):
    """Get deliverables for a specific campaign that belong to a specific creator"""
    return db.query(Deliverable).join(CampaignApplication).filter(
        CampaignApplication.campaign_id == campaign_id,
        CampaignApplication.creator_id == creator_id
    ).all()

def get_deliverables_by_campaign(db: Session, campaign_id: UUID, status_filter: Optional[str] = None):
    query = db.query(Deliverable).filter(Deliverable.campaign_id == campaign_id)
    if status_filter:
        query = query.filter(Deliverable.status == status_filter)
    return query.all()

def update_deliverable(db: Session, deliverable_id: UUID, deliverable_update: DeliverableUpdate, reviewer_id: UUID):
    db_deliverable = get_deliverable(db, deliverable_id)
    if db_deliverable:
        update_data = deliverable_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_deliverable, key, value)
        
        if deliverable_update.status == "approved":
            db_deliverable.approved_at = datetime.datetime.now()
            db_deliverable.approved_by = reviewer_id
        
        db.add(db_deliverable)
        db.commit()
        db.refresh(db_deliverable)
    return db_deliverable