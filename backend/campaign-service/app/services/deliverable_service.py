
# app/services/deliverable_service.py
from sqlalchemy.orm import Session
from app.crud import deliverable as crud_deliverable
from app.schemas.deliverable import (
    DeliverableCreate,
    DeliverableUpdate,
    DeliverableResponse
)
from uuid import UUID
from fastapi import HTTPException, status
from typing import List, Optional

class DeliverableService:
    def __init__(self, db: Session):
        self.db = db

    def submit_deliverable(self, deliverable_data: DeliverableCreate, creator_id: UUID):
        # Verify the application belongs to the creator
        application = crud_deliverable.get_application(self.db, deliverable_data.application_id)
        if not application or application.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to submit deliverable for this application"
            )
        
        db_deliverable = crud_deliverable.create_deliverable(self.db, deliverable_data)
        return DeliverableResponse.model_validate(db_deliverable)

    def get_creator_deliverables(self, creator_id: UUID, campaign_id: Optional[UUID] = None):
        deliverables = crud_deliverable.get_deliverables_by_creator(
            self.db, creator_id, campaign_id
        )
        return [DeliverableResponse.model_validate(d) for d in deliverables]

    def get_campaign_deliverables_for_creator(self, campaign_id: UUID, creator_id: UUID):
        """Get deliverables for a specific campaign that belong to the creator"""
        deliverables = crud_deliverable.get_deliverables_by_campaign_and_creator(
            self.db, campaign_id, creator_id
        )
        return [DeliverableResponse.model_validate(d) for d in deliverables]

    def review_deliverable(self, deliverable_id: UUID, review_data: DeliverableUpdate, reviewer_id: UUID):
        deliverable = crud_deliverable.get_deliverable(self.db, deliverable_id)
        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found"
            )
        
        updated_deliverable = crud_deliverable.update_deliverable(
            self.db, deliverable_id, review_data, reviewer_id
        )
        return DeliverableResponse.model_validate(updated_deliverable)

    def get_campaign_deliverables(self, campaign_id: UUID, status_filter: Optional[str] = None):
        deliverables = crud_deliverable.get_deliverables_by_campaign(
            self.db, campaign_id, status_filter
        )
        return [DeliverableResponse.model_validate(d) for d in deliverables]