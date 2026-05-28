"""
Asynchronous task management for background validation execution.
Uses Celery for distributed task processing with database persistence.
"""

from celery import Celery, Task
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import json

from app.config import settings
from app.database import SessionLocal, engine
from app.models.base import Base

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


class DatabaseTask(Task):
    """Base task class with database session management."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    
    def __call__(self, *args, **kwargs):
        """Execute task with database session."""
        db = SessionLocal()
        try:
            kwargs["db"] = db
            return self.run(*args, **kwargs)
        finally:
            db.close()


@celery_app.task(base=DatabaseTask, bind=True, name="execute_background_validation")
def execute_background_validation(
    self,
    dataset_id: int,
    validation_config: Dict[str, Any],
    rules_path: Optional[str] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Execute validation on a dataset in the background.
    
    Args:
        dataset_id: ID of the dataset to validate
        validation_config: Configuration for validation rules
        rules_path: Optional path to validation rules file
        db: Database session (injected by DatabaseTask)
    
    Returns:
        Dictionary containing validation results and metadata
    
    Raises:
        Exception: Validation execution errors
    """
    try:
        logger.info(f"Starting background validation for dataset {dataset_id}")
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Initializing validation"},
        )
        
        # Import validation service here to avoid circular imports
        from app.services.validation_service import ValidationService
        from app.crud.dataset_crud import DatasetCRUD
        
        # Get dataset
        dataset_crud = DatasetCRUD(db)
        dataset = dataset_crud.get_by_id(dataset_id)
        
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found")
            raise ValueError(f"Dataset {dataset_id} not found")
        
        logger.info(f"Found dataset: {dataset.name}")
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Loading validation rules"},
        )
        
        # Initialize validation service
        validation_service = ValidationService(db)
        
        # Execute validation
        logger.info(f"Executing validation for dataset {dataset_id}")
        self.update_state(
            state="PROGRESS",
            meta={"current": 50, "total": 100, "status": "Running validation checks"},
        )
        
        validation_results = validation_service.validate_dataset(
            dataset_id=dataset_id,
            config=validation_config,
            rules_path=rules_path,
        )
        
        logger.info(f"Validation completed for dataset {dataset_id}")
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Persisting results"},
        )
        
        # Prepare result
        result = {
            "dataset_id": dataset_id,
            "dataset_name": dataset.name,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "results": validation_results,
            "total_checks": len(validation_results.get("checks", [])),
            "failed_checks": sum(
                1 for check in validation_results.get("checks", [])
                if not check.get("passed", False)
            ),
        }
        
        logger.info(f"Background validation task completed for dataset {dataset_id}")
        return result
        
    except Exception as e:
        logger.error(
            f"Background validation failed for dataset {dataset_id}: {str(e)}",
            exc_info=True
        )
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "status": "Validation failed"},
        )
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="execute_batch_validation")
def execute_batch_validation(
    self,
    dataset_ids: list,
    validation_config: Dict[str, Any],
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Execute validation on multiple datasets in the background.
    
    Args:
        dataset_ids: List of dataset IDs to validate
        validation_config: Configuration for validation rules
        db: Database session (injected by DatabaseTask)
    
    Returns:
        Dictionary containing batch validation results
    """
    try:
        logger.info(f"Starting batch validation for {len(dataset_ids)} datasets")
        total_datasets = len(dataset_ids)
        completed = 0
        results = {}
        errors = {}
        
        for dataset_id in dataset_ids:
            try:
                logger.info(f"Processing dataset {dataset_id} ({completed + 1}/{total_datasets})")
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": completed,
                        "total": total_datasets,
                        "status": f"Processing dataset {dataset_id}",
                    },
                )
                
                result = execute_background_validation.apply_async(
                    args=[dataset_id, validation_config],
                    wait=True,
                    timeout=1800,  # 30 minutes timeout
                )
                results[dataset_id] = result.get()
                completed += 1
                
            except Exception as e:
                logger.error(f"Error validating dataset {dataset_id}: {str(e)}")
                errors[dataset_id] = str(e)
                completed += 1
        
        batch_result = {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "total_datasets": total_datasets,
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }
        
        logger.info(f"Batch validation completed: {len(results)} successful, {len(errors)} failed")
        return batch_result
        
    except Exception as e:
        logger.error(f"Batch validation failed: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)},
        )
        raise


@celery_app.task(name="cleanup_old_validation_results")
def cleanup_old_validation_results(days_to_keep: int = 30) -> Dict[str, Any]:
    """
    Clean up old validation results to manage database size.
    
    Args:
        days_to_keep: Number of days of results to retain
    
    Returns:
        Dictionary containing cleanup statistics
    """
    try:
        db = SessionLocal()
        logger.info(f"Starting cleanup of validation results older than {days_to_keep} days")
        
        from app.crud.validation_crud import ValidationCRUD
        from datetime import timedelta
        
        validation_crud = ValidationCRUD(db)
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = validation_crud.delete_before_date(cutoff_date)
        
        result = {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "records_deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }
        
        logger.info(f"Cleanup completed: {deleted_count} records deleted")
        return result
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a background task.
    
    Args:
        task_id: Celery task ID
    
    Returns:
        Dictionary containing task status and result
    """
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        status_info = {
            "task_id": task_id,
            "status": result.status,
            "current": 0,
            "total": 100,
            "result": None,
            "error": None,
        }
        
        if result.state == "PENDING":
            status_info["status"] = "pending"
        elif result.state == "PROGRESS":
            status_info.update(result.info)
        elif result.state == "SUCCESS":
            status_info["result"] = result.result
        elif result.state == "FAILURE":
            status_info["error"] = str(result.info)
        elif result.state == "RETRY":
            status_info["status"] = "retrying"
        elif result.state == "REVOKED":
            status_info["status"] = "revoked"
        
        return status_info
        
    except Exception as e:
        logger.error(f"Error retrieving task status: {str(e)}")
        return {
            "task_id": task_id,
            "status": "unknown",
            "error": str(e),
        }


def revoke_task(task_id: str, terminate: bool = False) -> Dict[str, Any]:
    """
    Revoke (cancel) a background task.
    
    Args:
        task_id: Celery task ID
        terminate: Whether to forcefully terminate the task
    
    Returns:
        Dictionary containing revocation status
    """
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        logger.info(f"Task {task_id} revoked (terminate={terminate})")
        
        return {
            "task_id": task_id,
            "status": "revoked",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error revoking task {task_id}: {str(e)}")
        return {
            "task_id": task_id,
            "status": "error",
            "error": str(e),
        }


def submit_validation_task(
    dataset_id: int,
    validation_config: Dict[str, Any],
    rules_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Submit a background validation task.
    
    Args:
        dataset_id: ID of dataset to validate
        validation_config: Validation configuration
        rules_path: Optional path to validation rules
    
    Returns:
        Dictionary with task_id and submission status
    """
    try:
        task = execute_background_validation.apply_async(
            args=[dataset_id, validation_config, rules_path],
            countdown=0,  # Execute immediately
        )
        
        logger.info(f"Validation task submitted: {task.id} for dataset {dataset_id}")
        
        return {
            "task_id": task.id,
            "dataset_id": dataset_id,
            "status": "submitted",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error submitting validation task: {str(e)}")
        raise


def submit_batch_validation_task(
    dataset_ids: list,
    validation_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Submit a batch validation task for multiple datasets.

    Args:
        dataset_ids: List of dataset IDs to validate
        validation_config: Validation configuration

    Returns:
        Dictionary with task_id and submission status
    """
    try:
        task = execute_batch_validation.apply_async(
            args=[dataset_ids, validation_config],
            countdown=0,
        )

        logger.info(
            f"Batch validation task submitted: {task.id} for {len(dataset_ids)} datasets"
        )

        return {
            "task_id": task.id,
            "dataset_ids": dataset_ids,
            "status": "submitted",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error submitting batch validation task: {str(e)}")
        raise


# ── Job Search Automation Tasks ───────────────────────────────────────────────

@celery_app.task(name="process_job_search_results")
def process_job_search_results(
    raw_markdown: str,
    role: str,
    location: str,
) -> Dict[str, Any]:
    """
    Process raw Indeed MCP search results and upsert jobs to the database.
    Called from the job routes after the MCP tool returns results.

    Args:
        raw_markdown: Raw markdown text from Indeed MCP search_jobs tool
        role: Job role that was searched
        location: Location that was searched

    Returns:
        Dict with created/skipped counts
    """
    db = SessionLocal()
    try:
        from app.services.job_discovery_service import JobDiscoveryService
        from app.crud.job_crud import upsert_jobs_batch

        service = JobDiscoveryService()
        jobs = service.process_search_results(raw_markdown, role, location)
        created, skipped = upsert_jobs_batch(db, jobs)

        logger.info(
            f"Job discovery [{role} / {location}]: {created} new, {skipped} skipped"
        )
        return {
            "status": "completed",
            "role": role,
            "location": location,
            "created": created,
            "skipped": skipped,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Job processing failed [{role}/{location}]: {e}", exc_info=True)
        raise
    finally:
        db.close()


@celery_app.task(base=DatabaseTask, bind=True, name="analyze_new_jobs_batch")
def analyze_new_jobs_batch(
    self,
    user_id: int = 1,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Run ATS analysis on unscored jobs using the master resume from config.
    Scores each job and stores results.

    Args:
        user_id: User whose resume to use for analysis
        db: Database session (injected by DatabaseTask)

    Returns:
        Dict with analysis counts and summary
    """
    try:
        from app.services.ats_analysis_service import ATSAnalysisService
        from app.services.job_scoring_service import JobScoringService
        from app.crud.job_crud import get_unanalyzed_jobs, update_job_analysis
        from app.crud.resume_crud import get_active_resume, create_resume_version
        from app.schemas.job_schema import JobUpdate

        self.update_state(state="PROGRESS", meta={"status": "Loading resume"})

        # Prefer DB resume; fall back to config
        resume = get_active_resume(db, user_id)
        resume_text = (resume.raw_text if resume else None) or settings.MASTER_RESUME_TEXT
        if not resume_text:
            logger.warning("No master resume found — skipping ATS analysis")
            return {"status": "skipped", "reason": "no_resume"}

        jobs = get_unanalyzed_jobs(db, limit=50)
        if not jobs:
            logger.info("No unanalyzed jobs found")
            return {"status": "completed", "analyzed": 0}

        self.update_state(
            state="PROGRESS",
            meta={"status": f"Analyzing {len(jobs)} jobs", "total": len(jobs)},
        )

        ats_service = ATSAnalysisService()
        scoring_service = JobScoringService()

        job_descriptions = [(j.id, j.description or j.title) for j in jobs]
        analyses = ats_service.batch_analyze(resume_text, job_descriptions)

        analyzed = 0
        for job in jobs:
            analysis = analyses.get(job.id, {})
            if "error" in analysis:
                continue

            composite = scoring_service.score_job(job, analysis)
            update = JobUpdate(
                ats_score=analysis.get("ats_score"),
                skill_match_pct=analysis.get("skill_match_pct"),
                missing_keywords=analysis.get("missing_keywords"),
                composite_score=composite,
                raw_analysis=analysis,
            )
            update_job_analysis(db, job.id, update)

            # Persist tailored resume version if bullets were generated
            if resume and analysis.get("tailored_bullets"):
                create_resume_version(
                    db,
                    master_id=resume.id,
                    job_id=job.id,
                    tailored_bullets=analysis.get("tailored_bullets"),
                    tailored_summary=analysis.get("tailored_summary"),
                    ats_improvements=analysis.get("missing_keywords"),
                )
            analyzed += 1

        logger.info(f"ATS analysis complete: {analyzed}/{len(jobs)} jobs scored")
        return {
            "status": "completed",
            "analyzed": analyzed,
            "ai_available": ats_service.ai_available,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"ATS batch analysis failed: {e}", exc_info=True)
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task(name="generate_daily_job_report")
def generate_daily_job_report(user_id: int = 1) -> Dict[str, Any]:
    """
    Build and persist the daily job search summary report.
    Runs after analyze_new_jobs_batch completes.

    Args:
        user_id: User to generate the report for

    Returns:
        Dict with report metadata
    """
    db = SessionLocal()
    try:
        from app.services.report_generation_service import ReportGenerationService

        service = ReportGenerationService()
        report = service.generate(db, user_id)

        logger.info(
            f"Daily report generated: {report.total_new_jobs} jobs, "
            f"report_id={report.id}, date={report.report_date}"
        )
        return {
            "status": "completed",
            "report_id": report.id,
            "report_date": str(report.report_date),
            "total_jobs": report.total_new_jobs,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}", exc_info=True)
        raise
    finally:
        db.close()


# ── Celery Beat Schedule ──────────────────────────────────────────────────────

# Add job search automation tasks to the beat schedule.
# These are chained: analyze runs 30 min after scrape, report runs 30 min after analyze.
# Scraping itself is triggered via API (POST /api/jobs/trigger-scrape) since the
# Indeed MCP tool is only callable from the Claude agent context.
celery_app.conf.beat_schedule = {
    "analyze-new-jobs-daily": {
        "task": "analyze_new_jobs_batch",
        "schedule": 3600 * 24,  # once per day (after manual/API scrape trigger)
        "kwargs": {"user_id": 1},
    },
    "generate-daily-report": {
        "task": "generate_daily_job_report",
        "schedule": 3600 * 24,  # once per day
        "kwargs": {"user_id": 1},
    },
    "cleanup-old-validations": {
        "task": "cleanup_old_validation_results",
        "schedule": 3600 * 24 * 7,  # weekly
    },
}
