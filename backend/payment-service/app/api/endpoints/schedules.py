
# app/api/endpoints/schedules.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.payment_schedule import (
    PaymentScheduleCreate, 
    PaymentScheduleUpdate, 
    PaymentScheduleResponse
)
from app.services.schedule_service import PaymentScheduleService
from app.crud import payment_schedule as crud_schedule

router = APIRouter()

@router.get("/", response_model=List[PaymentScheduleResponse])
async def get_payment_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    campaign_id: Optional[UUID] = None,
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """Get payment schedules"""
    
    schedules = crud_schedule.get_multi_filtered(
        db, skip=skip, limit=limit, campaign_id=campaign_id
    )
    
    return [PaymentScheduleResponse.model_validate(schedule) for schedule in schedules]

@router.post("/", response_model=PaymentScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_schedule(
    schedule: PaymentScheduleCreate,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Create a new payment schedule"""
    
    schedule_service = PaymentScheduleService(db)
    
    try:
        created_schedule = await schedule_service.create_schedule(schedule)
        return PaymentScheduleResponse.model_validate(created_schedule)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating payment schedule: {str(e)}"
        )

@router.get("/{schedule_id}", response_model=PaymentScheduleResponse)
async def get_payment_schedule(
    schedule_id: UUID,
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """Get payment schedule details"""
    
    schedule = crud_schedule.get(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment schedule not found"
        )
    
    return PaymentScheduleResponse.model_validate(schedule)

@router.patch("/{schedule_id}", response_model=PaymentScheduleResponse)
async def update_payment_schedule(
    schedule_id: UUID,
    schedule_update: PaymentScheduleUpdate,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Update payment schedule"""
    
    schedule = crud_schedule.get(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment schedule not found"
        )
    
    updated_schedule = crud_schedule.update(db, schedule_id, schedule_update)
    return PaymentScheduleResponse.model_validate(updated_schedule)

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_schedule(
    schedule_id: UUID,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Delete payment schedule"""
    
    schedule = crud_schedule.get(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment schedule not found"
        )
    
    crud_schedule.remove(db, schedule_id)
    return {"message": "Payment schedule deleted successfully"}

@router.post("/{schedule_id}/execute")
async def execute_payment_schedule(
    schedule_id: UUID,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Manually execute a payment schedule"""
    
    schedule_service = PaymentScheduleService(db)
    
    try:
        result = await schedule_service.execute_schedule(schedule_id)
        return {"message": "Payment schedule executed", "payments_created": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error executing payment schedule: {str(e)}"
        )

@router.get("/campaign/{campaign_id}/eligible")
async def get_eligible_creators_for_payout(
    campaign_id: UUID,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Get creators eligible for payout in a campaign"""
    
    schedule_service = PaymentScheduleService(db)
    
    try:
        eligible_creators = await schedule_service.get_eligible_creators(campaign_id)
        return {"eligible_creators": eligible_creators}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting eligible creators: {str(e)}"
        )

