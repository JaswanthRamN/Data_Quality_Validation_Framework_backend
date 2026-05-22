"""
Secured dataset API routes with authentication.
Requires JWT token for all operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.dependencies import get_current_user, get_admin_user
from app.schemas.dataset_schema import DatasetCreate, DatasetResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post(
    "/", 
    response_model=DatasetResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)]
)
def create_dataset(
    dataset_data: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new dataset.
    Requires authentication.
    
    Args:
        dataset_data: Dataset creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created dataset
    """
    try:
        db_dataset = Dataset(
            **dataset_data.dict(),
            created_by=current_user.id
        )
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        logger.info(f"Dataset created by user {current_user.username}: {db_dataset.name}")
        return db_dataset
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dataset"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/", 
    response_model=list[DatasetResponse],
    dependencies=[Depends(get_current_user)]
)
def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    List all datasets the user has access to.
    Requires authentication.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of datasets
    """
    try:
        query = db.query(Dataset)
        
        # Non-admin users only see their own datasets
        if not current_user.is_admin:
            query = query.filter(Dataset.created_by == current_user.id)
        
        datasets = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(datasets)} datasets for user {current_user.username}")
        return datasets
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve datasets"
        )


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
    dependencies=[Depends(get_current_user)]
)
def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific dataset by ID.
    Requires authentication. Non-admin users can only access their own datasets.
    
    Args:
        dataset_id: Dataset ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dataset details
    """
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        
        if not dataset:
            logger.warning(f"Dataset not found: {dataset_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Check access permissions
        if not current_user.is_admin and dataset.created_by != current_user.id:
            logger.warning(
                f"Unauthorized access attempt to dataset {dataset_id} by user {current_user.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this dataset"
            )
        
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dataset"
        )


@router.delete(
    "/{dataset_id}",
    dependencies=[Depends(get_current_user)]
)
def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a dataset.
    Requires authentication. Non-admin users can only delete their own datasets.
    
    Args:
        dataset_id: Dataset ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        
        if not dataset:
            logger.warning(f"Dataset not found for deletion: {dataset_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Check deletion permissions
        if not current_user.is_admin and dataset.created_by != current_user.id:
            logger.warning(
                f"Unauthorized deletion attempt on dataset {dataset_id} by user {current_user.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this dataset"
            )
        
        db.delete(dataset)
        db.commit()
        logger.info(f"Dataset deleted by user {current_user.username}: {dataset_id}")
        
        return {"message": "Dataset deleted successfully", "dataset_id": dataset_id}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dataset"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/user/{username}/datasets",
    response_model=list[DatasetResponse],
    dependencies=[Depends(get_admin_user)]
)
def get_user_datasets(
    username: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all datasets for a specific user.
    Admin only endpoint.
    
    Args:
        username: Username
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        List of user's datasets
    """
    from app.models.user import User as UserModel
    
    try:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        datasets = db.query(Dataset).filter(Dataset.created_by == user.id).all()
        logger.info(f"Admin {current_user.username} retrieved datasets for user {username}")
        return datasets
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user datasets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve datasets"
        )
