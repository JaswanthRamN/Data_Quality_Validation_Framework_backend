"""
Metrics API Routes

Provides endpoints for retrieving and calculating data quality metrics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import logging

from app.database import get_db
from app.schemas.metrics_schema import (
    QualityScoreResponse,
    MetricResponse,
    QualityAnalysisRequest,
    MetricStatisticsResponse
)
from app.metrics.quality_metrics import QualityMetricsCalculator, MetricType
from app.crud import dataset_crud, validation_crud
from app.core.security import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/quality-score/{dataset_id}", response_model=QualityScoreResponse)
async def get_quality_score(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get the quality score for a dataset.
    
    Args:
        dataset_id (int): ID of the dataset
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        Dict: Quality score with metrics breakdown
        
    Raises:
        HTTPException: If dataset not found or unauthorized
    """
    try:
        # Verify dataset exists and user has access
        dataset = dataset_crud.get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        if dataset.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Fetching quality score for dataset {dataset_id}")
        
        # Get validation results for the dataset
        validation_results = validation_crud.get_validation_results_by_dataset(
            db, dataset_id
        )
        
        if not validation_results:
            return {
                "dataset_id": dataset_id,
                "overall_score": 0.0,
                "metrics": [],
                "timestamp": datetime.utcnow().isoformat(),
                "message": "No validation data available"
            }
        
        # Build dataset structure from validation results
        # Group by column and extract values
        dataset_data = {}
        for result in validation_results:
            if result.column_name not in dataset_data:
                dataset_data[result.column_name] = []
            dataset_data[result.column_name].append(result.value)
        
        # Calculate quality metrics
        calculator = QualityMetricsCalculator()
        quality_result = calculator.calculate_dataset_quality(dataset_data)
        
        # Format response
        metrics_response = [
            {
                "name": metric.name,
                "value": metric.value,
                "category": metric.category.value,
                "details": metric.details
            }
            for metric in quality_result.metrics
        ]
        
        return {
            "dataset_id": dataset_id,
            "overall_score": quality_result.overall_score,
            "metrics": metrics_response,
            "timestamp": quality_result.timestamp,
            "issues": quality_result.issues
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quality score for dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating quality score")


@router.get("/metrics/{dataset_id}", response_model=List[MetricResponse])
async def get_metrics(
    dataset_id: int,
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    column_name: Optional[str] = Query(None, description="Filter by column name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """
    Get detailed metrics for a dataset.
    
    Args:
        dataset_id (int): ID of the dataset
        metric_type (Optional[str]): Filter by metric type
        column_name (Optional[str]): Filter by column name
        skip (int): Pagination offset
        limit (int): Pagination limit
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        List[Dict]: List of metrics with details
        
    Raises:
        HTTPException: If dataset not found or unauthorized
    """
    try:
        # Verify dataset exists and user has access
        dataset = dataset_crud.get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        if dataset.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Fetching metrics for dataset {dataset_id}")
        
        # Get validation results
        validation_results = validation_crud.get_validation_results_by_dataset(
            db, dataset_id, skip=skip, limit=limit
        )
        
        metrics = []
        for result in validation_results:
            # Apply filters
            if column_name and result.column_name != column_name:
                continue
            if metric_type and result.rule_name != metric_type:
                continue
            
            metrics.append({
                "id": result.id,
                "dataset_id": result.dataset_id,
                "column_name": result.column_name,
                "rule_name": result.rule_name,
                "value": result.value,
                "is_valid": result.is_valid,
                "error_message": result.error_message,
                "created_at": result.created_at.isoformat() if result.created_at else None
            })
        
        return metrics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching metrics for dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving metrics")


@router.post("/calculate", response_model=QualityScoreResponse)
async def calculate_quality(
    request: QualityAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Calculate quality score for provided data on demand.
    
    Args:
        request (QualityAnalysisRequest): Data and specifications for analysis
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        Dict: Calculated quality score with metrics
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Calculating quality metrics for user {current_user.id}")
        
        # Validate input
        if not request.data or len(request.data) == 0:
            raise HTTPException(status_code=400, detail="No data provided for analysis")
        
        # Calculate metrics
        calculator = QualityMetricsCalculator(weights=request.weights)
        quality_result = calculator.calculate_dataset_quality(
            request.data,
            request.column_specs
        )
        
        # Format response
        metrics_response = [
            {
                "name": metric.name,
                "value": metric.value,
                "category": metric.category.value,
                "details": metric.details
            }
            for metric in quality_result.metrics
        ]
        
        return {
            "overall_score": quality_result.overall_score,
            "metrics": metrics_response,
            "timestamp": quality_result.timestamp,
            "issues": quality_result.issues
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating quality metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating quality metrics")


@router.get("/statistics/{dataset_id}", response_model=MetricStatisticsResponse)
async def get_metric_statistics(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get statistical summary of metrics for a dataset.
    
    Args:
        dataset_id (int): ID of the dataset
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        Dict: Statistics including averages, min/max, distribution
        
    Raises:
        HTTPException: If dataset not found or unauthorized
    """
    try:
        # Verify dataset exists and user has access
        dataset = dataset_crud.get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        if dataset.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Fetching metric statistics for dataset {dataset_id}")
        
        # Get validation results
        validation_results = validation_crud.get_validation_results_by_dataset(
            db, dataset_id
        )
        
        if not validation_results:
            return {
                "dataset_id": dataset_id,
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "pass_rate": 0.0,
                "by_column": {},
                "by_rule": {}
            }
        
        # Calculate statistics
        total_checks = len(validation_results)
        passed_checks = sum(1 for r in validation_results if r.is_valid)
        failed_checks = total_checks - passed_checks
        pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Group by column
        by_column = {}
        for result in validation_results:
            if result.column_name not in by_column:
                by_column[result.column_name] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "pass_rate": 0.0
                }
            by_column[result.column_name]["total"] += 1
            if result.is_valid:
                by_column[result.column_name]["passed"] += 1
            else:
                by_column[result.column_name]["failed"] += 1
        
        # Calculate pass rates by column
        for col_stats in by_column.values():
            col_stats["pass_rate"] = (col_stats["passed"] / col_stats["total"] * 100) if col_stats["total"] > 0 else 0
        
        # Group by rule
        by_rule = {}
        for result in validation_results:
            if result.rule_name not in by_rule:
                by_rule[result.rule_name] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "pass_rate": 0.0
                }
            by_rule[result.rule_name]["total"] += 1
            if result.is_valid:
                by_rule[result.rule_name]["passed"] += 1
            else:
                by_rule[result.rule_name]["failed"] += 1
        
        # Calculate pass rates by rule
        for rule_stats in by_rule.values():
            rule_stats["pass_rate"] = (rule_stats["passed"] / rule_stats["total"] * 100) if rule_stats["total"] > 0 else 0
        
        return {
            "dataset_id": dataset_id,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "pass_rate": pass_rate,
            "by_column": by_column,
            "by_rule": by_rule,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating metric statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating statistics")


@router.get("/summary", response_model=Dict)
async def get_metrics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get summary of all metrics across user's datasets.
    
    Args:
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        Dict: Summary statistics
        
    Raises:
        HTTPException: If user not found
    """
    try:
        logger.info(f"Fetching metrics summary for user {current_user.id}")
        
        # Get all datasets for current user
        datasets = dataset_crud.get_user_datasets(db, current_user.id)
        
        if not datasets:
            return {
                "total_datasets": 0,
                "datasets": [],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Calculate quality scores for each dataset
        summary_data = []
        for dataset in datasets:
            validation_results = validation_crud.get_validation_results_by_dataset(
                db, dataset.id
            )
            
            if validation_results:
                total_checks = len(validation_results)
                passed_checks = sum(1 for r in validation_results if r.is_valid)
                quality_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            else:
                quality_score = 0.0
                total_checks = 0
                passed_checks = 0
            
            summary_data.append({
                "dataset_id": dataset.id,
                "dataset_name": dataset.name,
                "quality_score": quality_score,
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None
            })
        
        return {
            "total_datasets": len(datasets),
            "datasets": summary_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching metrics summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving metrics summary")
