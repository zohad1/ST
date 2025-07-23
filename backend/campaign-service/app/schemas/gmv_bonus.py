
# app/schemas/gmv_bonus.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class GMVBonusTierBase(BaseModel):
    tier_name: str
    min_gmv: float
    max_gmv: Optional[float] = None
    bonus_type: str  # 'flat_amount', 'commission_increase'
    bonus_value: float

class GMVBonusTierCreate(GMVBonusTierBase):
    pass

class GMVBonusTierResponse(GMVBonusTierBase):
    id: UUID
    campaign_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
