
# app/schemas/deliverable.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.campaign import DeliverableStatus

class DeliverableBase(BaseModel):
    application_id: UUID
    deliverable_number: int
    tiktok_post_url: Optional[str] = None
    post_caption: Optional[str] = None
    hashtags_used: Optional[List[str]] = None

class DeliverableCreate(DeliverableBase):
    pass

class DeliverableUpdate(BaseModel):
    status: Optional[DeliverableStatus] = None
    agency_feedback: Optional[str] = None
    revision_requested: Optional[bool] = None
    revision_notes: Optional[str] = None

class DeliverableResponse(DeliverableBase):
    id: UUID
    due_date: Optional[datetime] = None
    status: DeliverableStatus
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    agency_feedback: Optional[str] = None
    revision_requested: bool
    revision_notes: Optional[str] = None
    views_count: Optional[int] = 0
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    shares_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
