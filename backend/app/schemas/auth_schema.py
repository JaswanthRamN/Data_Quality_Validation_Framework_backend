"""
Pydantic schemas for authentication endpoints.
Defines request and response models for login and token operations.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Schema for change password request."""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=8)
