"""
Pydantic schemas for DailyReport — daily job search summary output.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.schemas.job_schema import JobSummary


class DailyReportResponse(BaseModel):
    id: int
    user_id: int
    report_date: date
    total_new_jobs: int
    top_jobs: Optional[List[JobSummary]] = None
    skill_gaps: Optional[List[str]] = None
    interview_topics: Optional[List[str]] = None
    report_html: Optional[str] = None
    notion_page_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DailyReportSummary(BaseModel):
    id: int
    report_date: date
    total_new_jobs: int
    top_score: Optional[float] = None
    notion_page_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
