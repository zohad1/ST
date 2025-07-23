
# app/schemas/referral.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class ReferralBase(BaseModel):
    referrer_id: UUID
    referred_id: UUID
    campaign_id: Optional[UUID] = None
    referral_code: Optional[str] = Field(None, max_length=50)

    @validator('referred_id')
    def validate_different_users(cls, v, values):
        if 'referrer_id' in values and v == values['referrer_id']:
            raise ValueError('Referrer and referred user cannot be the same')
        return v

class ReferralCreate(ReferralBase):
    pass

class ReferralUpdate(BaseModel):
    bonus_earned: Optional[float] = Field(None, ge=0)
    bonus_paid: Optional[float] = Field(None, ge=0)
    first_campaign_joined_at: Optional[datetime] = None

    @validator('bonus_earned', 'bonus_paid')
    def validate_amounts(cls, v):
        if v is not None:
            return round(v, 2)
        return v

class ReferralResponse(ReferralBase):
    id: UUID
    referred_at: datetime
    first_campaign_joined_at: Optional[datetime] = None
    bonus_earned: float
    bonus_paid: float
    pending_bonus: float

    class Config:
        from_attributes = True

class ReferralStats(BaseModel):
    referrer_id: UUID
    total_referrals: int
    successful_referrals: int
    total_bonus_earned: float
    total_bonus_paid: float
    pending_bonus: float

