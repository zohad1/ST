# app/models/payment.py
import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, DECIMAL, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.payment_enums import PaymentStatus, PaymentType, PayoutMethod

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {'schema': 'payments'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=True)
    earning_id = Column(UUID(as_uuid=True), ForeignKey("payments.creator_earnings.id"), nullable=True)
    
    # Payment details
    amount = Column(DECIMAL(10,2), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_method = Column(Enum(PayoutMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    
    # External payment IDs
    stripe_payment_intent_id = Column(String(255))
    fanbasis_transaction_id = Column(String(255))
    external_transaction_id = Column(String(255))
    
    # Payment metadata
    description = Column(Text)
    failure_reason = Column(Text)
    
    # Timestamps
    initiated_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    processed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))

    # Relationships
    earning = relationship("app.models.creator_earnings.CreatorEarnings", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"

    @property
    def is_completed(self):
        return self.status == PaymentStatus.completed

    @property
    def is_failed(self):
        return self.status == PaymentStatus.failed

    def mark_as_completed(self):
        """Mark payment as completed and set timestamp"""
        self.status = PaymentStatus.completed
        self.completed_at = datetime.datetime.now()

    def mark_as_failed(self, reason: str = None):
        """Mark payment as failed and set timestamp"""
        self.status = PaymentStatus.failed
        self.failed_at = datetime.datetime.now()
        if reason:
            self.failure_reason = reason


