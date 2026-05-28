"""
Pydantic schemas for validation endpoints.
Defines request and response models for validation operations.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ValidationCreate(BaseModel):
    """Schema for validation result creation request."""
    dataset_id: int
    validation_type: str = Field(..., min_length=1, max_length=50)
    status: str = Field(..., pattern="^(PASSED|FAILED|WARNING)$")
    passed_count: int = Field(0, ge=0)
    failed_count: int = Field(0, ge=0)
    pass_rate: float = Field(0.0, ge=0.0, le=100.0)
    error_message: Optional[str] = Field(None)
    errors: Optional[dict] = Field(None)
    validation_details: Optional[dict] = Field(None)
    execution_time_ms: float = Field(0.0, ge=0.0)


class ValidationUpdate(BaseModel):
    """Schema for validation result update request."""
    status: Optional[str] = Field(None, pattern="^(PASSED|FAILED|WARNING)$")
    passed_count: Optional[int] = Field(None, ge=0)
    failed_count: Optional[int] = Field(None, ge=0)
    pass_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    error_message: Optional[str] = Field(None)
    errors: Optional[dict] = Field(None)
    validation_details: Optional[dict] = Field(None)


class ValidationResponse(BaseModel):
    """Schema for validation result response."""
    id: int
    dataset_id: int
    validation_type: str
    status: str
    passed_count: int
    failed_count: int
    pass_rate: float
    error_message: Optional[str] = None
    errors: Optional[dict] = None
    validation_details: Optional[dict] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    execution_time_ms: float

    class Config:
        from_attributes = True


class ValidationSummary(BaseModel):
    """Schema for validation summary response."""
    total_validations: int
    passed: int
    failed: int
    warning: int
    average_pass_rate: float
    latest_validation: Optional[datetime] = None
