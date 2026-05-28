"""
Pydantic schemas for MasterResume and ResumeVersion.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ResumeCreate(BaseModel):
    raw_text: str


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    raw_text: str
    skills: Optional[List[str]] = None
    experience: Optional[list] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeVersionResponse(BaseModel):
    id: int
    master_id: int
    job_id: int
    tailored_bullets: Optional[List[str]] = None
    tailored_summary: Optional[str] = None
    ats_improvements: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
