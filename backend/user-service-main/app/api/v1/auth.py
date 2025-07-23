# app/api/v1/auth.py - COMPLETE ASYNC VERSION

from fastapi import APIRouter, HTTPException, status, Depends, Body, Header, Request, UploadFile, File
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional
from uuid import UUID
import jwt

# FIXED: Use async version
from app.core.database import get_db  # This returns AsyncSession
from app.core.security import (
    verify_password,
    get_password_hash,
    create_token_pair,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_access_token,
    generate_verification_token,
    generate_token,
    SECRET_KEY,
    REFRESH_SECRET_KEY,
    ALGORITHM,
    validate_password_strength
)
from app.models.user import User
from app.core.config import settings
from app.schemas.auth import (
    SignupRequest, LoginRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, EmailVerificationRequest, MessageResponse
)
from app.models.user_token import UserToken, TokenType
from app.services.auth_service import auth_service
from app.services.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

# Request/Response models
class AuthResponse(BaseModel):
    success: bool
    data: dict
    message: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# ASYNC dependency function for getting current user
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)  # Use AsyncSession
) -> User:
    """Get current user from JWT token - ASYNC VERSION"""
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Extract token from header
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # ASYNC database operations
    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

@router.post("/signup", response_model=MessageResponse)
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and send verification email - ASYNC VERSION"""
    try:
        logger.info(f"📝 Signup request received: {signup_data}")
        
        # Check if email already exists
        stmt = select(User).where(User.email == signup_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(signup_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Generate username
        base_username = signup_data.email.split('@')[0].lower()
        username = base_username
        counter = 1
        
        while True:
            username_stmt = select(User).where(User.username == username)
            username_result = await db.execute(username_stmt)
            if not username_result.scalar_one_or_none():
                break
            username = f"{base_username}{counter}"
            counter += 1
        
        # Create user
        user_data = {
            "email": signup_data.email,
            "username": username,
            "hashed_password": get_password_hash(signup_data.password),
            "role": signup_data.role,
            "is_active": True,
            "email_verified": False,
            "profile_completion_percentage": 30
        }
        
        # Add optional fields
        if hasattr(signup_data, 'first_name') and signup_data.first_name:
            user_data["first_name"] = signup_data.first_name
        if hasattr(signup_data, 'last_name') and signup_data.last_name:
            user_data["last_name"] = signup_data.last_name
        
        user = User(**user_data)
        db.add(user)
        await db.flush()  # Get user ID without committing
        
        # Create verification token
        verification_token = UserToken(
            user_id=str(user.id),
            token_type="email_verification",  # Use string value instead of enum
            token_value=generate_token(32),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            is_used=False
        )
        
        db.add(verification_token)
        await db.commit()
        await db.refresh(user)
        
        # Send verification email
        try:
            email_service.send_verification_email(
                user.email,
                user.first_name or user.username,
                verification_token.token_value
            )
            message = "Account created successfully. Please check your email to verify your account."
        except Exception as e:
            logger.warning(f"Failed to send verification email: {e}")
            message = "Account created successfully. Verification email could not be sent."
        
        return MessageResponse(
            message=message,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Signup error: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email with token - ASYNC VERSION"""
    try:
        logger.info(f"🔍 Email verification attempt with token: {verification_data.token[:8]}...")
        
        # Find verification token
        stmt = select(UserToken).where(
            UserToken.token_value == verification_data.token,
            UserToken.token_type == "email_verification",  # Use string value instead of enum
            UserToken.is_used == False,
            UserToken.expires_at > datetime.now(timezone.utc)
        )
        result = await db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            logger.warning(f"❌ Invalid or expired token: {verification_data.token[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        logger.info(f"✅ Token found for user: {token.user_id}")
        
        # Get user
        user_stmt = select(User).where(User.id == token.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.error(f"❌ User not found for token user_id: {token.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"✅ User found: {user.email}, current email_verified: {user.email_verified}")
        
        # Mark token as used and verify user
        token.is_used = True
        user.email_verified = True
        user.profile_completion_percentage = max(user.profile_completion_percentage, 40)
        
        # Explicitly commit the changes
        await db.commit()
        
        # Refresh the user object to ensure we have the latest data
        await db.refresh(user)
        
        logger.info(f"✅ Email verified successfully for user: {user.email}")
        logger.info(f"✅ Updated email_verified: {user.email_verified}")
        logger.info(f"✅ Updated profile_completion_percentage: {user.profile_completion_percentage}")
        
        # Send welcome email
        try:
            email_service.send_welcome_email(
                user.email,
                user.first_name or user.username,
                user.role.value
            )
            logger.info(f"✅ Welcome email sent to: {user.email}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to send welcome email: {e}")
        
        return MessageResponse(
            message="Email verified successfully! Welcome to LaunchPAID.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Email verification error: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )

# Add this endpoint to your app/api/v1/auth.py file
# Insert this right after the verify_email endpoint

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    resend_data: dict,  # Accept generic dict since we need just email
    db: AsyncSession = Depends(get_db)
):
    """Resend verification email - ASYNC VERSION"""
    try:
        # Get email from request
        email = resend_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Find user
        stmt = select(User).where(User.email == email.lower().strip())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists or not for security
            return MessageResponse(
                message="If your email is registered and unverified, you will receive a verification link.",
                success=True
            )
        
        if user.email_verified:
            return MessageResponse(
                message="Email is already verified.",
                success=True
            )
        
        # Invalidate existing verification tokens for this user
        existing_tokens_stmt = select(UserToken).where(
            UserToken.user_id == str(user.id),
            UserToken.token_type == "email_verification",  # Use string value instead of enum
            UserToken.is_used == False
        )
        existing_result = await db.execute(existing_tokens_stmt)
        existing_tokens = existing_result.scalars().all()
        
        for token in existing_tokens:
            token.is_used = True
        
        # Create new verification token
        verification_token = UserToken(
            user_id=str(user.id),
            token_type="email_verification",  # Use string value instead of enum
            token_value=generate_token(32),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            is_used=False
        )
        
        db.add(verification_token)
        await db.commit()
        
        # Send verification email
        try:
            email_service.send_verification_email(
                user.email,
                user.first_name or user.username,
                verification_token.token_value
            )
            message = "Verification email sent successfully."
        except Exception as e:
            logger.warning(f"Failed to send verification email: {e}")
            message = "If your email is registered and unverified, you will receive a verification link."
        
        return MessageResponse(
            message=message,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resend verification error: {str(e)}")
        await db.rollback()
        # Always return success to prevent email enumeration
        return MessageResponse(
            message="If your email is registered and unverified, you will receive a verification link.",
            success=True
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user with token generation - ASYNC VERSION"""
    try:
        # Validate input
        if not login_data.email or not login_data.email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        if not login_data.password or not login_data.password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )
        
        # Normalize email
        email = login_data.email.strip().lower()
        
        # Find user by email
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No account found with this email address"
            )
        
        # Check if email is verified
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please verify your email before logging in. Check your inbox for a verification link."
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password. Please try again."
            )
        
        # Generate access and refresh tokens
        access_token, refresh_token = create_token_pair(
            user_id=str(user.id),
            user_role=user.role.value
        )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await db.commit()

        # Send login notification email
        try:
            ip_address = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")[:150]
            email_service.send_login_notification_email(
                to_email=user.email,
                username=user.first_name or user.username,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.warning(f"Failed to send login notification email: {e}")
        
        return AuthResponse(
            success=True,
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "role": user.role.value,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "email_verified": user.email_verified,
                    "company_name": getattr(user, 'company_name', None),
                    "profile_completion": user.profile_completion_percentage,
                }
            },
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email - ASYNC VERSION"""
    try:
        # Find user
        stmt = select(User).where(User.email == forgot_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists or not for security
            return MessageResponse(
                message="If an account with this email exists, a password reset link has been sent.",
                success=True
            )
        
        # Create password reset token
        reset_token = UserToken(
            user_id=str(user.id),
            token_type=TokenType.PASSWORD_RESET,
            token_value=generate_token(32),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            is_used=False
        )
        
        db.add(reset_token)
        await db.commit()
        
        # Send password reset email
        try:
            email_service.send_password_reset_email(
                user.email,
                user.first_name or user.username,
                reset_token.token_value
            )
        except Exception as e:
            logger.warning(f"Failed to send password reset email: {e}")
        
        return MessageResponse(
            message="If an account with this email exists, a password reset link has been sent.",
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Password reset error: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token - ASYNC VERSION"""
    try:
        # Find token
        stmt = select(UserToken).where(
            UserToken.token_value == reset_data.token,
            UserToken.token_type == TokenType.PASSWORD_RESET,
            UserToken.is_used == False,
            UserToken.expires_at > datetime.now(timezone.utc)
        )
        result = await db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user
        user_stmt = select(User).where(User.id == token.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(reset_data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Update password and mark token as used
        user.hashed_password = get_password_hash(reset_data.new_password)
        token.is_used = True
        
        await db.commit()
        
        return MessageResponse(
            message="Password reset successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Password reset error: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.get("/profile")
@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile - for frontend compatibility"""
    return {
        "success": True,
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role.value,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "is_active": current_user.is_active,
            "email_verified": current_user.email_verified,
            "company_name": getattr(current_user, 'company_name', None),
            "profile_completion": current_user.profile_completion_percentage,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            # Additional profile fields
            "phone": current_user.phone,
            "gender": current_user.gender.value if current_user.gender else None,
            "bio": current_user.bio,
            "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
            "profile_image_url": current_user.profile_image_url,
            # Social media handles
            "tiktok_handle": current_user.tiktok_handle,
            "instagram_handle": current_user.instagram_handle,
            "discord_handle": current_user.discord_handle,
            # Address fields
            "address_line1": current_user.address_line1,
            "address_line2": current_user.address_line2,
            "city": current_user.city,
            "state": current_user.state,
            "postal_code": current_user.postal_code,
            "country": current_user.country,
            # Creator specific fields
            "content_niche": current_user.content_niche,
            "follower_count": current_user.follower_count,
            "average_views": current_user.average_views,
            "engagement_rate": float(current_user.engagement_rate) if current_user.engagement_rate else None,
        }
    }

@router.put("/profile")
async def update_current_user_profile(
    profile_update: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile - ASYNC VERSION"""
    try:
        # Clean and validate the update data
        update_data = {}
        
        # Fields that can be set to None when empty
        nullable_fields = [
            'phone', 'first_name', 'last_name', 'bio', 'tiktok_handle', 
            'instagram_handle', 'discord_handle', 'date_of_birth',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'content_niche'
        ]
        
        for field, value in profile_update.items():
            if hasattr(current_user, field):
                # Handle empty strings for optional fields - convert to None
                if value == "" and field in nullable_fields:
                    update_data[field] = None
                elif value == "" and field == 'gender':
                    # Skip gender if it's empty string - don't update it
                    continue
                elif value is not None:
                    update_data[field] = value
        
        logger.info(f"🔧 Updating profile with data: {update_data}")
        
        # Update only valid fields
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        return {
            "success": True,
            "data": {
                "id": str(current_user.id),
                "email": current_user.email,
                "username": current_user.username,
                "role": current_user.role.value,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "is_active": current_user.is_active,
                "email_verified": current_user.email_verified,
                "company_name": getattr(current_user, 'company_name', None),
                "profile_completion": current_user.profile_completion_percentage,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                # Additional profile fields  
                "phone": current_user.phone,
                "gender": current_user.gender.value if current_user.gender else None,
                "bio": current_user.bio,
                "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
                "profile_image_url": current_user.profile_image_url,
                # Social media handles
                "tiktok_handle": current_user.tiktok_handle,
                "instagram_handle": current_user.instagram_handle,
                "discord_handle": current_user.discord_handle,
                # Address fields
                "address_line1": current_user.address_line1,
                "address_line2": current_user.address_line2,
                "city": current_user.city,
                "state": current_user.state,
                "postal_code": current_user.postal_code,
                "country": current_user.country,
                # Creator specific fields
                "content_niche": current_user.content_niche,
                "follower_count": current_user.follower_count,
                "average_views": current_user.average_views,
                "engagement_rate": float(current_user.engagement_rate) if current_user.engagement_rate else None,
            }
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token - ASYNC VERSION"""
    try:
        # Decode refresh token
        payload = decode_refresh_token(request.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": "Invalid refresh token",
                    "message": "Please login again"
                }
            )
        
        # Get user
        user_id = payload.get("sub")
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": "User not found",
                    "message": "Please login again"
                }
            )
        
        # Create new token pair with role
        new_access_token, new_refresh_token = create_token_pair(
            user_id=str(user.id),
            user_role=user.role.value
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "message": "Token refresh failed"
            }
        )

@router.get("/test")
async def test_auth_endpoint():
    """Test endpoint to verify auth router is working"""
    return {"message": "Auth router is working!", "status": "success"}

@router.post("/test-signup")
async def test_signup_data(request: dict):
    """Test endpoint to see what data is being sent"""
    logger.info(f"📝 Test signup data received: {request}")
    return {"message": "Data received", "data": request}

@router.get("/debug/verification/{token}")
async def debug_verification_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to check verification token status"""
    try:
        # Find verification token
        stmt = select(UserToken).where(
            UserToken.token_value == token,
            UserToken.token_type == "email_verification"  # Use string value instead of enum
        )
        result = await db.execute(stmt)
        token_obj = result.scalar_one_or_none()
        
        if not token_obj:
            return {
                "token_exists": False,
                "message": "Token not found"
            }
        
        # Get user
        user_stmt = select(User).where(User.id == token_obj.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        return {
            "token_exists": True,
            "token_details": {
                "id": str(token_obj.id),
                "user_id": str(token_obj.user_id),
                "token_type": token_obj.token_type,
                "is_used": token_obj.is_used,
                "is_expired": token_obj.is_expired,
                "expires_at": token_obj.expires_at.isoformat() if token_obj.expires_at else None,
                "created_at": token_obj.created_at.isoformat() if token_obj.created_at else None
            },
            "user_details": {
                "id": str(user.id) if user else None,
                "email": user.email if user else None,
                "email_verified": user.email_verified if user else None,
                "profile_completion_percentage": user.profile_completion_percentage if user else None
            } if user else None
        }
        
    except Exception as e:
        logger.error(f"Debug verification error: {str(e)}")
        return {
            "error": str(e)
        }