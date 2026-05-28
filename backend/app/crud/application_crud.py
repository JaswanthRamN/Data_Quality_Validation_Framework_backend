"""
CRUD operations for JobApplication model.
"""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.job_application import JobApplication, ApplicationStatus
from app.schemas.application_schema import ApplicationCreate, ApplicationStatusUpdate

logger = logging.getLogger(__name__)


def create_application(
    db: Session, user_id: int, data: ApplicationCreate
) -> JobApplication:
    existing = (
        db.query(JobApplication)
        .filter(JobApplication.job_id == data.job_id, JobApplication.user_id == user_id)
        .first()
    )
    if existing:
        return existing

    try:
        app = JobApplication(
            job_id=data.job_id,
            user_id=user_id,
            status=ApplicationStatus.SAVED,
            notes=data.notes,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create application for job {data.job_id}: {e}")
        raise


def get_application_by_id(
    db: Session, app_id: int, user_id: int
) -> Optional[JobApplication]:
    return (
        db.query(JobApplication)
        .filter(JobApplication.id == app_id, JobApplication.user_id == user_id)
        .first()
    )


def get_applications(
    db: Session,
    user_id: int,
    status: Optional[ApplicationStatus] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[JobApplication]:
    query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
    if status:
        query = query.filter(JobApplication.status == status)
    return query.order_by(JobApplication.updated_at.desc()).offset(skip).limit(limit).all()


def update_application_status(
    db: Session, app_id: int, user_id: int, update: ApplicationStatusUpdate
) -> Optional[JobApplication]:
    app = get_application_by_id(db, app_id, user_id)
    if not app:
        return None

    app.status = update.status
    if update.applied_date:
        app.applied_date = update.applied_date
    if update.follow_up_date:
        app.follow_up_date = update.follow_up_date
    if update.notes:
        app.notes = update.notes

    try:
        db.commit()
        db.refresh(app)
        return app
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update application {app_id}: {e}")
        raise


def set_application_materials(
    db: Session,
    job_id: int,
    user_id: int,
    cover_letter: Optional[str],
    outreach_message: Optional[str],
    linkedin_message: Optional[str],
    resume_version_id: Optional[int] = None,
) -> Optional[JobApplication]:
    """Attach generated materials to an application, creating it if needed."""
    app = (
        db.query(JobApplication)
        .filter(JobApplication.job_id == job_id, JobApplication.user_id == user_id)
        .first()
    )
    if not app:
        app = JobApplication(job_id=job_id, user_id=user_id, status=ApplicationStatus.NEW)
        db.add(app)

    app.cover_letter = cover_letter
    app.outreach_message = outreach_message
    app.linkedin_message = linkedin_message
    if resume_version_id:
        app.resume_version_id = resume_version_id

    try:
        db.commit()
        db.refresh(app)
        return app
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to set materials for job {job_id}: {e}")
        raise


def set_notion_page_id(
    db: Session, app_id: int, notion_page_id: str
) -> None:
    app = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if app:
        app.notion_page_id = notion_page_id
        db.commit()
