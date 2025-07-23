# app/models/user.py - Updated with relationships
import uuid
import datetime
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Date, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base


# Keep enums for Python type hints
class UserRole(enum.Enum):
    AGENCY = "agency"
    CREATOR = "creator"
    BRAND = "brand"
    ADMIN = "admin"


class GenderType(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NON_BINARY = "NON_BINARY"
    PREFER_NOT_TO_SAY = "PERFER_NOT_TO_SAY"


# User model with relationships
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'users'}

    # All existing fields remain exactly the same
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(50))
    profile_image_url = Column(Text)
    bio = Column(Text)
    
    # Address information for shipping
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default='US')
    
    # Social media handles
    tiktok_handle = Column(String(100))
    tiktok_user_id = Column(String(100))
    discord_handle = Column(String(100))
    discord_user_id = Column(String(100))
    instagram_handle = Column(String(100))
    
    # Creator specific fields
    content_niche = Column(String(100))
    follower_count = Column(Integer, default=0)
    average_views = Column(Integer, default=0)
    engagement_rate = Column(Numeric(5, 2), default=0.00)
    
    # Additional creator fields for frontend compatibility
    tiktok_followers = Column(Integer, default=0)
    instagram_followers = Column(Integer, default=0)
    youtube_handle = Column(String(100))
    youtube_followers = Column(Integer, default=0)
    audience_male_percentage = Column(Numeric(5, 2))
    audience_female_percentage = Column(Numeric(5, 2))
    primary_age_group = Column(String(50))
    location = Column(String(100))
    age = Column(Integer)
    ethnicity = Column(String(50))
    shipping_address = Column(Text)
    
    # Agency/Brand specific fields
    company_name = Column(String(200))
    website_url = Column(Text)
    tax_id = Column(String(50))
    
    # Profile completion tracking
    profile_completion_percentage = Column(Integer, default=0)
    
    # Preferences
    notification_preferences = Column(JSONB, default={})
    timezone = Column(String(50), default='UTC')
    
    # ADD RELATIONSHIPS - CRITICAL FOR APPLICATION SYSTEM
    campaign_applications = relationship(
        "CampaignApplication",
        foreign_keys="CampaignApplication.creator_id",
        back_populates="creator"
    )
    
    reviewed_applications = relationship(
        "CampaignApplication",
        foreign_keys="CampaignApplication.reviewed_by",
        back_populates="reviewer"
    )
    
    deliverables = relationship(
        "Deliverable",
        foreign_keys="Deliverable.creator_id",
        back_populates="creator"
    )
    
    approved_deliverables = relationship(
        "Deliverable",
        foreign_keys="Deliverable.approved_by",
        back_populates="approver"
    )
    
    # Helper properties for frontend compatibility
    @property
    def avatar(self):
        """Alias for profile_image_url for frontend compatibility"""
        return self.profile_image_url
    
    @property
    def total_followers(self):
        """Calculate total followers across platforms"""
        total = (self.follower_count or 0)
        if self.tiktok_followers:
            total = max(total, self.tiktok_followers)
        total += (self.instagram_followers or 0) + (self.youtube_followers or 0)
        return total
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        fields = [
            self.first_name,
            self.last_name,
            self.email,
            self.phone,
            self.profile_image_url,
            self.bio,
            self.tiktok_handle,
            self.content_niche,
            self.location,
            self.shipping_address
        ]
        
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)