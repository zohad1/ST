# app/schemas/application.py
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.campaign import ApplicationStatus

class CreatorApplicationBase(BaseModel):
    campaign_id: UUID
    segment_id: Optional[UUID] = None

class CreatorApplicationCreate(CreatorApplicationBase):
    application_data: Optional[dict] = None

class CreatorApplicationUpdate(BaseModel):
    status: str  # Change to string since your model uses string
    rejection_reason: Optional[str] = None
    review_notes: Optional[str] = None
    
    class Config:
        use_enum_values = True

# Creator info schema for nested response
class CreatorInfo(BaseModel):
    id: UUID
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    profile_completion: Optional[int] = None
    total_followers: Optional[int] = None
    tiktok_handle: Optional[str] = None
    tiktok_followers: Optional[int] = None
    instagram_handle: Optional[str] = None
    instagram_followers: Optional[int] = None
    youtube_handle: Optional[str] = None
    youtube_followers: Optional[int] = None
    audience_gender: Optional[Dict[str, Optional[float]]] = None  # CHANGED: Allow None values
    primary_age: Optional[str] = None
    location: Optional[str] = None
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    niche: Optional[str] = None
    shipping_address: Optional[str] = None

    class Config:
        from_attributes = True

# Campaign info schema for nested response
class CampaignInfo(BaseModel):
    id: UUID
    name: str
    status: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class CreatorApplicationResponse(CreatorApplicationBase):
    id: UUID
    creator_id: UUID
    status: str  # CHANGED: Use string to match your model
    applied_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[UUID] = None
    reviewer_id: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    review_notes: Optional[str] = None
    application_data: Optional[dict] = None
    
    # New fields for frontend compatibility
    previous_gmv: Optional[float] = None
    engagement_rate: Optional[float] = None
    application_message: Optional[str] = None
    follower_count: Optional[int] = None  # Add this field
    
    # Nested objects with creator and campaign details
    creator: Optional[CreatorInfo] = None
    campaign: Optional[CampaignInfo] = None

    class Config:
        from_attributes = True
        use_enum_values = True
        
    @classmethod
    def from_orm_with_relations(cls, application, include_creator=True, include_campaign=True):
        """Create response with related data"""
        data = {
            "id": application.id,
            "creator_id": application.creator_id,
            "campaign_id": application.campaign_id,
            "segment_id": application.segment_id,
            "status": application.status,
            "applied_at": application.applied_at,
            "reviewed_at": getattr(application, 'reviewed_at', None),
            "reviewed_by": getattr(application, 'reviewed_by', None),
            "reviewer_id": getattr(application, 'reviewed_by', None),  # For frontend compatibility
            "rejection_reason": getattr(application, 'rejection_reason', None),
            "review_notes": getattr(application, 'review_notes', None),
            "application_data": application.application_data,
            "follower_count": getattr(application, 'follower_count', 0),
        }
        
        # Extract application message and metrics from application_data or direct fields
        if hasattr(application, 'application_message') and application.application_message:
            data["application_message"] = application.application_message
        elif application.application_data:
            data["application_message"] = application.application_data.get("message")
            
        if hasattr(application, 'previous_gmv') and application.previous_gmv is not None:
            data["previous_gmv"] = float(application.previous_gmv)
        elif application.application_data:
            data["previous_gmv"] = application.application_data.get("previous_gmv")
            
        if hasattr(application, 'engagement_rate') and application.engagement_rate is not None:
            data["engagement_rate"] = float(application.engagement_rate)
        elif application.application_data:
            data["engagement_rate"] = application.application_data.get("engagement_rate")
        
        # Include creator details if available
        if include_creator and hasattr(application, 'creator') and application.creator:
            creator = application.creator
            
            # FIXED: Handle None values for audience percentages
            male_percentage = getattr(creator, 'audience_male_percentage', None)
            female_percentage = getattr(creator, 'audience_female_percentage', None)
            
            # Only create audience_gender if we have valid values
            audience_gender = None
            if male_percentage is not None or female_percentage is not None:
                audience_gender = {
                    "male": float(male_percentage) if male_percentage is not None else 50.0,
                    "female": float(female_percentage) if female_percentage is not None else 50.0
                }
            
            data["creator"] = {
                "id": creator.id,
                "username": creator.username,
                "first_name": creator.first_name,
                "last_name": creator.last_name,
                "email": creator.email,
                "phone": creator.phone,
                "avatar": getattr(creator, 'profile_image_url', None),
                "profile_completion": calculate_profile_completion(creator),
                "total_followers": getattr(creator, 'follower_count', 0),
                "tiktok_handle": getattr(creator, 'tiktok_handle', None),
                "tiktok_followers": getattr(creator, 'tiktok_followers', getattr(creator, 'follower_count', 0)),
                "instagram_handle": getattr(creator, 'instagram_handle', None),
                "instagram_followers": getattr(creator, 'instagram_followers', 0),
                "youtube_handle": getattr(creator, 'youtube_handle', None),
                "youtube_followers": getattr(creator, 'youtube_followers', 0),
                "audience_gender": audience_gender,  # Use the processed value
                "primary_age": getattr(creator, 'primary_age_group', None),
                "location": getattr(creator, 'location', getattr(creator, 'city', None)),
                "age": getattr(creator, 'age', None),
                "ethnicity": getattr(creator, 'ethnicity', None),
                "niche": getattr(creator, 'content_niche', None),
                "shipping_address": getattr(creator, 'shipping_address', None)
            }
        
        # Include campaign details if available
        if include_campaign and hasattr(application, 'campaign') and application.campaign:
            campaign = application.campaign
            data["campaign"] = {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
                "description": getattr(campaign, 'description', None)
            }
        
        return cls(**data)


def calculate_profile_completion(user) -> int:
    """Calculate profile completion percentage for a creator."""
    fields = [
        user.first_name,
        user.last_name,
        user.email,
        user.phone,
        getattr(user, 'profile_image_url', None),
        getattr(user, 'bio', None),
        getattr(user, 'tiktok_handle', None),
        getattr(user, 'content_niche', None),
        getattr(user, 'location', getattr(user, 'city', None)),  # Fallback to city
        getattr(user, 'shipping_address', getattr(user, 'address_line1', None))  # Fallback to address
    ]
    
    completed = sum(1 for field in fields if field)
    return int((completed / len(fields)) * 100)