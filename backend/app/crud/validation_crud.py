"""
CRUD operations for ValidationResult model.
Handles validation result creation, retrieval, update, and deletion.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.validation_result import ValidationResult
from app.utils.logger import logger
from datetime import datetime


def create_validation_result(
    db: Session,
    dataset_id: int,
    validation_type: str,
    status: str,
    created_by: int,
    passed_count: int = 0,
    failed_count: int = 0,
    pass_rate: float = 0.0,
    error_message: str = None,
    errors: dict = None,
    validation_details: dict = None,
    execution_time_ms: float = 0.0
) -> ValidationResult:
    """
    Create a new validation result.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        validation_type: Type of validation performed
        status: Validation status (PASSED, FAILED, WARNING)
        created_by: User ID of creator
        passed_count: Number of passed validations
        failed_count: Number of failed validations
        pass_rate: Pass rate percentage
        error_message: Main error message
        errors: Detailed errors in JSON format
        validation_details: Validation configuration and results
        execution_time_ms: Execution time in milliseconds
        
    Returns:
        Created ValidationResult object
    """
    try:
        db_validation = ValidationResult(
            dataset_id=dataset_id,
            validation_type=validation_type,
            status=status,
            created_by=created_by,
            passed_count=passed_count,
            failed_count=failed_count,
            pass_rate=pass_rate,
            error_message=error_message,
            errors=errors,
            validation_details=validation_details,
            execution_time_ms=execution_time_ms
        )
        db.add(db_validation)
        db.commit()
        db.refresh(db_validation)
        logger.info(f"Validation result created: {validation_type} for dataset {dataset_id}")
        return db_validation
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating validation result: {str(e)}")
        raise


def get_validation_result_by_id(
    db: Session,
    validation_id: int
) -> ValidationResult | None:
    """
    Get validation result by ID.
    
    Args:
        db: Database session
        validation_id: Validation result ID
        
    Returns:
        ValidationResult object or None
    """
    return db.query(ValidationResult).filter(
        ValidationResult.id == validation_id
    ).first()


def get_dataset_validations(
    db: Session,
    dataset_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[ValidationResult]:
    """
    Get all validation results for a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of ValidationResult objects
    """
    return db.query(ValidationResult).filter(
        ValidationResult.dataset_id == dataset_id
    ).offset(skip).limit(limit).all()


def get_user_validations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[ValidationResult]:
    """
    Get all validation results created by a user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of ValidationResult objects
    """
    return db.query(ValidationResult).filter(
        ValidationResult.created_by == user_id
    ).offset(skip).limit(limit).all()


def get_latest_dataset_validation(
    db: Session,
    dataset_id: int,
    validation_type: str = None
) -> ValidationResult | None:
    """
    Get the latest validation result for a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        validation_type: Optional specific validation type
        
    Returns:
        Latest ValidationResult object or None
    """
    query = db.query(ValidationResult).filter(
        ValidationResult.dataset_id == dataset_id
    )
    
    if validation_type:
        query = query.filter(ValidationResult.validation_type == validation_type)
    
    return query.order_by(ValidationResult.created_at.desc()).first()


def get_validation_history(
    db: Session,
    dataset_id: int,
    limit: int = 10
) -> list[ValidationResult]:
    """
    Get validation history for a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        limit: Maximum records to return
        
    Returns:
        List of ValidationResult objects in reverse chronological order
    """
    return db.query(ValidationResult).filter(
        ValidationResult.dataset_id == dataset_id
    ).order_by(ValidationResult.created_at.desc()).limit(limit).all()


def update_validation_result(
    db: Session,
    validation_id: int,
    **kwargs
) -> ValidationResult | None:
    """
    Update validation result fields.
    
    Args:
        db: Database session
        validation_id: Validation result ID
        **kwargs: Fields to update
        
    Returns:
        Updated ValidationResult object or None
    """
    validation = get_validation_result_by_id(db, validation_id)
    if not validation:
        return None
    
    allowed_fields = {
        "status", "passed_count", "failed_count", "pass_rate",
        "error_message", "errors", "validation_details", "execution_time_ms"
    }
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            setattr(validation, key, value)
    
    try:
        db.commit()
        db.refresh(validation)
        logger.info(f"Validation result updated: {validation_id}")
        return validation
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating validation result: {str(e)}")
        raise


def delete_validation_result(db: Session, validation_id: int) -> bool:
    """
    Delete a validation result.
    
    Args:
        db: Database session
        validation_id: Validation result ID
        
    Returns:
        True if successful
    """
    validation = get_validation_result_by_id(db, validation_id)
    if not validation:
        return False
    
    try:
        db.delete(validation)
        db.commit()
        logger.info(f"Validation result deleted: {validation_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting validation result: {str(e)}")
        raise


def get_dataset_validation_summary(
    db: Session,
    dataset_id: int
) -> dict:
    """
    Get validation summary statistics for a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        Dictionary with validation statistics
    """
    try:
        validations = db.query(ValidationResult).filter(
            ValidationResult.dataset_id == dataset_id
        ).all()
        
        if not validations:
            return {
                "total_validations": 0,
                "passed": 0,
                "failed": 0,
                "warning": 0,
                "average_pass_rate": 0.0
            }
        
        stats = {
            "total_validations": len(validations),
            "passed": len([v for v in validations if v.status == "PASSED"]),
            "failed": len([v for v in validations if v.status == "FAILED"]),
            "warning": len([v for v in validations if v.status == "WARNING"]),
            "average_pass_rate": sum(v.pass_rate for v in validations) / len(validations) if validations else 0.0,
            "latest_validation": validations[0].created_at if validations else None
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting validation summary: {str(e)}")
        raise
