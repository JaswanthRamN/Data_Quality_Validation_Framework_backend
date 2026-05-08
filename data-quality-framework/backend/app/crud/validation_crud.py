from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.validation_result import ValidationResult
from typing import List, Dict, Any, Optional

def create_validation_result(
    db: Session,
    dataset_id: int,
    validation_type: str,
    status: str,
    passed_count: int,
    failed_count: int,
    pass_rate: float,
    errors: Optional[List[str]] = None,
    validation_details: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    try:
        db_result = ValidationResult(
            dataset_id=dataset_id,
            validation_type=validation_type,
            status=status,
            passed_count=passed_count,
            failed_count=failed_count,
            pass_rate=pass_rate,
            errors=errors or [],
            validation_details=validation_details or {}
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating validation result")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating validation result: {str(e)}")

def get_validation_result(db: Session, result_id: int) -> ValidationResult:
    try:
        result = db.query(ValidationResult).filter(ValidationResult.id == result_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Validation result not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving validation result: {str(e)}")

def get_all_validation_results(db: Session) -> List[ValidationResult]:
    try:
        return db.query(ValidationResult).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving validation results: {str(e)}")

def get_validation_results_by_dataset(db: Session, dataset_id: int) -> List[ValidationResult]:
    try:
        return db.query(ValidationResult).filter(ValidationResult.dataset_id == dataset_id).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving validation results: {str(e)}")

def get_validation_results_by_type(db: Session, validation_type: str) -> List[ValidationResult]:
    try:
        return db.query(ValidationResult).filter(
            ValidationResult.validation_type == validation_type
        ).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving validation results: {str(e)}")

def get_validation_results_by_status(db: Session, status: str) -> List[ValidationResult]:
    try:
        if status not in ["PASSED", "FAILED"]:
            raise HTTPException(status_code=400, detail="Status must be PASSED or FAILED")
        return db.query(ValidationResult).filter(ValidationResult.status == status).all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving validation results: {str(e)}")

def update_validation_result(
    db: Session,
    result_id: int,
    status: str = None,
    passed_count: int = None,
    failed_count: int = None,
    pass_rate: float = None,
    errors: List[str] = None,
    validation_details: Dict[str, Any] = None
) -> ValidationResult:
    try:
        result = db.query(ValidationResult).filter(ValidationResult.id == result_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Validation result not found")
        
        if status is not None:
            result.status = status
        if passed_count is not None:
            result.passed_count = passed_count
        if failed_count is not None:
            result.failed_count = failed_count
        if pass_rate is not None:
            result.pass_rate = pass_rate
        if errors is not None:
            result.errors = errors
        if validation_details is not None:
            result.validation_details = validation_details
        
        db.commit()
        db.refresh(result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating validation result: {str(e)}")

def delete_validation_result(db: Session, result_id: int) -> bool:
    try:
        result = db.query(ValidationResult).filter(ValidationResult.id == result_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Validation result not found")
        db.delete(result)
        db.commit()
        return True
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting validation result: {str(e)}")

def delete_validation_results_by_dataset(db: Session, dataset_id: int) -> int:
    try:
        count = db.query(ValidationResult).filter(
            ValidationResult.dataset_id == dataset_id
        ).delete()
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting validation results: {str(e)}")
