# app/schemas/webhook.py
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID

class StripeWebhookPayload(BaseModel):
    id: str
    object: str = "event"
    type: str
    data: Dict[str, Any]
    created: int
    livemode: bool
    pending_webhooks: int
    request: Optional[Dict[str, Any]] = None

class FanbasisWebhookPayload(BaseModel):
    transaction_id: str
    status: str
    amount: float
    currency: str = "USD"
    creator_id: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class WebhookProcessingResult(BaseModel):
    success: bool
    message: str
    payment_id: Optional[UUID] = None
    error_details: Optional[Dict[str, Any]] = None