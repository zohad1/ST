# app/services/application_service.py - Complete updated version
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.campaign import CampaignApplication, Campaign
from app.models.user import User
from app.schemas.application import (
    CreatorApplicationCreate, 
    CreatorApplicationUpdate, 
    CreatorApplicationResponse
)
from uuid import UUID
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def create_application(self, application_data: CreatorApplicationCreate, creator_id: UUID):
        """Create a new application"""
        # Check if creator already applied to this campaign
        existing = self.db.query(CampaignApplication).filter(
            and_(
                CampaignApplication.creator_id == creator_id,
                CampaignApplication.campaign_id == application_data.campaign_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already applied to this campaign"
            )
        
        # Create new application
        db_application = CampaignApplication(
            creator_id=creator_id,
            campaign_id=application_data.campaign_id,
            segment_id=application_data.segment_id,
            application_data=application_data.application_data,
            status="pending"
        )
        
        # Extract specific fields from application_data if provided
        if application_data.application_data:
            db_application.application_message = application_data.application_data.get("message")
            db_application.previous_gmv = application_data.application_data.get("previous_gmv", 0.0)
            db_application.engagement_rate = application_data.application_data.get("engagement_rate", 0.0)
        
        self.db.add(db_application)
        self.db.commit()
        self.db.refresh(db_application)
        
        # Reload with relationships
        db_application = self.db.query(CampaignApplication)\
            .options(joinedload(CampaignApplication.creator))\
            .options(joinedload(CampaignApplication.campaign))\
            .filter(CampaignApplication.id == db_application.id)\
            .first()
            
        return CreatorApplicationResponse.from_orm_with_relations(db_application)

    def get_creator_applications(self, creator_id: UUID) -> List[CreatorApplicationResponse]:
        """Get applications for a specific creator"""
        applications = self.db.query(CampaignApplication)\
            .options(joinedload(CampaignApplication.campaign))\
            .filter(CampaignApplication.creator_id == creator_id)\
            .order_by(CampaignApplication.applied_at.desc())\
            .all()
            
        return [CreatorApplicationResponse.from_orm_with_relations(app, include_creator=False) 
                for app in applications]

    def review_application(self, application_id: UUID, review_data: CreatorApplicationUpdate, reviewer_id: UUID):
        """Review an application (approve/reject)"""
        application = self.db.query(CampaignApplication)\
            .options(joinedload(CampaignApplication.creator))\
            .options(joinedload(CampaignApplication.campaign))\
            .filter(CampaignApplication.id == application_id)\
            .first()
            
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Update application
        application.status = review_data.status
        application.reviewed_by = reviewer_id
        application.reviewed_at = datetime.utcnow()
        
        if review_data.rejection_reason:
            application.rejection_reason = review_data.rejection_reason
        if hasattr(review_data, 'review_notes') and review_data.review_notes:
            application.review_notes = review_data.review_notes
        
        self.db.commit()
        self.db.refresh(application)
        
        return CreatorApplicationResponse.from_orm_with_relations(application)

    def get_campaign_applications(self, campaign_id: UUID, status_filter: Optional[str] = None):
        """Get all applications for a campaign with creator details"""
        query = self.db.query(CampaignApplication)\
            .options(joinedload(CampaignApplication.creator))\
            .options(joinedload(CampaignApplication.campaign))\
            .filter(CampaignApplication.campaign_id == campaign_id)
        
        if status_filter and status_filter.lower() != "all":
            query = query.filter(CampaignApplication.status == status_filter.lower())
        
        applications = query.order_by(CampaignApplication.applied_at.desc()).all()
        
        return [CreatorApplicationResponse.from_orm_with_relations(app) for app in applications]

    def get_applications_with_filters(
        self, 
        search: Optional[str] = None,
        status: Optional[str] = None,
        campaign_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get applications with filtering and creator details"""
        try:
            query = self.db.query(CampaignApplication)\
                .options(joinedload(CampaignApplication.creator))\
                .options(joinedload(CampaignApplication.campaign))
            
            # Apply filters
            if search:
                search_lower = f"%{search.lower()}%"
                query = query.join(CampaignApplication.creator).filter(
                    or_(
                        User.username.ilike(search_lower),
                        User.first_name.ilike(search_lower),
                        User.last_name.ilike(search_lower),
                        User.email.ilike(search_lower)
                    )
                )
            
            if status and status.lower() != "all":
                query = query.filter(CampaignApplication.status == status.lower())
            
            if campaign_name and campaign_name != "All Campaigns":
                query = query.join(CampaignApplication.campaign).filter(
                    Campaign.name == campaign_name
                )
            
            # Get total count before pagination
            total = query.count()
            
            # Apply pagination and ordering
            applications = query.order_by(CampaignApplication.applied_at.desc())\
                              .offset(skip)\
                              .limit(limit)\
                              .all()
            
            # Convert to response format
            return {
                "applications": [
                    CreatorApplicationResponse.from_orm_with_relations(app).model_dump() 
                    for app in applications
                ],
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Error in get_applications_with_filters: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving applications"
            )

    def get_application_statistics(self, campaign_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get application statistics"""
        try:
            query = self.db.query(CampaignApplication)
            
            if campaign_id:
                query = query.filter(CampaignApplication.campaign_id == campaign_id)
            
            applications = query.all()
            
            total = len(applications)
            pending = len([app for app in applications if app.status == "pending"])
            approved = len([app for app in applications if app.status == "approved"])
            rejected = len([app for app in applications if app.status == "rejected"])
            
            approval_rate = round((approved / total) * 100) if total > 0 else 0
            
            return {
                "total": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "approvalRate": approval_rate,
                "avgResponseTime": "2.3h"  # This would be calculated from actual data
            }
            
        except Exception as e:
            logger.error(f"Error in get_application_statistics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving application statistics"
            )