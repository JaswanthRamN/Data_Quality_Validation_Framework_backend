"""
Application tracking API routes — manage job application lifecycle.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.job_application import ApplicationStatus
from app.crud.application_crud import (
    create_application, get_application_by_id, get_applications,
    update_application_status,
)
from app.crud.job_crud import get_job_by_id
from app.crud.resume_crud import get_active_resume, get_resume_version
from app.schemas.application_schema import (
    ApplicationCreate, ApplicationStatusUpdate,
    ApplicationResponse, ApplicationMaterialsResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationResponse, status_code=201)
def save_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a job to the application tracker (SAVED status)."""
    job = get_job_by_id(db, data.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return create_application(db, current_user.id, data)


@router.get("/", response_model=list[ApplicationResponse])
def list_applications(
    status: Optional[ApplicationStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all applications for the current user, optionally filtered by status."""
    return get_applications(db, current_user.id, status=status, skip=skip, limit=limit)


@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = get_application_by_id(db, app_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.patch("/{app_id}/status", response_model=ApplicationResponse)
def update_status(
    app_id: int,
    data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update application status (e.g. APPLIED, INTERVIEW, OFFER, REJECTED)."""
    app = update_application_status(db, app_id, current_user.id, data)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.get("/{app_id}/materials", response_model=ApplicationMaterialsResponse)
def get_materials(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get generated cover letter, outreach messages, and tailored resume for an application."""
    app = get_application_by_id(db, app_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    tailored_bullets = None
    tailored_summary = None
    ats_improvements = None

    if app.resume_version_id:
        resume = get_active_resume(db, current_user.id)
        if resume:
            version = get_resume_version(db, job_id=app.job_id, master_id=resume.id)
            if version:
                tailored_bullets = version.tailored_bullets
                tailored_summary = version.tailored_summary
                ats_improvements = version.ats_improvements

    from app.services.ats_analysis_service import ATSAnalysisService
    return ApplicationMaterialsResponse(
        job_id=app.job_id,
        cover_letter=app.cover_letter,
        outreach_message=app.outreach_message,
        linkedin_message=app.linkedin_message,
        tailored_bullets=tailored_bullets,
        tailored_summary=tailored_summary,
        ats_improvements=ats_improvements,
        ai_available=ATSAnalysisService().ai_available,
    )
