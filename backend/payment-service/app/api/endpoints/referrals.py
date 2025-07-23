
# app/api/endpoints/referrals.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.referral import (
    ReferralCreate, 
    ReferralUpdate, 
    ReferralResponse,
    ReferralStats
)
from app.services.referral_service import ReferralService
from app.crud import referral as crud_referral

router = APIRouter()

@router.get("/", response_model=List[ReferralResponse])
async def get_referrals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    referrer_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get referrals with filtering"""
    
    # Authorization: creators can only see their own referrals
    if current_user["role"] == "creator":
        referrer_id = UUID(current_user["id"])
    
    referrals = crud_referral.get_multi_filtered(
        db, skip=skip, limit=limit,
        referrer_id=referrer_id, campaign_id=campaign_id
    )
    
    return [ReferralResponse.model_validate(referral) for referral in referrals]

@router.post("/", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referral: ReferralCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new referral"""
    
    # For creators, they can only create referrals where they are the referrer
    if current_user["role"] == "creator":
        referral.referrer_id = UUID(current_user["id"])
    
    referral_service = ReferralService(db)
    
    try:
        created_referral = await referral_service.create_referral(referral)
        return ReferralResponse.model_validate(created_referral)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating referral: {str(e)}"
        )

@router.get("/creator/{creator_id}/stats", response_model=ReferralStats)
async def get_creator_referral_stats(
    creator_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get referral statistics for a creator"""
    
    # Authorization check
    if (current_user["role"] == "creator" and 
        UUID(current_user["id"]) != creator_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other creators' referral stats"
        )
    
    referral_service = ReferralService(db)
    stats = await referral_service.get_referral_stats(creator_id)
    
    return stats

@router.post("/generate-code")
async def generate_referral_code(
    campaign_id: Optional[UUID] = None,
    current_user: dict = Depends(require_role(["creator"])),
    db: Session = Depends(get_db)
):
    """Generate a referral code for a creator"""
    
    creator_id = UUID(current_user["id"])
    referral_service = ReferralService(db)
    
    try:
        code = await referral_service.generate_referral_code(creator_id, campaign_id)
        return {"referral_code": code}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating referral code: {str(e)}"
        )

@router.post("/process-signup")
async def process_referral_signup(
    referral_code: str,
    referred_user_id: UUID,
    current_user: dict = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Process a referral when someone signs up with a referral code"""
    
    referral_service = ReferralService(db)
    
    try:
        result = await referral_service.process_referral_signup(
            referral_code, referred_user_id
        )
        return {"message": "Referral processed successfully", "details": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing referral: {str(e)}"
        )

@router.post("/{referral_id}/calculate-bonus")
async def calculate_referral_bonus(
    referral_id: UUID,
    current_user: dict = Depends(require_role(["agency", "admin"])),
    db: Session = Depends(get_db)
):
    """Calculate and assign referral bonus"""
    
    referral_service = ReferralService(db)
    
    try:
        bonus_amount = await referral_service.calculate_and_assign_bonus(referral_id)
        return {"message": "Referral bonus calculated", "bonus_amount": bonus_amount}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating referral bonus: {str(e)}"
        )

