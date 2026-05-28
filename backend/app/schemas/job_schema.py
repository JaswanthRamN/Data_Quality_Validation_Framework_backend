"""
Pydantic schemas for Job model — requests, responses, and filters.
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    source: str
    external_id: str
    title: str
    company: str
    location: Optional[str] = None
    is_remote: bool = False
    is_hybrid: bool = False
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    apply_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    role_category: Optional[str] = None
    sponsorship_likely: bool = False
    is_excluded: bool = False


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    composite_score: Optional[float] = None
    ats_score: Optional[float] = None
    skill_match_pct: Optional[float] = None
    missing_keywords: Optional[List[str]] = None
    raw_analysis: Optional[dict] = None
    sponsorship_likely: Optional[bool] = None
    is_excluded: Optional[bool] = None


class JobResponse(JobBase):
    id: int
    composite_score: Optional[float] = None
    ats_score: Optional[float] = None
    skill_match_pct: Optional[float] = None
    missing_keywords: Optional[List[str]] = None
    raw_analysis: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobSummary(BaseModel):
    """Lightweight summary for list views and daily reports."""
    id: int
    title: str
    company: str
    location: Optional[str] = None
    is_remote: bool
    is_hybrid: bool
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    composite_score: Optional[float] = None
    ats_score: Optional[float] = None
    skill_match_pct: Optional[float] = None
    sponsorship_likely: bool
    apply_url: Optional[str] = None
    role_category: Optional[str] = None
    missing_keywords: Optional[List[str]] = None
    why_it_fits: Optional[str] = None
    priority_rank: Optional[int] = None

    model_config = {"from_attributes": True}


class JobFilterParams(BaseModel):
    role_category: Optional[str] = None
    is_remote: Optional[bool] = None
    is_hybrid: Optional[bool] = None
    min_score: Optional[float] = None
    sponsorship_likely: Optional[bool] = None
    company: Optional[str] = None
    skip: int = 0
    limit: int = 50


class JobSearchResult(BaseModel):
    total: int
    jobs: List[JobSummary]
    ai_available: bool = True
