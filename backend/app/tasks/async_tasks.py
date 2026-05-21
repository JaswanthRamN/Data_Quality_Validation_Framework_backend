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
