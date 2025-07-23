
# app/schemas/payment.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.payment_enums import PaymentStatus, PaymentType, PayoutMethod

class PaymentBase(BaseModel):
    creator_id: UUID
    amount: float = Field(..., gt=0, description="Payment amount must be greater than 0")
    payment_type: PaymentType
    payment_method: PayoutMethod
    description: Optional[str] = Field(None, max_length=500)

    @validator('amount')
    def validate_amount(cls, v):
        return round(v, 2)

class PaymentCreate(PaymentBase):
    campaign_id: Optional[UUID] = None
    earning_id: Optional[UUID] = None

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    external_transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class PaymentResponse(PaymentBase):
    id: UUID
    campaign_id: Optional[UUID] = None
    earning_id: Optional[UUID] = None
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str] = None
    fanbasis_transaction_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
    initiated_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentListResponse(BaseModel):
    payments: list[PaymentResponse]
    total: int
    page: int
    limit: int

class BulkPaymentCreate(BaseModel):
    creator_ids: list[UUID] = Field(..., min_items=1, max_items=100)
    amount_per_creator: float = Field(..., gt=0)
    payment_type: PaymentType
    payment_method: PayoutMethod
    description: Optional[str] = None

    @validator('amount_per_creator')
    def validate_amount(cls, v):
        return round(v, 2)

