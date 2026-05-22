"""
Authentication API routes.
Handles user registration, login, token refresh, and password management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.auth_schema import (
    UserLoginRequest, 
    UserRegisterRequest, 
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    ChangePasswordRequest
)
from app.models.user import User
from app.crud import user_crud
from app.core.security import TokenManager, PasswordManager, TOKEN_TYPE_REFRESH
from app.config import settings
from app.utils.logger import logger
from jose import JWTError

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
    """
    # Check if user already exists
    if user_crud.get_user_by_username(db, user_data.username):
        logger.warning(f"Registration attempt with existing username: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if user_crud.get_user_by_email(db, user_data.email):
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        db_user = user_crud.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        logger.info(f"New user registered: {user_data.username}")
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access and refresh tokens.
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        Access token, refresh token, and expiration info
    """
    # Get user
    user = user_crud.get_user_by_username(db, login_data.username)
    if not user:
        logger.warning(f"Login attempt with non-existent username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not PasswordManager.verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Login attempt with wrong password for user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        logger.warning(f"Login attempt by inactive user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user_crud.update_last_login(db, user.id)
    
    # Create tokens
    access_token = TokenManager.create_access_token(
        data={"sub": user.username}
    )
    refresh_token = TokenManager.create_refresh_token(
        data={"sub": user.username}
    )
    
    logger.info(f"User logged in successfully: {login_data.username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        token_data: Refresh token
        db: Database session
        
    Returns:
        New access token
    """
    try:
        payload = TokenManager.verify_token(token_data.refresh_token, TOKEN_TYPE_REFRESH)
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user exists and is active
        user = user_crud.get_user_by_username(db, username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        new_access_token = TokenManager.create_access_token(
            data={"sub": user.username}
        )
        
        logger.info(f"Token refreshed for user: {username}")
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except JWTError as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Args:
        password_data: Old and new passwords
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # Verify old password
    if not PasswordManager.verify_password(password_data.old_password, current_user.hashed_password):
        logger.warning(f"Password change attempt with wrong old password for user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid old password"
        )
    
    # Update password
    if user_crud.update_password(db, current_user.id, password_data.new_password):
        logger.info(f"Password changed for user: {current_user.username}")
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
