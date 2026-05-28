"""
CRUD operations for MasterResume and ResumeVersion models.
"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.resume import MasterResume, ResumeVersion
from app.schemas.resume_schema import ResumeCreate

logger = logging.getLogger(__name__)


def create_or_replace_resume(
    db: Session, user_id: int, data: ResumeCreate, skills: Optional[List[str]] = None
) -> MasterResume:
    """Deactivate all previous resumes for the user and create a new active one."""
    db.query(MasterResume).filter(
        MasterResume.user_id == user_id, MasterResume.is_active == True
    ).update({"is_active": False})

    try:
        resume = MasterResume(
            user_id=user_id,
            raw_text=data.raw_text,
            skills=skills or [],
            is_active=True,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create resume for user {user_id}: {e}")
        raise


def get_active_resume(db: Session, user_id: int) -> Optional[MasterResume]:
    return (
        db.query(MasterResume)
        .filter(MasterResume.user_id == user_id, MasterResume.is_active == True)
        .first()
    )


def get_resume_version(db: Session, job_id: int, master_id: int) -> Optional[ResumeVersion]:
    return (
        db.query(ResumeVersion)
        .filter(ResumeVersion.job_id == job_id, ResumeVersion.master_id == master_id)
        .first()
    )


def create_resume_version(
    db: Session,
    master_id: int,
    job_id: int,
    tailored_bullets: Optional[List[str]],
    tailored_summary: Optional[str],
    ats_improvements: Optional[List[str]],
) -> ResumeVersion:
    # Overwrite existing version for same (master, job) pair
    existing = get_resume_version(db, job_id=job_id, master_id=master_id)
    if existing:
        existing.tailored_bullets = tailored_bullets
        existing.tailored_summary = tailored_summary
        existing.ats_improvements = ats_improvements
        db.commit()
        db.refresh(existing)
        return existing

    try:
        version = ResumeVersion(
            master_id=master_id,
            job_id=job_id,
            tailored_bullets=tailored_bullets,
            tailored_summary=tailored_summary,
            ats_improvements=ats_improvements,
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        return version
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create resume version for job {job_id}: {e}")
        raise
