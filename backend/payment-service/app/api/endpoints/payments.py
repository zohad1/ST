
# app/api/endpoints/payments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.payment import (
    PaymentCreate, 
    PaymentUpdate, 
    PaymentResponse, 
    PaymentListResponse,
    BulkPaymentCreate
)
from app.services.payment_service import PaymentProcessingService
from app.crud import payment as crud_payment

router = APIRouter()

@router.get("/", response_model=PaymentListResponse)
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    creator_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payments with filtering"""
    
    # Authorization: creators can only see their own payments
    if current_user["role"] == "creator":
        creator_id = UUID(current_user["sub"])  # Use "sub" instead of "id"
    
    payments, total = crud_payment.get_multi_filtered(
        db, skip=skip, limit=limit,
        creator_id=creator_id, campaign_id=campaign_id, status=status
    )
    
    return PaymentListResponse(
        payments=[PaymentResponse.model_validate(payment) for payment in payments],
        total=total,
        page=skip // limit + 1,
        limit=limit
    )

@router.get("/overview")
async def get_payment_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment overview for the current user"""
    
    # For now, return a simple overview
    # In a real implementation, you'd calculate totals, recent payments, etc.
    return {
        "total_earnings": 0.0,
        "pending_payments": 0.0,
        "completed_payments": 0.0,
        "recent_payments": []
    }

@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    creator_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history with filtering"""
    
    # Authorization: creators can only see their own payments
    if current_user["role"] == "creator":
        creator_id = UUID(current_user["sub"])  # Use "sub" instead of "id"
    
    payments = crud_payment.get_multi_filtered(
        db, skip=skip, limit=limit,
        creator_id=creator_id, campaign_id=campaign_id, status=status
    )
    
    return [PaymentResponse.model_validate(payment) for payment in payments]

@router.get("/creator/{creator_id}/history", response_model=List[PaymentResponse])
async def get_creator_payment_history(
    creator_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history for a creator"""
    
    # Authorization check
    if (current_user["role"] == "creator" and 
        UUID(current_user["sub"]) != creator_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other creators' payment history"
        )
    
    payments = crud_payment.get_by_creator_id(db, creator_id, skip=skip, limit=limit)
    return [PaymentResponse.model_validate(payment) for payment in payments]

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment details"""
    
    payment = crud_payment.get(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Authorization check
    if (current_user["role"] == "creator" and 
        UUID(current_user["sub"]) != payment.creator_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other creators' payments"
        )
    
    return PaymentResponse.model_validate(payment)

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Create a new payment"""
    
    payment_service = PaymentProcessingService(db)
    
    try:
        created_payment = await payment_service.create_manual_payment(payment)
        
        # Process payment in background
        background_tasks.add_task(
            payment_service.process_payment_async, created_payment.id
        )
        
        return PaymentResponse.model_validate(created_payment)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating payment: {str(e)}"
        )

@router.post("/bulk", response_model=List[PaymentResponse])
async def create_bulk_payments(
    bulk_payment: BulkPaymentCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Create multiple payments at once"""
    
    payment_service = PaymentProcessingService(db)
    
    try:
        payments = await payment_service.create_bulk_payments(bulk_payment)
        
        # Process payments in background
        for payment in payments:
            background_tasks.add_task(
                payment_service.process_payment_async, payment.id
            )
        
        return [PaymentResponse.model_validate(payment) for payment in payments]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating bulk payments: {str(e)}"
        )

@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    payment_update: PaymentUpdate,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Update payment details"""
    
    payment = crud_payment.get(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    updated_payment = crud_payment.update(db, payment_id, payment_update)
    return PaymentResponse.model_validate(updated_payment)

@router.post("/{payment_id}/retry")
async def retry_payment(
    payment_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Retry a failed payment"""
    
    payment = crud_payment.get(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed payments can be retried"
        )
    
    payment_service = PaymentProcessingService(db)
    
    try:
        # Reset payment status to pending
        crud_payment.update(db, payment_id, PaymentUpdate(status="pending"))
        
        # Retry processing in background
        background_tasks.add_task(
            payment_service.process_payment_async, payment_id
        )
        
        return {"message": "Payment retry initiated"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrying payment: {str(e)}"
        )

@router.post("/{payment_id}/cancel")
async def cancel_payment(
    payment_id: UUID,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Cancel a pending payment"""
    
    payment_service = PaymentProcessingService(db)
    
    try:
        result = await payment_service.cancel_payment(payment_id)
        return {"message": "Payment cancelled successfully", "details": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error cancelling payment: {str(e)}"
        )

