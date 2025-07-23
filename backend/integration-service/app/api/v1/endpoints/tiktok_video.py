from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_async_db
from app.services.tiktok_video_service import TikTokVideoService
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/sync-videos")
async def sync_tiktok_videos(
    creator_id: str = Body(...),
    db: AsyncSession = Depends(get_async_db)
):
    """Sync TikTok videos for a creator"""
    try:
        service = TikTokVideoService(db)
        result = await service.sync_videos_for_creator(creator_id)
        return result
    except Exception as e:
        logger.error(f"Failed to sync videos for creator {creator_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync videos")

@router.post("/mark-deliverable")
async def mark_video_as_deliverable(
    video_id: str = Body(...),
    deliverable_id: str = Body(...),
    creator_id: str = Body(...),
    db: AsyncSession = Depends(get_async_db)
):
    """Mark a TikTok video as a deliverable for a campaign"""
    try:
        service = TikTokVideoService(db)
        result = await service.mark_video_as_deliverable(video_id, deliverable_id, creator_id)
        return result
    except Exception as e:
        logger.error(f"Failed to mark video {video_id} as deliverable: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark deliverable")

@router.post("/attribute-gmv")
async def attribute_gmv_to_creator(
    creator_id: str = Body(...),
    db: AsyncSession = Depends(get_async_db)
):
    """Calculate GMV attribution for a creator"""
    try:
        service = TikTokVideoService(db)
        result = await service.calculate_gmv_attribution(creator_id)
        return result
    except Exception as e:
        logger.error(f"Failed to attribute GMV for creator {creator_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to attribute GMV") 