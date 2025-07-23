# app/crud/application.py - Fixed imports
from sqlalchemy.orm import Session
from app.models.campaign import CampaignApplication  # Changed from CreatorApplication
from app.schemas.application import CreatorApplicationCreate, CreatorApplicationUpdate
from uuid import UUID
from typing import List, Optional
import datetime

def create_application(db: Session, application: CreatorApplicationCreate, creator_id: UUID):
    db_application = CampaignApplication(
        **application.model_dump(),
        creator_id=creator_id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def get_application(db: Session, application_id: UUID):
    return db.query(CampaignApplication).filter(CampaignApplication.id == application_id).first()

def get_application_by_creator_campaign(db: Session, creator_id: UUID, campaign_id: UUID):
    return db.query(CampaignApplication).filter(
        CampaignApplication.creator_id == creator_id,
        CampaignApplication.campaign_id == campaign_id
    ).first()

def get_applications_by_creator(db: Session, creator_id: UUID):
    return db.query(CampaignApplication).filter(
        CampaignApplication.creator_id == creator_id
    ).all()

def get_applications_by_campaign(db: Session, campaign_id: UUID, status_filter: Optional[str] = None):
    query = db.query(CampaignApplication).filter(CampaignApplication.campaign_id == campaign_id)
    if status_filter:
        query = query.filter(CampaignApplication.status == status_filter)
    return query.all()

def get_all_applications(db: Session, skip: int = 0, limit: int = 1000):
    """Get all applications - method that was missing"""
    return db.query(CampaignApplication).offset(skip).limit(limit).all()
# app/crud/application.py - Fixed update_application method

def update_application(db: Session, application_id: UUID, application_update: CreatorApplicationUpdate, reviewer_id: UUID):
    db_application = get_application(db, application_id)
    if db_application:
        update_data = application_update.model_dump(exclude_unset=True)
        
        # Ensure status is a string value, not an enum object
        if 'status' in update_data and hasattr(update_data['status'], 'value'):
            update_data['status'] = update_data['status'].value
        
        for key, value in update_data.items():
            setattr(db_application, key, value)
        
        db_application.reviewed_at = datetime.datetime.now()
        db_application.reviewed_by = reviewer_id
        
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
    return db_application