# app/models/referral.py
import uuid
import datetime
from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint('referrer_id', 'referred_id', 'campaign_id', name='unique_referral_per_campaign'),
        {'schema': 'payments'}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    referred_id = Column(UUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaigns.id"), nullable=True)
    
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