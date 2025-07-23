
# tests/test_validators.py
import pytest
from datetime import datetime, timedelta
from app.core.validators import CampaignValidator
from app.core.exceptions import ValidationException

class TestCampaignValidator:
    
    def test_validate_campaign_dates_valid(self):
        """Test valid campaign dates"""
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=30)
        
        # Should not raise exception
        CampaignValidator.validate_campaign_dates(start_date, end_date)
    
    def test_validate_campaign_dates_invalid_order(self):
        """Test invalid date order"""
        start_date = datetime.now() + timedelta(days=30)
        end_date = datetime.now() + timedelta(days=1)
        
        with pytest.raises(ValidationException) as exc_info:
            CampaignValidator.validate_campaign_dates(start_date, end_date)
        
        assert "start date must be before end date" in str(exc_info.value.message)
    
    def test_validate_campaign_dates_past_start(self):
        """Test past start date"""
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=30)
        
        with pytest.raises(ValidationException) as exc_info:
            CampaignValidator.validate_campaign_dates(start_date, end_date)
        
        assert "cannot be in the past" in str(exc_info.value.message)
    
    def test_validate_hashtag_valid(self):
        """Test valid hashtag"""
        CampaignValidator.validate_hashtag("#validhashtag")
        CampaignValidator.validate_hashtag("#valid_hashtag123")
    
    def test_validate_hashtag_invalid(self):
        """Test invalid hashtag"""
        with pytest.raises(ValidationException):
            CampaignValidator.validate_hashtag("invalidhashtag")  # Missing #
        
        with pytest.raises(ValidationException):
            CampaignValidator.validate_hashtag("#")  # Too short
        
        with pytest.raises(ValidationException):
            CampaignValidator.validate_hashtag("#invalid-hashtag")  # Invalid characters