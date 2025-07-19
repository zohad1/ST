# app/api/v1/endpoints/tiktok_account.py - TikTok Account Integration Endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.tiktok_models import TikTokAccount
from app.services.tiktok_account_service import TikTokAccountService
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/status/{user_id}")
async def get_tiktok_connection_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get TikTok connection status for a user"""
    try:
        account_service = TikTokAccountService(db)
        status = await account_service.get_connection_status(user_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connection status: {str(e)}")

@router.post("/auth/init")
async def init_tiktok_auth(
    user_id: str,
    redirect_uri: str,
    db: Session = Depends(get_db)
):
    """Initialize TikTok OAuth authentication"""
    try:
        account_service = TikTokAccountService(db)
        auth_data = await account_service.init_auth(user_id, redirect_uri)
        return auth_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize auth: {str(e)}")

@router.post("/auth/callback")
async def handle_tiktok_auth_callback(
    code: str,
    state: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Handle TikTok OAuth callback"""
    account_service = TikTokAccountService(db)
    status = await account_service.handle_auth_callback(code, state, user_id)
    return status

@router.delete("/disconnect/{user_id}")
async def disconnect_tiktok(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Disconnect TikTok account"""
    account_service = TikTokAccountService(db)
    result = await account_service.disconnect_account(user_id)
    return {"success": result}

@router.post("/sync/{user_id}")
async def sync_tiktok_data(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Sync TikTok account data"""
    account_service = TikTokAccountService(db)
    result = await account_service.sync_account_data(user_id)
    return {"success": result}

@router.get("/metrics/{user_id}")
async def get_tiktok_metrics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get TikTok account metrics"""
    account_service = TikTokAccountService(db)
    metrics = await account_service.get_account_metrics(user_id)
    return metrics 