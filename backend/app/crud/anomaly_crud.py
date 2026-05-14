"""
CRUD operations for Anomaly Results

Provides Create, Read, Update, Delete operations for anomaly detection results.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
from datetime import datetime
from app.models.anomaly_result import AnomalyResult
from app.schemas.anomaly_schema import AnomalyResultCreate, AnomalyResultUpdate
import logging

logger = logging.getLogger(__name__)


def create_anomaly_result(db: Session, anomaly_result: AnomalyResultCreate) -> AnomalyResult:
    """
    Create a new anomaly result record.
    
    Args:
        db (Session): Database session
        anomaly_result (AnomalyResultCreate): Anomaly result data
        
    Returns:
        AnomalyResult: Created anomaly result
    """
    try:
        db_anomaly = AnomalyResult(
            dataset_id=anomaly_result.dataset_id,
            detection_method=anomaly_result.detection_method,
            column_name=anomaly_result.column_name,
            value=anomaly_result.value,
            anomaly_score=anomaly_result.anomaly_score,
            is_anomaly=anomaly_result.is_anomaly,
            lower_bound=anomaly_result.lower_bound,
            upper_bound=anomaly_result.upper_bound,
            threshold=anomaly_result.threshold,
            metadata=anomaly_result.metadata
        )
        db.add(db_anomaly)
        db.commit()
        db.refresh(db_anomaly)
        logger.info(f"Created anomaly result with ID {db_anomaly.id}")
        return db_anomaly
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating anomaly result: {str(e)}")
        raise


def create_batch_anomaly_results(
    db: Session, 
    anomaly_results: List[AnomalyResultCreate]
) -> List[AnomalyResult]:
    """
    Create multiple anomaly result records in batch.
    
    Args:
        db (Session): Database session
        anomaly_results (List[AnomalyResultCreate]): List of anomaly results to create
        
    Returns:
        List[AnomalyResult]: List of created anomaly results
    """
    try:
        db_anomalies = [
            AnomalyResult(
                dataset_id=ar.dataset_id,
                detection_method=ar.detection_method,
                column_name=ar.column_name,
                value=ar.value,
                anomaly_score=ar.anomaly_score,
                is_anomaly=ar.is_anomaly,
                lower_bound=ar.lower_bound,
                upper_bound=ar.upper_bound,
                threshold=ar.threshold,
                metadata=ar.metadata
            )
            for ar in anomaly_results
        ]
        db.add_all(db_anomalies)
        db.commit()
        for anomaly in db_anomalies:
            db.refresh(anomaly)
        logger.info(f"Batch created {len(db_anomalies)} anomaly results")
        return db_anomalies
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch creating anomaly results: {str(e)}")
        raise


def get_anomaly_result(db: Session, anomaly_id: int) -> Optional[AnomalyResult]:
    """
    Retrieve a single anomaly result by ID.
    
    Args:
        db (Session): Database session
        anomaly_id (int): ID of the anomaly result
        
    Returns:
        Optional[AnomalyResult]: Anomaly result or None if not found
    """
    try:
        return db.query(AnomalyResult).filter(AnomalyResult.id == anomaly_id).first()
    except Exception as e:
        logger.error(f"Error retrieving anomaly result {anomaly_id}: {str(e)}")
        raise


def get_anomaly_results_by_dataset(
    db: Session,
    dataset_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[AnomalyResult]:
    """
    Retrieve all anomaly results for a specific dataset.
    
    Args:
        db (Session): Database session
        dataset_id (int): ID of the dataset
        skip (int): Number of records to skip (pagination)
        limit (int): Maximum number of records to return
        
    Returns:
        List[AnomalyResult]: List of anomaly results
    """
    try:
        return db.query(AnomalyResult).filter(
            AnomalyResult.dataset_id == dataset_id
        ).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error retrieving anomaly results for dataset {dataset_id}: {str(e)}")
        raise


def get_anomalies_by_method(
    db: Session,
    dataset_id: int,
    detection_method: str,
    skip: int = 0,
    limit: int = 100
) -> List[AnomalyResult]:
    """
    Retrieve anomaly results filtered by detection method.
    
    Args:
        db (Session): Database session
        dataset_id (int): ID of the dataset
        detection_method (str): Detection method (e.g., 'z_score', 'iqr')
        skip (int): Number of records to skip (pagination)
        limit (int): Maximum number of records to return
        
    Returns:
        List[AnomalyResult]: List of anomaly results
    """
    try:
        return db.query(AnomalyResult).filter(
            and_(
                AnomalyResult.dataset_id == dataset_id,
                AnomalyResult.detection_method == detection_method
            )
        ).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error retrieving anomalies by method: {str(e)}")
        raise


def get_detected_anomalies(
    db: Session,
    dataset_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[AnomalyResult]:
    """
    Retrieve only the records that were flagged as anomalies.
    
    Args:
        db (Session): Database session
        dataset_id (int): ID of the dataset
        skip (int): Number of records to skip (pagination)
        limit (int): Maximum number of records to return
        
    Returns:
        List[AnomalyResult]: List of anomalies (is_anomaly=True)
    """
    try:
        return db.query(AnomalyResult).filter(
            and_(
                AnomalyResult.dataset_id == dataset_id,
                AnomalyResult.is_anomaly == True
            )
        ).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error retrieving detected anomalies: {str(e)}")
        raise


def get_anomalies_by_column(
    db: Session,
    dataset_id: int,
    column_name: str,
    skip: int = 0,
    limit: int = 100
) -> List[AnomalyResult]:
    """
    Retrieve anomaly results for a specific column.
    
    Args:
        db (Session): Database session
        dataset_id (int): ID of the dataset
        column_name (str): Name of the column
        skip (int): Number of records to skip (pagination)
        limit (int): Maximum number of records to return
        
    Returns:
        List[AnomalyResult]: List of anomaly results for the column
    """
    try:
        return db.query(AnomalyResult).filter(
            and_(
                AnomalyResult.dataset_id == dataset_id,
                AnomalyResult.column_name == column_name
            )
        ).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error retrieving anomalies for column {column_name}: {str(e)}")
        raise


def get_anomaly_statistics(db: Session, dataset_id: int) -> Dict:
    """
    Get anomaly statistics for a dataset.
    
    Args:
        db (Session): Database session
        dataset_id (int): ID of the dataset
        
    Returns:
        Dict: Statistics including total records, anomaly count, anomaly percentage, methods used
    """
    try:
        total = db.query(AnomalyResult).filter(
            AnomalyResult.dataset_id == dataset_id
        ).count()
        
        anomaly_count = db.query(AnomalyResult).filter(
            and_(
                AnomalyResult.dataset_id == dataset_id,
                AnomalyResult.is_anomaly == True
            )
        ).count()
        
        methods = db.query(AnomalyResult.detection_method).filter(
            AnomalyResult.dataset_id == dataset_id
        ).distinct().all()
        
        return {
            "total_records": total,
            "anomaly_count": anomaly_count,
            "anomaly_percentage": (anomaly_count / total * 100) if total > 0 else 0,
            "detection_methods": [m[0] for m in methods]
        }
    except Exception as e:
        logger.error(f"Error calculating anomaly statistics: {str(e)}")
        raise


def update_anomaly_result(
    db: Session,
    anomaly_id: int,
    anomaly_update: AnomalyResultUpdate
) -> Optional[AnomalyResult]:
    """
    Update an existing anomaly result record.
    
    Args:
        db (Session): Database session
        anomaly_id (int): ID of the anomaly result to update
        anomaly_update (AnomalyResultUpdate): Updated data
        
    Returns:
        Optional[AnomalyResult]: Updated anomaly result or None if not found
    """
    try:
        db_anomaly = db.query(AnomalyResult).filter(AnomalyResult.id == anomaly_id).first()
        if not db_anomaly:
            logger.warning(f"Anomaly result {anomaly_id} not found")
            return None
        
        update_data = anomaly_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_anomaly, key, value)
        
        db_anomaly.updated_at = datetime.utcnow()
        db.add(db_anomaly)
        db.commit()
        db.refresh(db_anomaly)
        logger.info(f"Updated anomaly result {anomaly_id}")
        return db_anomaly
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating anomaly result {anomaly_id}: {str(e)}")
        raise


def delete_anomaly_result(db: Session, anomaly_id: int) -> bool:
    """
    Delete an anomaly result record.
    
    Args:
        db (Session): Database session
        anomaly_id (int): ID of the anomaly result to delete
        
    Returns:
        bool: True if deletion was successful, False if record not found
    """
    try:
        db_anomaly = db.query(AnomalyResult).filter(AnomalyResult.id == anomaly_id).first()
        if not db_anomaly:
            logger.warning(f"Anomaly result {anomaly_id} not found for deletion")
            return False
        
        db.delete(db_anomaly)
        db.commit()
        logger.info(f"Deleted anomaly result {anomaly_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting anomaly result {anomaly_id}: {str(e)}")
        raise


def delete_anomalies_by_dataset(db: Session, dataset_id: int) -> int:
    """
    Delete all anomaly results for a specific dataset.
    
    Args:
        db (Session): Database session
        dataset_id (int): ID of the dataset
        
    Returns:
        int: Number of records deleted
    """
    try:
        count = db.query(AnomalyResult).filter(
            AnomalyResult.dataset_id == dataset_id
        ).delete()
        db.commit()
        logger.info(f"Deleted {count} anomaly results for dataset {dataset_id}")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting anomalies for dataset {dataset_id}: {str(e)}")
        raise


def delete_anomalies_by_method(db: Session, dataset_id: int, detection_method: str) -> int:
    """
    Delete anomaly results by detection method for a dataset.
    
    Args:
        db (Session): Database session
        dataset_id (int): ID of the dataset
        detection_method (str): Detection method to delete
        
    Returns:
        int: Number of records deleted
    """
    try:
        count = db.query(AnomalyResult).filter(
            and_(
                AnomalyResult.dataset_id == dataset_id,
                AnomalyResult.detection_method == detection_method
            )
        ).delete()
        db.commit()
        logger.info(f"Deleted {count} anomaly results for method {detection_method}")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting anomalies by method: {str(e)}")
        raise
