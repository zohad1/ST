# app/api/endpoints/deliverables.py
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.deliverable import (
    DeliverableCreate,
    DeliverableResponse,
    DeliverableUpdate
)
from app.services.deliverable_service import DeliverableService

router = APIRouter()

@router.post("/", response_model=DeliverableResponse, status_code=status.HTTP_201_CREATED)
async def submit_deliverable(
    deliverable: DeliverableCreate,
    current_user: dict = Depends(require_role(["creator"])),
    db: Session = Depends(get_db)
):
    """Creator submits a deliverable"""
    service = DeliverableService(db)
    return service.submit_deliverable(deliverable, creator_id=UUID(current_user["id"]))

@router.get("/my-deliverables", response_model=List[DeliverableResponse])
async def get_my_deliverables(
    campaign_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(require_role(["creator"])),
    db: Session = Depends(get_db)
):
    """Get creator's deliverables"""
    service = DeliverableService(db)
    return service.get_creator_deliverables(
        creator_id=UUID(current_user["id"]), 
        campaign_id=campaign_id
    )

@router.get("/campaign/{campaign_id}/creator", response_model=List[DeliverableResponse])
async def get_campaign_deliverables_for_creator(
    campaign_id: UUID,
    current_user: dict = Depends(require_role(["creator"])),
    db: Session = Depends(get_db)
):
    """Get deliverables for a specific campaign (creator view)"""
    service = DeliverableService(db)
    return service.get_campaign_deliverables_for_creator(
        campaign_id=campaign_id,
        creator_id=UUID(current_user["id"])
    )

@router.put("/{deliverable_id}/review", response_model=DeliverableResponse)
async def review_deliverable(
    deliverable_id: UUID,
    review_data: DeliverableUpdate,
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """Agency/Brand reviews deliverable"""
    service = DeliverableService(db)
    return service.review_deliverable(
        deliverable_id,
        review_data,
        reviewer_id=UUID(current_user["id"])
    )

@router.get("/campaign/{campaign_id}", response_model=List[DeliverableResponse])
async def get_campaign_deliverables(
    campaign_id: UUID,
    status_filter: Optional[str] = Query(None),
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """Get all deliverables for a campaign (agency/brand view)"""
    service = DeliverableService(db)
    return service.get_campaign_deliverables(campaign_id, status_filter)