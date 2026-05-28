"""
Resume management API routes — upload master resume and retrieve tailored versions.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.crud.resume_crud import (
    create_or_replace_resume, get_active_resume, get_resume_version,
)
from app.schemas.resume_schema import ResumeCreate, ResumeResponse, ResumeVersionResponse
from app.services.job_discovery_service import USER_CORE_SKILLS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/", response_model=ResumeResponse, status_code=201)
def upload_resume(
    data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload or replace the master resume.
    Automatically extracts skill keywords from the text.
    """
    raw_lower = data.raw_text.lower()
    extracted_skills = [s for s in USER_CORE_SKILLS if s in raw_lower]
    return create_or_replace_resume(db, current_user.id, data, skills=extracted_skills)


@router.get("/", response_model=ResumeResponse)
def get_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's active master resume."""
    resume = get_active_resume(db, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No resume found. Upload one via POST /api/resume/",
        )
    return resume


@router.get("/versions/{job_id}", response_model=ResumeVersionResponse)
def get_tailored_version(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the AI-tailored resume version for a specific job."""
    resume = get_active_resume(db, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="No master resume found")

    version = get_resume_version(db, job_id=job_id, master_id=resume.id)
    if not version:
        raise HTTPException(
            status_code=404,
            detail="No tailored version for this job yet. Trigger ATS analysis first.",
        )
    return version
