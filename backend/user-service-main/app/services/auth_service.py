# app/services/auth_service.py - Complete Async Version
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, select
import logging
import secrets

from app.models.user import User, UserRole
from app.models.user_token import UserToken, TokenType
from app.schemas.auth import (
    SignupRequest, LoginRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, EmailVerificationRequest
)
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_refresh_token,
    validate_password_strength, generate_token, create_token_pair
)
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class AuthService:
    """Enterprise-grade authentication service with token management - Async Version"""
    
    async def _create_token(self, db: AsyncSession, user_id: str, token_type: str, 
                           expires_hours: int = 24, token_value: Optional[str] = None) -> UserToken:
        """
        Create a new token for user (ASYNC)
        
        Args:
            db: Async database session
            user_id: User UUID
            token_type: Type of token (string value)
            expires_hours: Hours until expiration
            token_value: Optional custom token value
            
        Returns:
            UserToken instance
        """
        # Invalidate any existing tokens of the same type
        existing_query = select(UserToken).where(
            and_(
                UserToken.user_id == user_id,
                UserToken.token_type == token_type,
                UserToken.is_used == False
            )
        )
        
        result = await db.execute(existing_query)
        existing_tokens = result.scalars().all()
        
        for token in existing_tokens:
            token.is_used = True
        
        # Create new token
        token = UserToken(
            user_id=user_id,
            token_type=token_type,
            token_value=token_value or secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_hours),
            is_used=False
        )
        
        db.add(token)
        await db.flush()  # Get the token ID without committing
        return token
    
    def _generate_username(self, email: str, role: UserRole, company_name: Optional[str] = None) -> str:
        """Generate username from email or company name"""
        base_username = email.split('@')[0].lower()
        
        # For brands/agencies, try to use company name
        if role in [UserRole.AGENCY, UserRole.BRAND] and company_name:
            # Convert company name to username format
            base_username = ''.join(c.lower() if c.isalnum() else '_' for c in company_name)
            base_username = base_username.strip('_')[:50]  # Limit length
        
        return base_username
    
    async def signup(self, db: AsyncSession, signup_data: SignupRequest) -> Tuple[User, str]:
        """
        Register a new user with enhanced profile fields (ASYNC)
        Returns: (user, verification_message)
        """
        try:
            logger.info(f"📝 Starting signup for: {signup_data.email}")
            
            # Check if email already exists
            existing_query = select(User).where(User.email == signup_data.email)
            result = await db.execute(existing_query)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise ValueError("Email already registered")
            
            # Validate password strength
            is_valid, error_msg = validate_password_strength(signup_data.password)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Generate username
            username = self._generate_username(
                signup_data.email, 
                UserRole(signup_data.role),
                getattr(signup_data, 'company_name', None)
            )
            
            # Ensure username is unique
            counter = 1
            original_username = username
            while True:
                username_query = select(User).where(User.username == username)
                result = await db.execute(username_query)
                if not result.scalar_one_or_none():
                    break
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create user based on role
            user_data = {
                "email": signup_data.email,
                "username": username,
                "hashed_password": get_password_hash(signup_data.password),
                "role": signup_data.role,
                "is_active": True,
                "email_verified": False,
                "profile_completion_percentage": 30  # Basic signup complete
            }
            
            # Add role-specific fields
            if hasattr(signup_data, 'firstName') and signup_data.firstName:
                user_data["first_name"] = signup_data.firstName
            if hasattr(signup_data, 'lastName') and signup_data.lastName:
                user_data["last_name"] = signup_data.lastName
            
            # Create user
            user = User(**user_data)
            db.add(user)
            await db.flush()  # Get user ID without committing
            
            # Create verification token
            verification_token = await self._create_token(
                db, str(user.id), "email_verification",  # Use string value
                expires_hours=24
            )
            
            await db.commit()
            await db.refresh(user)
            
            # Send verification email
            display_name = user.display_name
            email_sent = email_service.send_verification_email(
                user.email, 
                display_name, 
                verification_token.token_value
            )
            
            if email_sent:
                message = "Account created successfully. Please check your email to verify your account."
            else:
                message = "Account created successfully. Verification email could not be sent."
            
            logger.info(f"✅ User registered successfully: {user.email}")
            return user, message
            
        except ValueError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Signup error: {str(e)}")
            raise ValueError("An error occurred during signup")
    
    async def login(self, db: AsyncSession, login_data: LoginRequest) -> Tuple[User, str, str]:
        """
        Authenticate user and return tokens (ASYNC)
        Supports login with email or username
        """
        try:
            logger.info(f"🔐 Login attempt for: {login_data.email}")
            
            # Find user by email or username
            user_query = select(User).where(
                and_(
                    or_(
                        User.email == login_data.email,
                        User.username == login_data.email
                    ),
                    User.is_active == True
                )
            )
            
            result = await db.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"❌ User not found: {login_data.email}")
                raise ValueError("Invalid credentials")
            
            # Verify password
            if not verify_password(login_data.password, user.hashed_password):
                logger.warning(f"❌ Invalid password for: {user.email}")
                raise ValueError("Invalid credentials")
            
            # Check if user is active
            if not user.is_active:
                raise ValueError("Account is deactivated. Please contact support.")
            
            # Check if email is verified
            if not user.email_verified:
                raise ValueError("Please verify your email before logging in.")
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            
            # Create token pair
            access_token, refresh_token = create_token_pair(
                user_id=str(user.id),
                user_role=user.role.value
            )
            
            # Store refresh token in database
            await self._create_token(
                db, str(user.id), "refresh",  # Use string value
                expires_hours=24*30,  # 30 days
                token_value=refresh_token
            )
            
            await db.commit()
            
            logger.info(f"✅ Login successful for: {user.email}")
            return user, access_token, refresh_token
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Login error: {str(e)}")
            await db.rollback()
            raise ValueError("An error occurred during login")
    
    async def verify_email(self, db: AsyncSession, verification_data: EmailVerificationRequest) -> str:
        """
        Verify user email address (ASYNC)
        """
        try:
            # Find verification token
            token_query = select(UserToken).where(
                and_(
                    UserToken.token_value == verification_data.token,
                    UserToken.token_type == "email_verification",  # Use string value
                    UserToken.is_used == False
                )
            )
            
            result = await db.execute(token_query)
            token = result.scalar_one_or_none()
            
            if not token or token.is_expired:
                raise ValueError("Invalid or expired verification token")
            
            # Get user and verify email
            user_query = select(User).where(User.id == token.user_id)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            # Update user and mark token as used
            user.email_verified = True
            user.profile_completion_percentage = max(user.profile_completion_percentage, 40)
            token.is_used = True
            
            await db.commit()
            
            logger.info(f"✅ Email verified for user: {user.email}")
            return "Email verified successfully"
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Email verification error: {str(e)}")
            await db.rollback()
            raise ValueError("An error occurred during email verification")
    
    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token (ASYNC)
        """
        try:
            # Verify refresh token
            payload = decode_refresh_token(refresh_token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise ValueError("Invalid refresh token")
            
            # Find refresh token
            token_query = select(UserToken).where(
                and_(
                    UserToken.token_value == refresh_token,
                    UserToken.token_type == "refresh",  # Use string value
                    UserToken.is_used == False
                )
            )
            
            result = await db.execute(token_query)
            token = result.scalar_one_or_none()
            
            if not token or token.is_expired:
                raise ValueError("Invalid or expired refresh token")
            
            # Get user
            user_query = select(User).where(
                and_(User.id == user_id, User.is_active == True)
            )
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            # Mark old refresh token as used
            token.is_used = True
            
            # Create new token pair
            new_access_token, new_refresh_token = create_token_pair(
                user_id=str(user.id),
                user_role=user.role.value
            )
            
            # Store new refresh token
            await self._create_token(
                db, str(user.id), "refresh",  # Use string value
                expires_hours=24*30,  # 30 days
                token_value=new_refresh_token
            )
            
            await db.commit()
            
            logger.info(f"✅ Token refreshed for user: {user.email}")
            return new_access_token, new_refresh_token
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Token refresh error: {str(e)}")
            await db.rollback()
            raise ValueError("An error occurred during token refresh")


# Create global instance
auth_service = AuthService()