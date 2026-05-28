"""
CRUD operations for Job model — includes upsert deduplication logic.
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.job import Job
from app.schemas.job_schema import JobCreate, JobUpdate, JobFilterParams

logger = logging.getLogger(__name__)


def upsert_job(db: Session, job_data: JobCreate) -> tuple[Job, bool]:
    """
    Insert a new job or skip if (source, external_id) already exists.
    Returns (job, created) where created=True means it was new.
    """
    existing = (
        db.query(Job)
        .filter(Job.source == job_data.source, Job.external_id == job_data.external_id)
        .first()
    )
    if existing:
        return existing, False

    try:
        job = Job(**job_data.model_dump())
        db.add(job)
        db.commit()
        db.refresh(job)
        return job, True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to insert job {job_data.title} @ {job_data.company}: {e}")
        raise


def upsert_jobs_batch(db: Session, jobs: List[JobCreate]) -> tuple[int, int]:
    """
    Bulk upsert a list of jobs.
    Returns (created_count, skipped_count).
    """
    created = skipped = 0
    for job_data in jobs:
        try:
            _, is_new = upsert_job(db, job_data)
            if is_new:
                created += 1
            else:
                skipped += 1
        except Exception as e:
            logger.warning(f"Skipping job due to error: {e}")
            skipped += 1
    return created, skipped


def get_job_by_id(db: Session, job_id: int) -> Optional[Job]:
    return db.query(Job).filter(Job.id == job_id, Job.is_excluded == False).first()


def get_jobs(db: Session, params: JobFilterParams) -> tuple[List[Job], int]:
    query = db.query(Job).filter(Job.is_excluded == False)

    if params.role_category:
        query = query.filter(Job.role_category == params.role_category)
    if params.is_remote is not None:
        query = query.filter(Job.is_remote == params.is_remote)
    if params.is_hybrid is not None:
        query = query.filter(Job.is_hybrid == params.is_hybrid)
    if params.min_score is not None:
        query = query.filter(Job.composite_score >= params.min_score)
    if params.sponsorship_likely is not None:
        query = query.filter(Job.sponsorship_likely == params.sponsorship_likely)
    if params.company:
        query = query.filter(Job.company.ilike(f"%{params.company}%"))

    total = query.count()
    jobs = (
        query.order_by(Job.composite_score.desc().nullslast(), Job.created_at.desc())
        .offset(params.skip)
        .limit(params.limit)
        .all()
    )
    return jobs, total


def get_top_jobs(db: Session, limit: int = 10) -> List[Job]:
    """Returns top N jobs by composite score with ATS analysis completed."""
    return (
        db.query(Job)
        .filter(Job.is_excluded == False, Job.composite_score.isnot(None))
        .order_by(Job.composite_score.desc())
        .limit(limit)
        .all()
    )


def get_unanalyzed_jobs(db: Session, limit: int = 50) -> List[Job]:
    """Returns jobs that have not yet been scored."""
    return (
        db.query(Job)
        .filter(Job.is_excluded == False, Job.ats_score.is_(None))
        .order_by(Job.created_at.desc())
        .limit(limit)
        .all()
    )


def update_job_analysis(db: Session, job_id: int, update: JobUpdate) -> Optional[Job]:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(job, field, value)
    try:
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update job {job_id}: {e}")
        raise


def exclude_job(db: Session, job_id: int) -> Optional[Job]:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    job.is_excluded = True
    db.commit()
    db.refresh(job)
    return job
