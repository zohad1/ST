# app/api/v1/auth.py - Fixed version
from fastapi import APIRouter, HTTPException, status, Depends, Body, Header, Request, UploadFile, File
import os
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional
from uuid import UUID
import jwt

from app.core.database import get_db
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

# Dependency function for getting current user
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    
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
    
    # Get user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
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
    db: Session = Depends(get_db)
):
    """
    Register a new user and send verification email
    """
    try:
        # Debug logging
        logger.info(f"📝 Signup request received: {signup_data}")
        logger.info(f"📝 Role type: {type(signup_data.role)}, Value: {signup_data.role}")
        logger.info(f"📝 Username: {signup_data.username}")
        
        # Create user and verification token
        user, verification_message = auth_service.signup(db, signup_data)
        
        return MessageResponse(
            message=verification_message,
            success=True
        )
        
    except ValueError as e:
        logger.error(f"❌ Signup validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token
    """
    try:
        # Find the token
        token = db.query(UserToken).filter(
            UserToken.token_value == verification_data.token,
            UserToken.token_type == TokenType.EMAIL_VERIFICATION,
            UserToken.is_used == False,
            UserToken.expires_at > datetime.now(timezone.utc)
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Get the user
        user = db.query(User).filter(User.id == token.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Mark token as used
        token.is_used = True
        
        # Mark user as verified
        user.email_verified = True
        
        db.commit()
        
        # Send welcome email
        try:
            email_service.send_welcome_email(
                user.email,
                user.display_name,
                user.role.value
            )
        except Exception as e:
            # Log error but don't fail the verification
            print(f"Failed to send welcome email: {e}")
        
        return MessageResponse(
            message="Email verified successfully! Welcome to LaunchPAID.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Resend verification email
    """
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Create new verification token
        verification_token = auth_service._create_token(
            db,
            str(user.id),
            TokenType.EMAIL_VERIFICATION,
            expires_hours=24
        )
        
        # Send verification email
        email_sent = email_service.send_verification_email(
            user.email,
            user.display_name,
            verification_token.token_value
        )
        
        if email_sent:
            return MessageResponse(
                message="Verification email sent successfully",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Send password reset email
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == forgot_data.email).first()
        if not user:
            # Don't reveal if email exists or not for security
            return MessageResponse(
                message="If an account with this email exists, a password reset link has been sent.",
                success=True
            )
        
        # Create password reset token
        reset_token = auth_service._create_token(
            db,
            str(user.id),
            TokenType.PASSWORD_RESET,
            expires_hours=1
        )
        
        # Send password reset email
        email_sent = email_service.send_password_reset_email(
            user.email,
            user.display_name,
            reset_token.token_value
        )
        
        if email_sent:
            return MessageResponse(
                message="If an account with this email exists, a password reset link has been sent.",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with token
    """
    try:
        # Find the token
        token = db.query(UserToken).filter(
            UserToken.token_value == reset_data.token,
            UserToken.token_type == TokenType.PASSWORD_RESET,
            UserToken.is_used == False,
            UserToken.expires_at > datetime.now(timezone.utc)
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get the user
        user = db.query(User).filter(User.id == token.user_id).first()
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
        
        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        
        # Mark token as used
        token.is_used = True
        
        db.commit()
        
        return MessageResponse(
            message="Password reset successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user with token generation
    """
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
        user = db.query(User).filter(User.email == email).first()
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
        
        # Generate access and refresh tokens WITH role claim so other services can authorize properly
        access_token, refresh_token = create_token_pair(
            user_id=str(user.id),
            user_role=user.role.value
        )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.commit()

        # ------------------------------
        # Send login notification email
        # ------------------------------
        try:
            ip_address = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")[:150]
            email_service.send_login_notification_email(
                to_email=user.email,
                username=user.display_name,
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
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "isActive": user.is_active,
                    "emailVerified": user.email_verified,
                    "companyName": getattr(user, 'company_name', None),
                    "profileCompletion": user.profile_completion_percentage,
                }
            },
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
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
            "firstName": current_user.first_name,
            "lastName": current_user.last_name,
            "isActive": current_user.is_active,
            "emailVerified": current_user.email_verified,
            "companyName": getattr(current_user, 'company_name', None),
            "profileCompletion": current_user.profile_completion_percentage,
            "createdAt": current_user.created_at.isoformat() if current_user.created_at else None,
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
    db: Session = Depends(get_db)
):
    """Update current user profile - for frontend compatibility"""
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
        
        print(f"🔧 Updating profile with data: {update_data}")
        
        # Update only valid fields
        for field, value in update_data.items():
            if hasattr(current_user, field):
                print(f"🔧 Setting {field} = {value}")
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "data": {
                "id": str(current_user.id),
                "email": current_user.email,
                "username": current_user.username,
                "role": current_user.role.value,
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "isActive": current_user.is_active,
                "emailVerified": current_user.email_verified,
                "companyName": getattr(current_user, 'company_name', None),
                "profileCompletion": current_user.profile_completion_percentage,
                "createdAt": current_user.created_at.isoformat() if current_user.created_at else None,
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
        db.rollback()
        print(f"❌ Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

# ---------------------------------------------------------------------------
# 📸 Profile Image Upload Endpoint
# ---------------------------------------------------------------------------

# FastAPI UploadFile returns SpooledTemporaryFile asynchronously.
# This endpoint saves the uploaded image to "static/profile_images" directory
# and updates the user's profile_image_url field. The resulting URL is served
# via the /static mount configured in main.py.


@router.post("/profile-image")
async def upload_profile_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new profile image for the current user."""

    # Validate content type
    if file.content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise HTTPException(status_code=400, detail="Invalid image type. Only JPEG, PNG, WEBP or GIF allowed.")

    # Build storage path
    static_dir = os.path.join(os.getcwd(), "static", "profile_images")
    os.makedirs(static_dir, exist_ok=True)

    # Preserve extension
    ext = file.filename.split(".")[-1].lower()
    filename = f"{current_user.id}.{ext}"
    file_path = os.path.join(static_dir, filename)

    # Save file to disk
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Failed to save uploaded image: {e}")
        raise HTTPException(status_code=500, detail="Failed to save image")

    # Build public URL (served via /static)
    # Use request.base_url to get the host the client is connecting to
    base_url = str(request.base_url).rstrip("/")  # e.g. http://localhost:8000
    public_url = f"{base_url}/static/profile_images/{filename}"

    # Update user record
    current_user.profile_image_url = public_url
    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Profile image uploaded successfully",
        "data": {
            "profile_image_url": public_url
        }
    }

@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
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
        user = db.query(User).filter(User.id == user_id).first()
        
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

# Add other endpoints (register, logout, etc.) here...
@router.get("/test")
async def test_auth_endpoint():
    """Test endpoint to verify auth router is working"""
    return {"message": "Auth router is working!", "status": "success"}

@router.post("/test-signup")
async def test_signup_data(request: dict):
    """Test endpoint to see what data is being sent"""
    logger.info(f"📝 Test signup data received: {request}")
    return {"message": "Data received", "data": request}