"""
Pydantic schemas for JobApplication — tracking application lifecycle.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.job_application import ApplicationStatus


class ApplicationCreate(BaseModel):
    job_id: int
    notes: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    applied_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationMaterialsResponse(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None
    outreach_message: Optional[str] = None
    linkedin_message: Optional[str] = None
    tailored_bullets: Optional[list] = None
    tailored_summary: Optional[str] = None
    ats_improvements: Optional[list] = None
    ai_available: bool = True


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    status: ApplicationStatus
    applied_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    cover_letter: Optional[str] = None
    outreach_message: Optional[str] = None
    linkedin_message: Optional[str] = None
    notes: Optional[str] = None
    resume_version_id: Optional[int] = None
    notion_page_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
