# app/schemas/creator_earnings.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class CreatorEarningsBase(BaseModel):
    creator_id: UUID
    campaign_id: UUID
    application_id: UUID
    base_earnings: float = Field(default=0.00, ge=0, description="Base earnings amount")
    gmv_commission: float = Field(default=0.00, ge=0, description="GMV commission amount")
    bonus_earnings: float = Field(default=0.00, ge=0, description="Bonus earnings amount")
    referral_earnings: float = Field(default=0.00, ge=0, description="Referral earnings amount")

    @validator('base_earnings', 'gmv_commission', 'bonus_earnings', 'referral_earnings')
    def validate_earnings_amounts(cls, v):
        return round(v, 2)

class CreatorEarningsCreate(CreatorEarningsBase):
    pass

class CreatorEarningsUpdate(BaseModel):
    base_earnings: Optional[float] = Field(None, ge=0)
    gmv_commission: Optional[float] = Field(None, ge=0)
    bonus_earnings: Optional[float] = Field(None, ge=0)
    referral_earnings: Optional[float] = Field(None, ge=0)

    @validator('base_earnings', 'gmv_commission', 'bonus_earnings', 'referral_earnings', pre=True)
    def validate_optional_amounts(cls, v):
        if v is not None:
            return round(v, 2)
        return v

class CreatorEarningsResponse(CreatorEarningsBase):
    id: UUID
    total_earnings: float = Field(description="Total calculated earnings")
    total_paid: float = Field(description="Total amount paid out")
    pending_payment: float = Field(description="Pending payment amount")
    first_earned_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True

class CreatorEarningsSummary(BaseModel):
    creator_id: UUID
    total_campaigns: int
    total_earnings: float
    total_paid: float
    pending_payment: float
    last_updated: datetime

