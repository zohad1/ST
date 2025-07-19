# app/services/tiktok_account_service.py - TikTok Account Integration Service
from sqlalchemy.orm import Session
from app.models.tiktok_models import TikTokAccount
from app.core.config import settings
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import httpx

class TikTokAccountService:
    def __init__(self, db: Session):
        self.db = db
        self.client_id = settings.TIKTOK_CLIENT_ID
        self.client_secret = settings.TIKTOK_CLIENT_SECRET
        self.redirect_uri = settings.TIKTOK_REDIRECT_URI
        self.api_base_url = "https://open.tiktokapis.com/v2"
    
    async def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get TikTok connection status for a user"""
        account = self.db.query(TikTokAccount).filter(
            TikTokAccount.user_id == user_id
        ).first()
        
        if not account:
            return {
                "status": "disconnected",
                "username": None,
                "userId": None,
                "connectedAt": None,
                "lastSync": None,
                "error": None
            }
        
        return {
            "status": "active" if account.is_active else "error",
            "username": account.username,
            "userId": account.tiktok_user_id,
            "connectedAt": account.connected_at.isoformat() if account.connected_at else None,
            "lastSync": account.last_sync_at.isoformat() if account.last_sync_at else None,
            "error": None
        }
    
    async def init_auth(self, user_id: str, redirect_uri: str) -> Dict[str, Any]:
        """Initialize TikTok OAuth authentication"""
        state = str(uuid.uuid4())
        
        # TikTok OAuth URL
        auth_url = (
            f"https://www.tiktok.com/v2/auth/authorize/"
            f"?client_key={self.client_id}"
            f"&scope=user.info.basic,video.list"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )
        
        return {
            "authUrl": auth_url,
            "state": state
        }
    
    async def handle_auth_callback(self, code: str, state: str, user_id: str) -> Dict[str, Any]:
        """Handle TikTok OAuth callback"""
        try:
            # Exchange code for access token
            token_data = await self._exchange_code_for_token(code)
            
            # Get user info
            user_info = await self._get_user_info(token_data["access_token"])
            
            # Save or update account
            account = self.db.query(TikTokAccount).filter(
                TikTokAccount.user_id == user_id
            ).first()
            
            if not account:
                account = TikTokAccount(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    tiktok_user_id=user_info["open_id"],
                    username=user_info.get("username", ""),
                    display_name=user_info.get("display_name", ""),
                    avatar_url=user_info.get("avatar_url", ""),
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    access_token_expire_in=token_data["expires_in"],
                    refresh_token_expire_in=token_data["refresh_expires_in"],
                    is_active=True,
                    connected_at=datetime.utcnow()
                )
                self.db.add(account)
            else:
                account.tiktok_user_id = user_info["open_id"]
                account.username = user_info.get("username", "")
                account.display_name = user_info.get("display_name", "")
                account.avatar_url = user_info.get("avatar_url", "")
                account.access_token = token_data["access_token"]
                account.refresh_token = token_data["refresh_token"]
                account.access_token_expire_in = token_data["expires_in"]
                account.refresh_token_expire_in = token_data["refresh_expires_in"]
                account.is_active = True
                account.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return await self.get_connection_status(user_id)
            
        except Exception as e:
            return {
                "status": "error",
                "username": None,
                "userId": None,
                "connectedAt": None,
                "lastSync": None,
                "error": str(e)
            }
    
    async def disconnect_account(self, user_id: str) -> bool:
        """Disconnect TikTok account"""
        try:
            account = self.db.query(TikTokAccount).filter(
                TikTokAccount.user_id == user_id
            ).first()
            
            if account:
                account.is_active = False
                account.access_token = None
                account.refresh_token = None
                self.db.commit()
            
            return True
        except Exception as e:
            print(f"Error disconnecting account: {e}")
            return False
    
    async def sync_account_data(self, user_id: str) -> bool:
        """Sync TikTok account data"""
        try:
            account = self.db.query(TikTokAccount).filter(
                TikTokAccount.user_id == user_id,
                TikTokAccount.is_active == True
            ).first()
            
            if not account:
                return False
            
            # Refresh token if needed
            if self._is_token_expired(account):
                await self._refresh_token(account)
            
            # Get updated user info
            user_info = await self._get_user_info(account.access_token)
            
            # Update account data
            account.username = user_info.get("username", account.username)
            account.display_name = user_info.get("display_name", account.display_name)
            account.avatar_url = user_info.get("avatar_url", account.avatar_url)
            account.follower_count = user_info.get("follower_count", account.follower_count)
            account.following_count = user_info.get("following_count", account.following_count)
            account.like_count = user_info.get("like_count", account.like_count)
            account.video_count = user_info.get("video_count", account.video_count)
            account.last_sync_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error syncing account data: {e}")
            return False
    
    async def get_account_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get TikTok account metrics"""
        account = self.db.query(TikTokAccount).filter(
            TikTokAccount.user_id == user_id,
            TikTokAccount.is_active == True
        ).first()
        
        if not account:
            return None
        
        return {
            "followers": account.follower_count,
            "following": account.following_count,
            "likes": account.like_count,
            "videos": account.video_count,
            "lastUpdated": account.last_sync_at.isoformat() if account.last_sync_at else None
        }
    
    async def _exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://open.tiktokapis.com/v2/oauth/token/",
                data={
                    "client_key": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            return response.json()["data"]
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get TikTok user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/user/info/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get user info: {response.text}")
            
            return response.json()["data"]["user"]
    
    async def _refresh_token(self, account: TikTokAccount) -> bool:
        """Refresh access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://open.tiktokapis.com/v2/oauth/token/",
                    data={
                        "client_key": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": account.refresh_token
                    }
                )
                
                if response.status_code != 200:
                    return False
                
                token_data = response.json()["data"]
                
                account.access_token = token_data["access_token"]
                account.refresh_token = token_data["refresh_token"]
                account.access_token_expire_in = token_data["expires_in"]
                account.refresh_token_expire_in = token_data["refresh_expires_in"]
                
                self.db.commit()
                return True
                
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def _is_token_expired(self, account: TikTokAccount) -> bool:
        """Check if access token is expired"""
        if not account.access_token_expire_in:
            return True
        
        # Add some buffer time (5 minutes)
        buffer_time = timedelta(minutes=5)
        expiry_time = account.updated_at + timedelta(seconds=account.access_token_expire_in) - buffer_time
        
        return datetime.utcnow() > expiry_time 