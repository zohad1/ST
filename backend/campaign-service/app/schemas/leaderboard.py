
# app/schemas/leaderboard.py
from pydantic import BaseModel
from typing import List, Optional

class LeaderboardEntry(BaseModel):
    rank: int
    creator_id: str
    creator_name: str
    username: str
    avatar_url: Optional[str] = None
    gmv: float
    deliverables_completed: int
    total_deliverables: int
    engagement_rate: float
    total_views: int
    is_current_user: bool

class CampaignLeaderboard(BaseModel):
    campaign_id: str
    campaign_name: str
    total_creators: int
    total_gmv: float
    total_views: int
    entries: List[LeaderboardEntry]
    current_user_rank: Optional[int] = None
    current_user_gmv: Optional[float] = None