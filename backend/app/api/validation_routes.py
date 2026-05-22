"""
Secured validation API routes with authentication.
Requires JWT token for all operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models.user import User
from app.models.validation_result import ValidationResult
from app.models.dataset import Dataset
from app.dependencies import get_current_user, get_admin_user
from app.schemas.validation_schema import ValidationCreate, ValidationResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/validations", tags=["validations"])


@router.post(
    "/",
    response_model=ValidationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)]
)
def create_validation(
    validation_data: ValidationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new validation result.
    Requires authentication and access to the dataset.
    
    Args:
        validation_data: Validation creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created validation result
    """
    try:
        # Verify user has access to the dataset
        dataset = db.query(Dataset).filter(Dataset.id == validation_data.dataset_id).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        if not current_user.is_admin and dataset.created_by != current_user.id:
            logger.warning(
                f"Unauthorized validation attempt on dataset {validation_data.dataset_id} by user {current_user.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to validate this dataset"
            )
        
        db_validation = ValidationResult(
            **validation_data.dict(),
            created_by=current_user.id
        )
        db.add(db_validation)
        db.commit()
        db.refresh(db_validation)
        logger.info(f"Validation created by user {current_user.username}: {db_validation.id}")
        return db_validation
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create validation"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=list[ValidationResponse],
    dependencies=[Depends(get_current_user)]
)
def list_validations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    dataset_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    List validations with optional filtering.
    Requires authentication. Non-admin users only see their own validations.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        dataset_id: Optional dataset ID filter
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of validation results
    """
    try:
        query = db.query(ValidationResult)
        
        # Filter by dataset if provided
        if dataset_id:
            query = query.filter(ValidationResult.dataset_id == dataset_id)
        
        # Non-admin users only see their own validations
        if not current_user.is_admin:
            query = query.filter(ValidationResult.created_by == current_user.id)
        
        validations = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(validations)} validations for user {current_user.username}")
        return validations
    except Exception as e:
        logger.error(f"Error listing validations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve validations"
        )


@router.get(
    "/{validation_id}",
    response_model=ValidationResponse,
    dependencies=[Depends(get_current_user)]
)
def get_validation(
    validation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific validation result by ID.
    Requires authentication. Non-admin users can only access their own validations.
    
    Args:
        validation_id: Validation ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Validation result details
    """
    try:
        validation = db.query(ValidationResult).filter(
            ValidationResult.id == validation_id
        ).first()
        
        if not validation:
            logger.warning(f"Validation not found: {validation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation not found"
            )
        
        # Check access permissions
        if not current_user.is_admin and validation.created_by != current_user.id:
            logger.warning(
                f"Unauthorized access attempt to validation {validation_id} by user {current_user.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this validation"
            )
        
        return validation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve validation"
        )


@router.delete(
    "/{validation_id}",
    dependencies=[Depends(get_current_user)]
)
def delete_validation(
    validation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a validation result.
    Requires authentication. Non-admin users can only delete their own validations.
    
    Args:
        validation_id: Validation ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        validation = db.query(ValidationResult).filter(
            ValidationResult.id == validation_id
        ).first()
        
        if not validation:
            logger.warning(f"Validation not found for deletion: {validation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation not found"
            )
        
        # Check deletion permissions
        if not current_user.is_admin and validation.created_by != current_user.id:
            logger.warning(
                f"Unauthorized deletion attempt on validation {validation_id} by user {current_user.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this validation"
            )
        
        db.delete(validation)
        db.commit()
        logger.info(f"Validation deleted by user {current_user.username}: {validation_id}")
        
        return {"message": "Validation deleted successfully", "validation_id": validation_id}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete validation"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/dataset/{dataset_id}/results",
    response_model=list[ValidationResponse],
    dependencies=[Depends(get_current_user)]
)
def get_dataset_validations(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all validation results for a specific dataset.
    Requires access to the dataset.
    
    Args:
        dataset_id: Dataset ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of validation results for the dataset
    """
    try:
        # Verify user has access to the dataset
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        if not current_user.is_admin and dataset.created_by != current_user.id:
            logger.warning(
                f"Unauthorized access to dataset {dataset_id} validations by user {current_user.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this dataset's validations"
            )
        
        validations = db.query(ValidationResult).filter(
            ValidationResult.dataset_id == dataset_id
        ).all()
        
        return validations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dataset validations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve validations"
        )
