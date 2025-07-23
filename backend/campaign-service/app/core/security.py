# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Use auto_error=False to handle missing tokens gracefully
security = HTTPBearer(auto_error=False)


# app/core/security.py - Add this function
def verify_session_token(token: str) -> dict:
    """Verify session token by calling user service"""
    import requests
    
    try:
        # Call user service to validate token
        response = requests.get(
            "http://localhost:8000/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "id": user_data.get("id"),
                "role": user_data.get("role")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token"
            )
    except Exception as e:
        logger.error(f"Session token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify session token"
        )

# Update the verify_token function
def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """Verify JWT or session token and return user data"""
    
    if credentials is None:
        logger.error("No authorization credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        logger.info(f"Token received: {token[:50]}..." if len(token) > 50 else f"Token received: {token}")
        logger.info(f"Token length: {len(token)}")
        
        # Check if it's a session token (starts with 'token_')
        if token.startswith('token_'):
            logger.info("Detected session token format, verifying with user service")
            return verify_session_token(token)
        
        # Otherwise, try JWT verification
        token_parts = token.split('.')
        if len(token_parts) != 3:
            logger.error(f"Invalid token format. Expected 3 parts, got {len(token_parts)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        logger.info(f"Token decoded successfully - User: {user_id}, Role: {role}")
        
        if user_id is None or role is None:
            logger.error(f"Invalid token payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"id": user_id, "role": role}
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """Get current user from JWT token"""
    return verify_token(credentials)


def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Get current user from JWT token, but don't fail if not authenticated"""
    if credentials is None:
        return None
    try:
        return verify_token(credentials)
    except HTTPException:
        return None


def require_role(allowed_roles: List[str]):
    """Create a dependency that requires specific roles"""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            logger.warning(f"User {current_user['id']} with role {current_user['role']} attempted to access resource requiring roles: {allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker


# Helper functions for common role requirements
def require_agency(current_user: dict = Depends(get_current_user)) -> dict:
    """Require agency role"""
    if current_user["role"] not in ["agency", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agency access required"
        )
    return current_user


def require_brand(current_user: dict = Depends(get_current_user)) -> dict:
    """Require brand role"""
    if current_user["role"] not in ["brand", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brand access required"
        )
    return current_user


def require_creator(current_user: dict = Depends(get_current_user)) -> dict:
    """Require creator role"""
    if current_user["role"] not in ["creator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creator access required"
        )
    return current_user


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Utility function to create JWT tokens (useful for testing)
def create_access_token(user_id: str, role: str, additional_claims: dict = None) -> str:
    """Create a JWT access token"""
    from datetime import datetime, timedelta
    
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    # Add any additional claims
    if additional_claims:
        payload.update(additional_claims)
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    logger.info(f"Created token for user {user_id} with role {role}")
    return token


# Function to decode token without verification (for debugging)
def decode_token_unsafe(token: str) -> dict:
    """Decode JWT token without verification - FOR DEBUGGING ONLY"""
    try:
        # Decode without verification
        unverified = jwt.decode(token, options={"verify_signature": False})
        logger.warning(f"Decoded token (unverified): {unverified}")
        return unverified
    except Exception as e:
        logger.error(f"Failed to decode token even without verification: {e}")
        return {}