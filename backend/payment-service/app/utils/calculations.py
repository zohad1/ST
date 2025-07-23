
# app/utils/calculations.py (Enhanced version)
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def calculate_gmv_commission(gmv_amount: float, commission_rate: float) -> float:
    """Calculate GMV commission based on rate"""
    if gmv_amount <= 0 or commission_rate <= 0:
        return 0.0
    
    commission = gmv_amount * (commission_rate / 100)
    return round_currency(commission)

def calculate_bonus_tier_amount(gmv: float, bonus_tiers: List[Dict]) -> float:
    """Calculate bonus amount based on GMV and tier structure"""
    if not bonus_tiers or gmv <= 0:
        return 0.0
    
    total_bonus = 0.0
    
    for tier in sorted(bonus_tiers, key=lambda x: x.get('min_gmv', 0)):
        min_gmv = tier.get('min_gmv', 0)
        max_gmv = tier.get('max_gmv')
        bonus_type = tier.get('bonus_type', 'flat_amount')
        bonus_value = tier.get('bonus_value', 0)
        
        # Check if GMV falls within this tier
        if gmv >= min_gmv:
            if max_gmv is None or gmv <= max_gmv:
                if bonus_type == 'flat_amount':
                    total_bonus += bonus_value
                elif bonus_type == 'commission_increase':
                    # This would be an additional commission percentage
                    additional_commission = gmv * (bonus_value / 100)
                    total_bonus += additional_commission
    
    return round_currency(total_bonus)

def calculate_leaderboard_bonus(position: int, leaderboard_config: List[Dict]) -> float:
    """Calculate leaderboard bonus based on position"""
    if not leaderboard_config or position <= 0:
        return 0.0
    
    for config in leaderboard_config:
        position_start = config.get('position_start', 1)
        position_end = config.get('position_end', 1)
        bonus_amount = config.get('bonus_amount', 0)
        
        if position_start <= position <= position_end:
            return round_currency(bonus_amount)
    
    return 0.0

def round_currency(amount: float) -> float:
    """Round amount to 2 decimal places using banker's rounding"""
    if amount is None:
        return 0.0
    
    decimal_amount = Decimal(str(amount))
    rounded = decimal_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(rounded)

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string"""
    return f"${amount:.2f}"

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage with safe division"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def validate_earning_amounts(*amounts: float) -> bool:
    """Validate that all earning amounts are non-negative"""
    return all(amount >= 0 for amount in amounts if amount is not None)