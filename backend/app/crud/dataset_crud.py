"""
CRUD operations for Dataset model.
Handles dataset creation, retrieval, update, and deletion.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.dataset import Dataset
from app.utils.logger import logger


def create_dataset(
    db: Session,
    name: str,
    source_type: str,
    created_by: int,
    description: str = None,
    file_path: str = None,
    record_count: int = 0,
    column_count: int = 0
) -> Dataset:
    """
    Create a new dataset.
    
    Args:
        db: Database session
        name: Dataset name
        source_type: Source type (csv, json, parquet, database)
        created_by: User ID of creator
        description: Dataset description
        file_path: File path if applicable
        record_count: Number of records
        column_count: Number of columns
        
    Returns:
        Created Dataset object
        
    Raises:
        ValueError: If dataset name already exists
    """
    try:
        db_dataset = Dataset(
            name=name,
            source_type=source_type,
            created_by=created_by,
            description=description,
            file_path=file_path,
            record_count=record_count,
            column_count=column_count
        )
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        logger.info(f"Dataset created: {name} (ID: {db_dataset.id})")
        return db_dataset
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Dataset creation failed - duplicate name: {name}")
        raise ValueError("Dataset with this name already exists")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating dataset: {str(e)}")
        raise


def get_dataset_by_id(db: Session, dataset_id: int) -> Dataset | None:
    """
    Get dataset by ID.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        Dataset object or None
    """
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def get_dataset_by_name(db: Session, name: str) -> Dataset | None:
    """
    Get dataset by name.
    
    Args:
        db: Database session
        name: Dataset name
        
    Returns:
        Dataset object or None
    """
    return db.query(Dataset).filter(Dataset.name == name).first()


def get_user_datasets(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Dataset]:
    """
    Get all datasets created by a user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of Dataset objects
    """
    return db.query(Dataset).filter(
        Dataset.created_by == user_id,
        Dataset.is_active == 1
    ).offset(skip).limit(limit).all()


def get_all_datasets(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Dataset]:
    """
    Get all active datasets.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of Dataset objects
    """
    return db.query(Dataset).filter(
        Dataset.is_active == 1
    ).offset(skip).limit(limit).all()


def update_dataset(
    db: Session,
    dataset_id: int,
    **kwargs
) -> Dataset | None:
    """
    Update dataset fields.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        **kwargs: Fields to update
        
    Returns:
        Updated Dataset object or None
    """
    dataset = get_dataset_by_id(db, dataset_id)
    if not dataset:
        return None
    
    allowed_fields = {
        "description", "record_count", "column_count",
        "file_path", "is_active"
    }
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            setattr(dataset, key, value)
    
    try:
        db.commit()
        db.refresh(dataset)
        logger.info(f"Dataset updated: {dataset_id}")
        return dataset
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating dataset: {str(e)}")
        raise


def delete_dataset(db: Session, dataset_id: int) -> bool:
    """
    Soft delete a dataset (mark as inactive).
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        True if successful
    """
    dataset = get_dataset_by_id(db, dataset_id)
    if not dataset:
        return False
    
    try:
        dataset.is_active = 0
        db.commit()
        logger.info(f"Dataset deleted (soft): {dataset_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting dataset: {str(e)}")
        raise


def hard_delete_dataset(db: Session, dataset_id: int) -> bool:
    """
    Permanently delete a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        True if successful
    """
    dataset = get_dataset_by_id(db, dataset_id)
    if not dataset:
        return False
    
    try:
        db.delete(dataset)
        db.commit()
        logger.info(f"Dataset deleted (hard): {dataset_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error hard deleting dataset: {str(e)}")
        raise
