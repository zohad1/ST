# app/api/endpoints/earnings.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.creator_earnings import (
    CreatorEarningsResponse, 
    CreatorEarningsCreate, 
    CreatorEarningsUpdate,
    CreatorEarningsSummary
)
from app.services.earnings_service import EarningsCalculationService
from app.crud import creator_earnings as crud_earnings

router = APIRouter()

@router.get("/", response_model=List[CreatorEarningsResponse])
async def get_earnings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    campaign_id: Optional[UUID] = None,
    creator_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get earnings records with filtering"""
    
    # Authorization: creators can only see their own earnings
    if current_user["role"] == "creator":
        creator_id = UUID(current_user["sub"])
    
    earnings = crud_earnings.get_multi_filtered(
        db, skip=skip, limit=limit, 
        campaign_id=campaign_id, creator_id=creator_id
    )
    
    return [CreatorEarningsResponse.model_validate(earning) for earning in earnings]

@router.get("/creator/{creator_id}", response_model=List[CreatorEarningsResponse])
async def get_creator_earnings(
    creator_id: UUID,
    campaign_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get earnings for a specific creator"""
    
    # Authorization check
    if current_user["role"] == "creator" and UUID(current_user["sub"]) != creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other creators' earnings"
        )
    
    if campaign_id:
        earning = crud_earnings.get_by_creator_and_campaign(db, creator_id, campaign_id)
        return [CreatorEarningsResponse.model_validate(earning)] if earning else []
    else:
        earnings = crud_earnings.get_by_creator_id(db, creator_id)
        return [CreatorEarningsResponse.model_validate(earning) for earning in earnings]

@router.get("/creator/{creator_id}/summary", response_model=CreatorEarningsSummary)
async def get_creator_earnings_summary(
    creator_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get earnings summary for a creator"""
    
    # Authorization check
    if current_user["role"] == "creator" and UUID(current_user["sub"]) != creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other creators' earnings"
        )
    
    earnings = crud_earnings.get_by_creator_id(db, creator_id)
    
    if not earnings:
        return CreatorEarningsSummary(
            creator_id=creator_id,
            total_campaigns=0,
            total_earnings=0.0,
            total_paid=0.0,
            pending_payment=0.0,
            last_updated=None
        )
    
    total_earnings = sum(e.calculated_total_earnings for e in earnings)
    total_paid = sum(float(e.total_paid) for e in earnings)
    pending_payment = sum(e.calculated_pending_payment for e in earnings)
    last_updated = max(e.last_updated for e in earnings)
    
    return CreatorEarningsSummary(
        creator_id=creator_id,
        total_campaigns=len(earnings),
        total_earnings=total_earnings,
        total_paid=total_paid,
        pending_payment=pending_payment,
        last_updated=last_updated
    )

@router.get("/campaign/{campaign_id}/totals")
async def get_campaign_earnings_totals(
    campaign_id: UUID,
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """Get total earnings for a campaign"""
    
    earnings_service = EarningsCalculationService(db)
    totals = await earnings_service.calculate_campaign_total_payouts(campaign_id)
    
    return totals

@router.post("/calculate", response_model=CreatorEarningsResponse)
async def calculate_earnings(
    creator_id: UUID,
    campaign_id: UUID,
    application_id: UUID,
    deliverables_completed: int = 0,
    gmv_generated: float = 0.0,
    force_recalculate: bool = False,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Calculate or recalculate earnings for a creator"""
    
    earnings_service = EarningsCalculationService(db)
    
    try:
        earnings = await earnings_service.calculate_creator_earnings(
            creator_id=creator_id,
            campaign_id=campaign_id,
            application_id=application_id,
            deliverables_completed=deliverables_completed,
            gmv_generated=gmv_generated,
            force_recalculate=force_recalculate
        )
        
        return CreatorEarningsResponse.model_validate(earnings)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating earnings: {str(e)}"
        )

@router.post("/process-deliverable")
async def process_deliverable_completion(
    creator_id: UUID,
    campaign_id: UUID,
    application_id: UUID,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Process earnings when a deliverable is completed"""
    
    earnings_service = EarningsCalculationService(db)
    
    try:
        await earnings_service.process_deliverable_completion(
            creator_id, campaign_id, application_id
        )
        
        return {"message": "Deliverable completion processed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing deliverable: {str(e)}"
        )

@router.post("/process-gmv")
async def process_gmv_update(
    creator_id: UUID,
    campaign_id: UUID,
    new_gmv_amount: float,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Process earnings when GMV is updated"""
    
    earnings_service = EarningsCalculationService(db)
    
    try:
        await earnings_service.process_gmv_update(
            creator_id, campaign_id, new_gmv_amount
        )
        
        return {"message": "GMV update processed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing GMV update: {str(e)}"
        )

