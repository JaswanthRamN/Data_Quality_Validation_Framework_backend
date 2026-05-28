"""
Job search API routes — discover, filter, rank, and manage job listings.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.models.user import User
from app.crud.job_crud import (
    get_job_by_id, get_jobs, get_top_jobs, get_unanalyzed_jobs,
    upsert_jobs_batch, exclude_job,
)
from app.schemas.job_schema import (
    JobResponse, JobSummary, JobFilterParams, JobSearchResult,
)
from app.services.job_discovery_service import JobDiscoveryService
from app.services.ats_analysis_service import ATSAnalysisService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])

_discovery_service = JobDiscoveryService()
_ats_service = ATSAnalysisService()


@router.get("/top", response_model=list[JobSummary], summary="Top 10 jobs by score")
def get_top_scored_jobs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the top N jobs ranked by composite score."""
    jobs = get_top_jobs(db, limit=limit)
    summaries = []
    for rank, job in enumerate(jobs, start=1):
        analysis = job.raw_analysis or {}
        summaries.append(
            JobSummary(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                is_remote=job.is_remote,
                is_hybrid=job.is_hybrid,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                composite_score=job.composite_score,
                ats_score=job.ats_score,
                skill_match_pct=job.skill_match_pct,
                sponsorship_likely=job.sponsorship_likely,
                apply_url=job.apply_url,
                role_category=job.role_category,
                missing_keywords=job.missing_keywords,
                why_it_fits=analysis.get("why_it_fits", ""),
                priority_rank=rank,
            )
        )
    return summaries


@router.get("/", response_model=JobSearchResult, summary="List and filter jobs")
def list_jobs(
    role_category: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    is_hybrid: Optional[bool] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    sponsorship_likely: Optional[bool] = Query(None),
    company: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List jobs with optional filters. Results ordered by composite score."""
    params = JobFilterParams(
        role_category=role_category,
        is_remote=is_remote,
        is_hybrid=is_hybrid,
        min_score=min_score,
        sponsorship_likely=sponsorship_likely,
        company=company,
        skip=skip,
        limit=limit,
    )
    jobs, total = get_jobs(db, params)
    summaries = [
        JobSummary(
            id=j.id, title=j.title, company=j.company, location=j.location,
            is_remote=j.is_remote, is_hybrid=j.is_hybrid,
            salary_min=j.salary_min, salary_max=j.salary_max,
            composite_score=j.composite_score, ats_score=j.ats_score,
            skill_match_pct=j.skill_match_pct, sponsorship_likely=j.sponsorship_likely,
            apply_url=j.apply_url, role_category=j.role_category,
            missing_keywords=j.missing_keywords,
        )
        for j in jobs
    ]
    return JobSearchResult(total=total, jobs=summaries, ai_available=_ats_service.ai_available)


@router.get("/{job_id}", response_model=JobResponse, summary="Get full job detail")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/trigger-scrape", summary="Manually trigger job discovery (admin)")
def trigger_scrape(
    role: str = Query(..., description="Job role to search"),
    location: str = Query(..., description="Location to search (or 'remote')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """
    Triggers an Indeed job search for the given role+location.
    The caller must provide the raw Indeed MCP results via the
    POST /jobs/ingest endpoint after calling the MCP tool.
    Returns the search query parameters to use with the Indeed MCP tool.
    """
    return {
        "message": "Use the Indeed MCP tool with these parameters, then POST to /jobs/ingest",
        "mcp_tool": "mcp__19b1b25b-39e3-44bd-989c-b2925f1d9690__search_jobs",
        "params": {
            "search": role,
            "location": location,
            "country_code": "US",
            "job_type": "fulltime",
        },
        "next_step": "POST /api/jobs/ingest with {raw_markdown, role, location}",
    }


@router.post("/ingest", summary="Ingest Indeed MCP search results")
def ingest_jobs(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts raw Indeed MCP markdown output and processes it into the DB.
    Payload: {raw_markdown: str, role: str, location: str}
    """
    raw_markdown = payload.get("raw_markdown", "")
    role = payload.get("role", "")
    location = payload.get("location", "")

    if not raw_markdown or not role:
        raise HTTPException(status_code=400, detail="raw_markdown and role are required")

    jobs = _discovery_service.process_search_results(raw_markdown, role, location)
    jobs = _discovery_service.deduplicate(jobs)
    created, skipped = upsert_jobs_batch(db, jobs)

    return {
        "status": "success",
        "role": role,
        "location": location,
        "jobs_found": len(jobs),
        "created": created,
        "skipped": skipped,
    }


@router.post("/{job_id}/exclude", summary="Flag a job as excluded")
def mark_excluded(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = exclude_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "excluded", "job_id": job_id}


@router.post("/trigger-analysis", summary="Queue ATS analysis for unscored jobs (admin)")
def trigger_ats_analysis(
    current_user: User = Depends(get_admin_user),
):
    """Submits the analyze_new_jobs_batch Celery task."""
    from app.tasks.async_tasks import analyze_new_jobs_batch
    task = analyze_new_jobs_batch.apply_async(kwargs={"user_id": current_user.id})
    return {"task_id": task.id, "status": "queued"}
