# app/models/creator_earnings.py
import uuid
import datetime
from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey, text, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class CreatorEarnings(Base):
    __tablename__ = "creator_earnings"
    __table_args__ = {'schema': 'payments'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.creator_applications.id"), nullable=False)
    
    # Earnings breakdown
    base_earnings = Column(DECIMAL(10,2), default=0.00)
    gmv_commission = Column(DECIMAL(10,2), default=0.00)
    bonus_earnings = Column(DECIMAL(10,2), default=0.00)
    referral_earnings = Column(DECIMAL(10,2), default=0.00)
    
    # Computed columns (using server_default for PostgreSQL generated columns)
    total_earnings = Column(
        DECIMAL(10,2), 
        server_default=text("(base_earnings + gmv_commission + bonus_earnings + referral_earnings)")
    )
    total_paid = Column(DECIMAL(10,2), default=0.00)
    pending_payment = Column(
        DECIMAL(10,2),
        server_default=text("((base_earnings + gmv_commission + bonus_earnings + referral_earnings) - total_paid)")
    )
    
    # Timestamps
    first_earned_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    last_updated = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relationships
    payments = relationship(
        "app.models.payment.Payment",
        back_populates="earning",
        primaryjoin="CreatorEarnings.id==app.models.payment.Payment.earning_id",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CreatorEarnings(id={self.id}, creator_id={self.creator_id}, total_earnings={self.total_earnings})>"

    @property
    def calculated_total_earnings(self):
        """Calculate total earnings in Python if DB computed column isn't available"""
        return float(self.base_earnings + self.gmv_commission + self.bonus_earnings + self.referral_earnings)

    @property
    def calculated_pending_payment(self):
        """Calculate pending payment in Python if DB computed column isn't available"""
        return float(self.calculated_total_earnings - self.total_paid)


