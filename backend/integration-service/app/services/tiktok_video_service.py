# app/services/tiktok_video_service.py - Video tracking and attribution service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
import httpx

from app.models.tiktok_models import (
    TikTokVideo, TikTokVideoMetrics, TikTokAccount, TikTokOrder, 
    CampaignVideoDeliverable
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class TikTokVideoService:
    """Service for managing TikTok video data and tracking"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_base_url = "https://open.tiktokapis.com/v2"
    
    async def sync_creator_videos(
        self, 
        account_id: str, 
        limit: int = 50
    ) -> Dict[str, Any]:
        """Sync videos for a TikTok account"""
        try:
            # Get account details
            account = await self._get_account(account_id)
            if not account or not account.access_token:
                return {"success": False, "error": "Account not found or not authenticated"}
            
            # Fetch videos from TikTok API
            videos_data = await self._fetch_videos_from_api(account.access_token, limit)
            
            synced_count = 0
            updated_count = 0
            
            for video_data in videos_data.get("videos", []):
                video = await self._upsert_video(account_id, video_data)
                if video:
                    # Record metrics snapshot
                    await self._record_video_metrics(video.video_id, video_data)
                    
                    if video_data.get("is_new", True):
                        synced_count += 1
                    else:
                        updated_count += 1
            
            # Update account last sync time
            await self._update_account_sync_time(account_id)
            
            return {
                "success": True,
                "synced_videos": synced_count,
                "updated_videos": updated_count,
                "total_videos": len(videos_data.get("videos", []))
            }
            
        except Exception as e:
            logger.error(f"Error syncing videos for account {account_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def mark_video_as_deliverable(
        self,
        video_id: str,
        campaign_id: str,
        deliverable_id: str,
        creator_id: str
    ) -> Dict[str, Any]:
        """Mark a video as a campaign deliverable"""
        try:
            # Update video record
            stmt = (
                update(TikTokVideo)
                .where(TikTokVideo.video_id == video_id)
                .values(
                    campaign_id=campaign_id,
                    deliverable_id=deliverable_id,
                    is_deliverable=True,
                    deliverable_status="pending"
                )
            )
            await self.db.execute(stmt)
            
            # Create deliverable tracking record
            deliverable_record = CampaignVideoDeliverable(
                id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                deliverable_id=deliverable_id,
                creator_id=creator_id,
                video_id=video_id,
                submitted_at=datetime.utcnow(),
                status="pending"
            )
            
            self.db.add(deliverable_record)
            await self.db.commit()
            
            return {"success": True, "message": "Video marked as deliverable"}
            
        except Exception as e:
            logger.error(f"Error marking video {video_id} as deliverable: {e}")
            await self.db.rollback()
            return {"success": False, "error": str(e)}
    
    async def approve_deliverable_video(
        self,
        video_id: str,
        reviewer_id: str,
        notes: str = None
    ) -> Dict[str, Any]:
        """Approve a deliverable video"""
        try:
            # Update video status
            stmt = (
                update(TikTokVideo)
                .where(TikTokVideo.video_id == video_id)
                .values(deliverable_status="approved")
            )
            await self.db.execute(stmt)
            
            # Update deliverable record
            stmt = (
                update(CampaignVideoDeliverable)
                .where(CampaignVideoDeliverable.video_id == video_id)
                .values(
                    status="approved",
                    approved_at=datetime.utcnow(),
                    reviewer_id=reviewer_id,
                    reviewer_notes=notes
                )
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            return {"success": True, "message": "Deliverable approved"}
            
        except Exception as e:
            logger.error(f"Error approving deliverable {video_id}: {e}")
            await self.db.rollback()
            return {"success": False, "error": str(e)}
    
    async def get_creator_video_performance(
        self,
        creator_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get video performance metrics for a creator"""
        try:
            # Build query
            stmt = select(TikTokVideo).join(TikTokAccount).where(
                TikTokAccount.user_id == creator_id
            )
            
            if start_date:
                stmt = stmt.where(TikTokVideo.created_at >= start_date)
            if end_date:
                stmt = stmt.where(TikTokVideo.created_at <= end_date)
            
            result = await self.db.execute(stmt)
            videos = result.scalars().all()
            
            # Calculate aggregated metrics
            total_views = sum(video.view_count or 0 for video in videos)
            total_likes = sum(video.like_count or 0 for video in videos)
            total_comments = sum(video.comment_count or 0 for video in videos)
            total_shares = sum(video.share_count or 0 for video in videos)
            total_gmv = sum(float(video.attributed_gmv or 0) for video in videos)
            
            avg_engagement_rate = 0
            if total_views > 0:
                total_engagement = total_likes + total_comments + total_shares
                avg_engagement_rate = (total_engagement / total_views) * 100
            
            return {
                "total_videos": len(videos),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "total_gmv": total_gmv,
                "avg_engagement_rate": round(avg_engagement_rate, 2),
                "deliverable_videos": len([v for v in videos if v.is_deliverable])
            }
            
        except Exception as e:
            logger.error(f"Error getting creator performance for {creator_id}: {e}")
            return {"error": str(e)}
    
    async def get_top_performing_videos(
        self,
        shop_id: str = None,
        creator_id: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing videos by GMV or engagement"""
        try:
            stmt = select(TikTokVideo).options(selectinload(TikTokVideo.account))
            
            if creator_id:
                stmt = stmt.join(TikTokAccount).where(TikTokAccount.user_id == creator_id)
            
            # Order by attributed GMV first, then by engagement
            stmt = stmt.order_by(
                desc(TikTokVideo.attributed_gmv),
                desc(TikTokVideo.view_count)
            ).limit(limit)
            
            result = await self.db.execute(stmt)
            videos = result.scalars().all()
            
            video_list = []
            for video in videos:
                engagement_rate = 0
                if video.view_count and video.view_count > 0:
                    total_engagement = (video.like_count or 0) + (video.comment_count or 0) + (video.share_count or 0)
                    engagement_rate = (total_engagement / video.view_count) * 100
                
                video_list.append({
                    "video_id": video.video_id,
                    "title": video.title,
                    "creator": {
                        "username": video.account.username if video.account else None,
                        "display_name": video.account.display_name if video.account else None
                    },
                    "metrics": {
                        "views": video.view_count or 0,
                        "likes": video.like_count or 0,
                        "comments": video.comment_count or 0,
                        "shares": video.share_count or 0,
                        "engagement_rate": round(engagement_rate, 2)
                    },
                    "gmv_attributed": float(video.attributed_gmv or 0),
                    "orders_attributed": video.attributed_orders or 0,
                    "url": video.share_url,
                    "created_at": video.created_at.isoformat() if video.created_at else None,
                    "is_deliverable": video.is_deliverable
                })
            
            return video_list
            
        except Exception as e:
            logger.error(f"Error getting top performing videos: {e}")
            return []
    
    async def _get_account(self, account_id: str) -> Optional[TikTokAccount]:
        """Get TikTok account by ID"""
        stmt = select(TikTokAccount).where(TikTokAccount.id == account_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _fetch_videos_from_api(self, access_token: str, limit: int) -> Dict[str, Any]:
        """Fetch videos from TikTok API"""
        # Mock implementation - in production this would call actual TikTok API
        # For now, return mock data
        mock_videos = []
        for i in range(min(limit, 10)):  # Return up to 10 mock videos
            mock_videos.append({
                "video_id": f"mock_video_{i}_{uuid.uuid4().hex[:8]}",
                "title": f"Mock Video {i+1}",
                "description": f"This is a mock video description {i+1}",
                "view_count": 10000 + (i * 1000),
                "like_count": 800 + (i * 50),
                "comment_count": 50 + (i * 5),
                "share_count": 20 + (i * 2),
                "duration": 30 + (i * 5),
                "share_url": f"https://tiktok.com/@creator/video/mock_{i}",
                "cover_image_url": f"https://example.com/cover_{i}.jpg",
                "created_at": datetime.utcnow() - timedelta(days=i),
                "is_new": True
            })
        
        return {"videos": mock_videos}
    
    async def _upsert_video(self, account_id: str, video_data: Dict[str, Any]) -> Optional[TikTokVideo]:
        """Insert or update video record"""
        try:
            # Check if video exists
            stmt = select(TikTokVideo).where(TikTokVideo.video_id == video_data["video_id"])
            result = await self.db.execute(stmt)
            existing_video = result.scalar_one_or_none()
            
            if existing_video:
                # Update existing video
                stmt = (
                    update(TikTokVideo)
                    .where(TikTokVideo.video_id == video_data["video_id"])
                    .values(
                        view_count=video_data.get("view_count", 0),
                        like_count=video_data.get("like_count", 0),
                        comment_count=video_data.get("comment_count", 0),
                        share_count=video_data.get("share_count", 0),
                        updated_at=datetime.utcnow()
                    )
                )
                await self.db.execute(stmt)
                video_data["is_new"] = False
                return existing_video
            else:
                # Create new video
                video = TikTokVideo(
                    id=str(uuid.uuid4()),
                    account_id=account_id,
                    video_id=video_data["video_id"],
                    title=video_data.get("title"),
                    description=video_data.get("description"),
                    view_count=video_data.get("view_count", 0),
                    like_count=video_data.get("like_count", 0),
                    comment_count=video_data.get("comment_count", 0),
                    share_count=video_data.get("share_count", 0),
                    duration=video_data.get("duration"),
                    share_url=video_data.get("share_url"),
                    cover_image_url=video_data.get("cover_image_url"),
                    created_at=video_data.get("created_at", datetime.utcnow())
                )
                
                self.db.add(video)
                await self.db.flush()
                video_data["is_new"] = True
                return video
                
        except Exception as e:
            logger.error(f"Error upserting video {video_data.get('video_id')}: {e}")
            return None
    
    async def _record_video_metrics(self, video_id: str, video_data: Dict[str, Any]):
        """Record a metrics snapshot for a video"""
        try:
            metrics = TikTokVideoMetrics(
                id=str(uuid.uuid4()),
                video_id=video_id,
                view_count=video_data.get("view_count", 0),
                like_count=video_data.get("like_count", 0),
                comment_count=video_data.get("comment_count", 0),
                share_count=video_data.get("share_count", 0),
                recorded_at=datetime.utcnow()
            )
            
            # Calculate engagement rate
            if video_data.get("view_count", 0) > 0:
                total_engagement = (
                    video_data.get("like_count", 0) + 
                    video_data.get("comment_count", 0) + 
                    video_data.get("share_count", 0)
                )
                metrics.engagement_rate = (total_engagement / video_data["view_count"]) * 100
            
            self.db.add(metrics)
            
        except Exception as e:
            logger.error(f"Error recording metrics for video {video_id}: {e}")
    
    async def _update_account_sync_time(self, account_id: str):
        """Update the last sync time for an account"""
        try:
            stmt = (
                update(TikTokAccount)
                .where(TikTokAccount.id == account_id)
                .values(last_sync_at=datetime.utcnow())
            )
            await self.db.execute(stmt)
            
        except Exception as e:
            logger.error(f"Error updating sync time for account {account_id}: {e}")


class GMVAttributionService:
    """Service for attributing GMV to creators and videos"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def attribute_order_to_video(
        self,
        order_id: str,
        video_id: str,
        attribution_method: str = "last_click",
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """Attribute an order to a specific video"""
        try:
            # Update order with attribution
            stmt = (
                update(TikTokOrder)
                .where(TikTokOrder.order_id == order_id)
                .values(
                    attributed_video_id=video_id,
                    attribution_method=attribution_method,
                    attribution_confidence=confidence
                )
            )
            await self.db.execute(stmt)
            
            # Update video GMV attribution
            await self._update_video_attribution(video_id)
            await self.db.commit()
            
            return {"success": True, "message": "Order attributed to video"}
            
        except Exception as e:
            logger.error(f"Error attributing order {order_id} to video {video_id}: {e}")
            await self.db.rollback()
            return {"success": False, "error": str(e)}
    
    async def calculate_creator_gmv(
        self,
        creator_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate total GMV attributed to a creator"""
        try:
            # Query orders attributed to creator's videos
            stmt = (
                select(
                    func.sum(TikTokOrder.total_amount).label("total_gmv"),
                    func.count(TikTokOrder.id).label("order_count"),
                    func.count(func.distinct(TikTokOrder.attributed_video_id)).label("video_count")
                )
                .where(TikTokOrder.creator_id == creator_id)
            )
            
            if start_date:
                stmt = stmt.where(TikTokOrder.create_time >= int(start_date.timestamp()))
            if end_date:
                stmt = stmt.where(TikTokOrder.create_time <= int(end_date.timestamp()))
            
            result = await self.db.execute(stmt)
            data = result.first()
            
            total_gmv = float(data.total_gmv or 0)
            order_count = data.order_count or 0
            video_count = data.video_count or 0
            
            return {
                "total_gmv": total_gmv,
                "order_count": order_count,
                "video_count": video_count,
                "average_order_value": total_gmv / max(order_count, 1),
                "gmv_per_video": total_gmv / max(video_count, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating GMV for creator {creator_id}: {e}")
            return {"error": str(e)}
    
    async def _update_video_attribution(self, video_id: str):
        """Update GMV attribution for a video"""
        try:
            # Calculate total GMV and orders for this video
            stmt = (
                select(
                    func.sum(TikTokOrder.total_amount).label("total_gmv"),
                    func.count(TikTokOrder.id).label("order_count")
                )
                .where(TikTokOrder.attributed_video_id == video_id)
            )
            
            result = await self.db.execute(stmt)
            data = result.first()
            
            total_gmv = data.total_gmv or 0
            order_count = data.order_count or 0
            
            # Update video record
            stmt = (
                update(TikTokVideo)
                .where(TikTokVideo.video_id == video_id)
                .values(
                    attributed_gmv=total_gmv,
                    attributed_orders=order_count,
                    last_attribution_update=datetime.utcnow()
                )
            )
            await self.db.execute(stmt)
            
        except Exception as e:
            logger.error(f"Error updating attribution for video {video_id}: {e}") 