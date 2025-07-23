# Create fixed models without external foreign keys for standalone testing

# app/models/standalone_models.py
"""
Standalone models for payment service testing
These models don't reference external tables from other services
"""
import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, DECIMAL, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.payment_enums import PaymentStatus, PaymentType, PayoutMethod

class CreatorEarnings(Base):
    __tablename__ = "creator_earnings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Store IDs as strings instead of foreign keys for standalone testing
    creator_id = Column(String(36), nullable=False)  # UUID as string
    campaign_id = Column(String(36), nullable=False)  # UUID as string
    application_id = Column(String(36), nullable=False)  # UUID as string
    
    # Earnings breakdown
    base_earnings = Column(DECIMAL(10,2), default=0.00)
    gmv_commission = Column(DECIMAL(10,2), default=0.00)
    bonus_earnings = Column(DECIMAL(10,2), default=0.00)
    referral_earnings = Column(DECIMAL(10,2), default=0.00)
    
    # Payment tracking
    total_paid = Column(DECIMAL(10,2), default=0.00)
    
    # Timestamps
    first_earned_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    last_updated = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relationships
    payments = relationship("Payment", back_populates="earning", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CreatorEarnings(id={self.id}, creator_id={self.creator_id}, total_earnings={self.calculated_total_earnings})>"

    @property
    def calculated_total_earnings(self):
        """Calculate total earnings in Python"""
        return float(self.base_earnings + self.gmv_commission + self.bonus_earnings + self.referral_earnings)

    @property
    def calculated_pending_payment(self):
        """Calculate pending payment in Python"""
        return float(self.calculated_total_earnings - self.total_paid)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Store IDs as strings instead of foreign keys
    creator_id = Column(String(36), nullable=False)  # UUID as string
    campaign_id = Column(String(36), nullable=True)  # UUID as string
    earning_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to earnings table
    
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
    earning = relationship("CreatorEarnings", back_populates="payments")

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


class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(String(36), nullable=False)  # UUID as string
    
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


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Store IDs as strings instead of foreign keys
    referrer_id = Column(String(36), nullable=False)  # UUID as string
    referred_id = Column(String(36), nullable=False)  # UUID as string
    campaign_id = Column(String(36), nullable=True)  # UUID as string
    
    # Referral details
    referral_code = Column(String(50))
    referred_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    first_campaign_joined_at = Column(DateTime(timezone=True))
    
    # Bonus tracking
    bonus_earned = Column(DECIMAL(10,2), default=0.00)
    bonus_paid = Column(DECIMAL(10,2), default=0.00)

    def __repr__(self):
        return f"<Referral(id={self.id}, referrer_id={self.referrer_id}, referred_id={self.referred_id})>"

    @property
    def pending_bonus(self):
        return float(self.bonus_earned - self.bonus_paid)

    @property
    def is_bonus_pending(self):
        return self.pending_bonus > 0

    def generate_referral_code(self, prefix: str = "REF") -> str:
        """Generate a unique referral code"""
        import secrets
        import string
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.referral_code = f"{prefix}-{random_part}"
        return self.referral_code





