"""
Pydantic schemas for dataset endpoints.
Defines request and response models for dataset operations.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DatasetCreate(BaseModel):
    """Schema for dataset creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    file_path: Optional[str] = Field(None, max_length=500)
    record_count: int = Field(0, ge=0)
    column_count: int = Field(0, ge=0)


class DatasetUpdate(BaseModel):
    """Schema for dataset update request."""
    description: Optional[str] = Field(None, max_length=500)
    record_count: Optional[int] = Field(None, ge=0)
    column_count: Optional[int] = Field(None, ge=0)
    is_active: Optional[int] = Field(None)


class DatasetResponse(BaseModel):
    """Schema for dataset response."""
    id: int
    name: str
    source_type: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    record_count: int
    column_count: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_active: int

    class Config:
        from_attributes = True
