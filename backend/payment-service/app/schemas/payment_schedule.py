
# app/schemas/payment_schedule.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class PaymentScheduleBase(BaseModel):
    campaign_id: UUID
    schedule_name: str = Field(..., min_length=1, max_length=100)
    is_automated: bool = True
    trigger_on_deliverable_completion: bool = False
    trigger_on_gmv_milestone: bool = False
    gmv_milestone_amount: Optional[float] = Field(None, gt=0)
    trigger_on_campaign_completion: bool = False
    payment_delay_days: int = Field(default=0, ge=0, le=365)
    minimum_payout_amount: float = Field(default=0.00, ge=0)

    @validator('gmv_milestone_amount', 'minimum_payout_amount')
    def validate_amounts(cls, v):
        if v is not None:
            return round(v, 2)
        return v

    @validator('gmv_milestone_amount')
    def validate_gmv_milestone(cls, v, values):
        if values.get('trigger_on_gmv_milestone') and v is None:
            raise ValueError('GMV milestone amount is required when trigger_on_gmv_milestone is True')
        return v

class PaymentScheduleCreate(PaymentScheduleBase):
    pass

class PaymentScheduleUpdate(BaseModel):
    schedule_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_automated: Optional[bool] = None
    trigger_on_deliverable_completion: Optional[bool] = None
    trigger_on_gmv_milestone: Optional[bool] = None
    gmv_milestone_amount: Optional[float] = Field(None, gt=0)
    trigger_on_campaign_completion: Optional[bool] = None
    payment_delay_days: Optional[int] = Field(None, ge=0, le=365)
    minimum_payout_amount: Optional[float] = Field(None, ge=0)

class PaymentScheduleResponse(PaymentScheduleBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

