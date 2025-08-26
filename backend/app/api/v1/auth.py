"""
Authentication API routes for LearnAid.
Handles user login, registration, token refresh, and password management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token
)
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import (
    Token, LoginRequest, RefreshTokenRequest, 
    UserResponse, ChangePasswordRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    Accepts username/email and password, returns JWT tokens.
    """
    try:
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == form_data.username) | 
            (User.email == form_data.username)
        ).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt by inactive user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        logger.info(f"Successful login for user: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current user information from token.
    """
    try:
        # Verify token and get payload
        payload = verify_token(current_user)
        user_id = payload.get("sub")
        
        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not get user information"
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    """
    try:
        # Verify token and get user
        payload = verify_token(current_user)
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(request.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = get_password_hash(request.new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not change password"
        )


@router.post("/logout")
async def logout():
    """
    User logout endpoint.
    Since JWT is stateless, this just returns success.
    In production, you might want to maintain a blacklist.
    """
    return {"message": "Successfully logged out"}


# Password reset endpoints (placeholder for future implementation)
@router.post("/forgot-password")
async def forgot_password():
    """
    Request password reset (to be implemented with email service).
    """
    return {"message": "Password reset functionality will be implemented in future"}


@router.post("/reset-password")
async def reset_password():
    """
    Reset password with token (to be implemented with email service).
    """
    return {"message": "Password reset functionality will be implemented in future"}


# User registration endpoint (admin only initially)
@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: dict,  # This will be replaced with proper schema later
    db: Session = Depends(get_db)
):
    """
    Register a new user (admin functionality).
    This is a placeholder - proper implementation will be in admin routes.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User registration is handled through admin panel"
    )
