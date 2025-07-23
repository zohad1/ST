
# app/core/validators.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.exceptions import ValidationException

class CampaignValidator:
    """Validation utilities for campaign data"""
    
    @staticmethod
    def validate_campaign_dates(start_date: Optional[datetime], end_date: Optional[datetime]):
        """Validate campaign date logic"""
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationException("Campaign start date must be before end date")
        
        if start_date and start_date < datetime.now():
            raise ValidationException("Campaign start date cannot be in the past")
    
    @staticmethod
    def validate_budget(total_budget: Optional[float], spent_amount: Optional[float] = 0):
        """Validate budget constraints"""
        if total_budget is not None and total_budget <= 0:
            raise ValidationException("Total budget must be greater than 0")
        
        if spent_amount and total_budget and spent_amount > total_budget:
            raise ValidationException("Spent amount cannot exceed total budget")
    
    @staticmethod
    def validate_creator_limits(max_creators: Optional[int], min_deliverables: Optional[int]):
        """Validate creator and deliverable limits"""
        if max_creators is not None and max_creators <= 0:
            raise ValidationException("Maximum creators must be greater than 0")
        
        if min_deliverables is not None and min_deliverables <= 0:
            raise ValidationException("Minimum deliverables must be greater than 0")
    
    @staticmethod
    def validate_payout_rates(base_payout: Optional[float], commission_rate: Optional[float]):
        """Validate payout rates"""
        if base_payout is not None and base_payout < 0:
            raise ValidationException("Base payout cannot be negative")
        
        if commission_rate is not None and (commission_rate < 0 or commission_rate > 100):
            raise ValidationException("Commission rate must be between 0 and 100")
    
    @staticmethod
    def validate_hashtag(hashtag: Optional[str]):
        """Validate hashtag format"""
        if hashtag:
            if not hashtag.startswith('#'):
                raise ValidationException("Hashtag must start with #")
            
            if len(hashtag) < 2:
                raise ValidationException("Hashtag must be at least 2 characters long")
            
            # Basic validation for hashtag format
            if not hashtag[1:].replace('_', '').isalnum():
                raise ValidationException("Hashtag can only contain letters, numbers, and underscores")
    
    @staticmethod
    def validate_product_links(product_links: Optional[List[str]]):
        """Validate TikTok product links"""
        if product_links:
            for link in product_links:
                if not link.startswith('https://'):
                    raise ValidationException("Product links must be HTTPS URLs")
                
                if 'tiktok' not in link.lower():
                    raise ValidationException("Product links must be TikTok URLs")