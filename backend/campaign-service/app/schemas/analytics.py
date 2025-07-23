from pydantic import BaseModel

class CampaignAnalytics(BaseModel):
    campaign_id: str
    campaign_name: str
    current_gmv: float
    target_gmv: float
    gmv_progress_percentage: float
    total_deliverables: int
    completed_deliverables: int
    deliverable_progress_percentage: float
    days_remaining: int
    campaign_status: str  # 'active', 'ending_soon', 'completed', 'draft'
    user_rank: int
    total_creators: int
    user_gmv: float
    user_deliverables_completed: int
    user_total_deliverables: int
    user_engagement_rate: float
    user_total_views: int 