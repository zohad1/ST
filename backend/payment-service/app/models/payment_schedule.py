# app/models/payment_schedule.py
import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"
    __table_args__ = {'schema': 'payments'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=False)
    
    # Schedule configuration
    schedule_name = Column(String(100), nullable=False)
    is_automated = Column(Boolean, default=True)
    
    # Trigger conditions
    trigger_on_deliverable_completion = Column(Boolean, default=False)
    trigger_on_gmv_milestone = Column(Boolean, default=False)
    gmv_milestone_amount = Column(DECIMAL(12,2))
    trigger_on_campaign_completion = Column(Boolean, default=False)
    
    # Payment timing
    payment_delay_days = Column(Integer, default=0)
    minimum_payout_amount = Column(DECIMAL(10,2), default=0.00)
    
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)

    def __repr__(self):
        return f"<PaymentSchedule(id={self.id}, name={self.schedule_name}, campaign_id={self.campaign_id})>"

    @property
    def should_trigger_on_deliverable(self):
        return self.is_automated and self.trigger_on_deliverable_completion

    @property
    def should_trigger_on_gmv(self):
        return self.is_automated and self.trigger_on_gmv_milestone

    @property
    def should_trigger_on_completion(self):
        return self.is_automated and self.trigger_on_campaign_completion


