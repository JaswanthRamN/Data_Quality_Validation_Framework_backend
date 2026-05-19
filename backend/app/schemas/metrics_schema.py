"""
Metrics API Schemas

Pydantic schemas for metrics API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class MetricResponse(BaseModel):
    """Schema for individual metric response."""
    id: int
    dataset_id: int
    column_name: str
    rule_name: str
    value: Optional[float] = None
    is_valid: bool
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class MetricDetailResponse(BaseModel):
    """Schema for detailed metric information."""
    name: str
    value: float = Field(..., ge=0, le=100)
    category: str
    details: Optional[Dict] = None


class QualityScoreResponse(BaseModel):
    """Schema for quality score response."""
    dataset_id: Optional[int] = None
    overall_score: float = Field(..., ge=0, le=100)
    metrics: List[MetricDetailResponse]
    timestamp: str
    issues: Optional[List[str]] = None
    message: Optional[str] = None


class MetricStatisticsResponse(BaseModel):
    """Schema for metric statistics response."""
    dataset_id: int
    total_checks: int
    passed_checks: int
    failed_checks: int
    pass_rate: float
    by_column: Dict[str, Dict]
    by_rule: Dict[str, Dict]
    timestamp: Optional[str] = None


class ColumnSpecification(BaseModel):
    """Schema for column-specific validation specifications."""
    column_name: str
    null_indicators: Optional[List] = None
    valid_values: Optional[List] = None
    validation_rule: Optional[str] = None
    expected_type: Optional[str] = None
    expected_format: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_types: Optional[List[str]] = None


class QualityAnalysisRequest(BaseModel):
    """Schema for on-demand quality analysis request."""
    data: Dict[str, List] = Field(
        ...,
        description="Dictionary of column_name -> list of values"
    )
    column_specs: Optional[Dict[str, Dict]] = Field(
        None,
        description="Optional column specifications for custom validation"
    )
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Optional custom weights for metrics (must sum to 1.0)"
    )


class MetricsFilter(BaseModel):
    """Schema for filtering metrics."""
    metric_type: Optional[str] = None
    column_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None


class DatasetMetricsSummary(BaseModel):
    """Schema for dataset metrics summary."""
    dataset_id: int
    dataset_name: str
    quality_score: float = Field(..., ge=0, le=100)
    total_checks: int
    passed_checks: int
    updated_at: Optional[str] = None


class MetricsSummaryResponse(BaseModel):
    """Schema for metrics summary response."""
    total_datasets: int
    datasets: List[DatasetMetricsSummary]
    timestamp: str
