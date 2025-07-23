# app/services/dashboard_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, distinct
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import httpx

logger = logging.getLogger(__name__)

class DashboardService:
    """Service for aggregating dashboard data across all user types"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_creator_performance_data(
        self, 
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive creator performance data"""
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # In a real implementation, this would query TikTok video and order data
        # For now, return mock data that matches the expected structure
        
        # Calculate period-over-period changes
        views_change = self._calculate_change(450000, 380000)
        gmv_change = self._calculate_change(12500, 10800)
        
        return {
            "current_period": {
                "total_videos": 25,
                "total_views": 450000,
                "total_likes": 28500,
                "total_shares": 1200,
                "total_comments": 3400,
                "avg_engagement_rate": 7.2,
                "total_gmv": 12500.0,
                "total_orders": 85,
                "avg_order_value": 147.06
            },
            "changes": {
                "views_change": views_change,
                "gmv_change": gmv_change
            }
        }
    
    async def get_campaign_deliverables_status(
        self,
        user_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Get deliverable status for a campaign"""
        # This would query actual campaign deliverables
        # Mock implementation for now
        
        return {
            "completed": 8,
            "approved": 6,
            "pending": 2,
            "total_required": 10
        }
    
    async def get_agency_creator_metrics(
        self,
        agency_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated metrics for all creators under an agency"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # This would aggregate across all campaigns managed by the agency
        # Mock implementation for now
        
        return {
            "total_views": 2400000,
            "total_likes": 145000,
            "total_comments": 28000,
            "active_creators": 45,
            "total_posts": 320,
            "avg_posts_per_creator": 7.1,
            "total_payouts": 45860
        }
    
    async def get_content_performance_by_day(
        self,
        shop_id: str = None,
        creator_id: str = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get daily content performance metrics"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Generate mock daily data
        data = []
        current = start_date
        base_posts = 50
        
        while current <= end_date:
            # Simulate varying daily performance
            day_of_week = current.weekday()
            multiplier = 1.2 if day_of_week in [5, 6] else 1.0  # Weekend boost
            
            posts = int(base_posts * multiplier)
            views = posts * 2500
            likes = int(views * 0.08)
            
            data.append({
                "date": current.strftime("%b %d"),
                "posts": posts,
                "views": views,
                "likes": likes
            })
            current += timedelta(days=1)
        
        return data
    
    async def get_top_performing_content(
        self,
        shop_id: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing videos"""
        # This would query actual video performance data
        # Mock implementation for now
        
        mock_content = [
            {
                "video_id": "video_001",
                "title": "Summer Fashion Haul",
                "creator": {
                    "username": "@emmarodriguez",
                    "display_name": "Emma Rodriguez"
                },
                "metrics": {
                    "views": 125400,
                    "likes": 10289,
                    "comments": 892,
                    "shares": 234,
                    "engagement_rate": 9.2
                },
                "gmv_attributed": 3250.0,
                "url": "https://tiktok.com/@emmarodriguez/video/123",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "video_id": "video_002", 
                "title": "Tech Gadget Review",
                "creator": {
                    "username": "@sofichen",
                    "display_name": "Sofia Chen"
                },
                "metrics": {
                    "views": 98200,
                    "likes": 7365,
                    "comments": 623,
                    "shares": 187,
                    "engagement_rate": 8.3
                },
                "gmv_attributed": 2890.0,
                "url": "https://tiktok.com/@sofichen/video/456", 
                "created_at": "2024-01-14T15:20:00Z"
            }
        ]
        
        return mock_content[:limit]
    
    def _calculate_change(self, current: float, previous: float) -> str:
        """Calculate percentage change"""
        if previous == 0:
            return "+100%" if current > 0 else "0%"
        
        change = ((current - previous) / previous) * 100
        return f"{change:+.0f}%"
    
    def _calculate_engagement_rate(self, likes: int, comments: int, shares: int, views: int) -> float:
        """Calculate engagement rate for content"""
        if views == 0:
            return 0.0
        
        engagement = likes + comments + shares
        return (engagement / views) * 100


class GMVAttributionService:
    """Service for attributing GMV to creators"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def attribute_order_to_creator(
        self,
        order_id: str,
        attribution_method: str = "last_click"
    ) -> Optional[str]:
        """Attribute an order to a creator based on various methods"""
        # Implementation would depend on your attribution logic
        # - Last click: Last video viewed before purchase
        # - First click: First video that introduced product
        # - Linear: Split credit among all videos viewed
        # - Time decay: More recent videos get more credit
        
        # This would need to track user journey from video to purchase
        # For now, return mock attribution
        return "creator_123"
    
    async def calculate_creator_gmv(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate total GMV attributed to a creator"""
        # This would query actual order data with attribution
        # Mock implementation for now
        
        return {
            "total_gmv": 12500.0,
            "order_count": 85,
            "unique_products": 12,
            "average_order_value": 147.06,
            "attribution_confidence": 0.92
        }
    
    async def get_gmv_by_video(
        self,
        creator_id: str,
        video_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get GMV attribution for specific videos"""
        # Mock implementation
        return [
            {
                "video_id": "video_001",
                "gmv_attributed": 3250.0,
                "orders_attributed": 22,
                "attribution_method": "last_click",
                "confidence_score": 0.95
            },
            {
                "video_id": "video_002",
                "gmv_attributed": 2890.0, 
                "orders_attributed": 19,
                "attribution_method": "last_click",
                "confidence_score": 0.87
            }
        ]


class IntegrationDataService:
    """Service for syncing data from external platforms"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.integration_service_url = "http://localhost:8005"
    
    async def sync_creator_videos(self, creator_id: str) -> Dict[str, Any]:
        """Sync TikTok videos for a creator"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.integration_service_url}/api/v1/integrations/tiktok/sync-videos",
                    json={"creator_id": creator_id}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to sync videos for creator {creator_id}: {response.status_code}")
                    return {"success": False, "error": "Sync failed"}
                    
        except Exception as e:
            logger.error(f"Error syncing videos for creator {creator_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync_shop_orders(self, shop_id: str) -> Dict[str, Any]:
        """Sync TikTok Shop orders"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.integration_service_url}/api/v1/orders/sync",
                    headers={"X-Shop-ID": shop_id}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to sync orders for shop {shop_id}: {response.status_code}")
                    return {"success": False, "error": "Sync failed"}
                    
        except Exception as e:
            logger.error(f"Error syncing orders for shop {shop_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def track_deliverable_completion(
        self,
        deliverable_id: str,
        video_url: str,
        creator_id: str
    ) -> Dict[str, Any]:
        """Track when a deliverable is completed with a video"""
        try:
            # Extract TikTok video ID from URL
            video_id = self._extract_video_id_from_url(video_url)
            
            # Mark video as deliverable in integration service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.integration_service_url}/api/v1/integrations/tiktok/mark-deliverable",
                    json={
                        "video_id": video_id,
                        "deliverable_id": deliverable_id,
                        "creator_id": creator_id
                    }
                )
                
                return response.json() if response.status_code == 200 else {"success": False}
                
        except Exception as e:
            logger.error(f"Error tracking deliverable {deliverable_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_video_id_from_url(self, url: str) -> str:
        """Extract TikTok video ID from URL"""
        # Simple extraction - would need more robust parsing
        import re
        match = re.search(r'/video/(\d+)', url)
        return match.group(1) if match else "" 