"""
Data Quality Metrics Module

Calculates various data quality metrics and scores including completeness,
accuracy, consistency, timeliness, and overall quality scores.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Enumeration of metric types."""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"


@dataclass
class QualityMetric:
    """Data structure for quality metrics."""
    name: str
    value: float  # 0-100
    weight: float  # 0-1
    category: MetricType
    details: Optional[Dict] = None


@dataclass
class QualityScore:
    """Data structure for overall quality scores."""
    overall_score: float  # 0-100
    metrics: List[QualityMetric]
    timestamp: str
    dataset_id: Optional[int] = None
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class QualityMetricsCalculator:
    """
    Calculate data quality metrics for datasets.
    
    Supports multiple quality dimensions:
    - Completeness: Percentage of non-null values
    - Accuracy: Percentage of valid/expected values
    - Consistency: Consistency of data across records
    - Timeliness: Data freshness
    - Validity: Conformance to expected format/type
    - Uniqueness: Percentage of unique values
    """
    
    # Default weights for metrics (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        MetricType.COMPLETENESS: 0.25,
        MetricType.ACCURACY: 0.25,
        MetricType.CONSISTENCY: 0.20,
        MetricType.TIMELINESS: 0.15,
        MetricType.VALIDITY: 0.10,
        MetricType.UNIQUENESS: 0.05
    }
    
    def __init__(self, weights: Optional[Dict[MetricType, float]] = None):
        """
        Initialize the calculator.
        
        Args:
            weights (Optional[Dict[MetricType, float]]): Custom weights for metrics
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to 1.0."""
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0):
            logger.warning(f"Metric weights sum to {total_weight}, normalizing to 1.0")
            for key in self.weights:
                self.weights[key] = self.weights[key] / total_weight
    
    def calculate_completeness(
        self,
        data: List,
        null_indicators: Optional[List] = None
    ) -> float:
        """
        Calculate completeness score (percentage of non-null values).
        
        Args:
            data (List): List of values
            null_indicators (Optional[List]): Custom null indicators (e.g., ['', 'NA', 'NULL'])
            
        Returns:
            float: Completeness score (0-100)
        """
        try:
            if not data:
                return 0.0
            
            null_indicators = null_indicators or [None, '', 'null', 'NULL', 'NA', 'N/A']
            
            non_null_count = sum(1 for x in data if x not in null_indicators and x is not None)
            completeness = (non_null_count / len(data)) * 100
            
            return min(completeness, 100.0)
        except Exception as e:
            logger.error(f"Error calculating completeness: {str(e)}")
            return 0.0
    
    def calculate_accuracy(
        self,
        data: List,
        valid_values: Optional[List] = None,
        validation_rule: Optional[callable] = None
    ) -> float:
        """
        Calculate accuracy score based on valid values or validation rule.
        
        Args:
            data (List): List of values
            valid_values (Optional[List]): List of acceptable values
            validation_rule (Optional[callable]): Function to validate each value
            
        Returns:
            float: Accuracy score (0-100)
        """
        try:
            if not data:
                return 0.0
            
            if validation_rule:
                valid_count = sum(1 for x in data if validation_rule(x))
            elif valid_values:
                valid_count = sum(1 for x in data if x in valid_values)
            else:
                return 100.0  # No validation criteria provided
            
            accuracy = (valid_count / len(data)) * 100
            return min(accuracy, 100.0)
        except Exception as e:
            logger.error(f"Error calculating accuracy: {str(e)}")
            return 0.0
    
    def calculate_consistency(
        self,
        data: List,
        expected_type: Optional[type] = None,
        expected_format: Optional[str] = None
    ) -> float:
        """
        Calculate consistency score (data type and format consistency).
        
        Args:
            data (List): List of values
            expected_type (Optional[type]): Expected data type
            expected_format (Optional[str]): Expected format regex pattern
            
        Returns:
            float: Consistency score (0-100)
        """
        try:
            if not data:
                return 0.0
            
            consistent_count = 0
            
            for value in data:
                if value is None or value == '':
                    consistent_count += 1
                    continue
                
                is_consistent = True
                
                # Check type consistency
                if expected_type:
                    is_consistent = is_consistent and isinstance(value, expected_type)
                
                # Check format consistency (if format regex is provided)
                if expected_format and is_consistent:
                    import re
                    is_consistent = is_consistent and bool(re.match(expected_format, str(value)))
                
                if is_consistent:
                    consistent_count += 1
            
            consistency = (consistent_count / len(data)) * 100
            return min(consistency, 100.0)
        except Exception as e:
            logger.error(f"Error calculating consistency: {str(e)}")
            return 0.0
    
    def calculate_timeliness(
        self,
        timestamps: List,
        freshness_threshold_days: int = 30
    ) -> float:
        """
        Calculate timeliness score based on data freshness.
        
        Args:
            timestamps (List): List of timestamp values
            freshness_threshold_days (int): Threshold for considering data fresh
            
        Returns:
            float: Timeliness score (0-100)
        """
        try:
            if not timestamps:
                return 0.0
            
            from datetime import datetime, timedelta
            
            now = datetime.utcnow()
            threshold = now - timedelta(days=freshness_threshold_days)
            
            fresh_count = 0
            for ts in timestamps:
                if ts is None or ts == '':
                    continue
                try:
                    if isinstance(ts, str):
                        ts_obj = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    else:
                        ts_obj = ts
                    
                    if ts_obj >= threshold:
                        fresh_count += 1
                except:
                    pass
            
            timeliness = (fresh_count / len([t for t in timestamps if t is not None and t != ''])) * 100
            return min(timeliness, 100.0)
        except Exception as e:
            logger.error(f"Error calculating timeliness: {str(e)}")
            return 50.0  # Default to moderate score on error
    
    def calculate_validity(
        self,
        data: List,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allowed_types: Optional[List[type]] = None
    ) -> float:
        """
        Calculate validity score (data type and range conformance).
        
        Args:
            data (List): List of values
            min_value (Optional[float]): Minimum valid value
            max_value (Optional[float]): Maximum valid value
            allowed_types (Optional[List[type]]): Allowed data types
            
        Returns:
            float: Validity score (0-100)
        """
        try:
            if not data:
                return 0.0
            
            valid_count = 0
            
            for value in data:
                if value is None or value == '':
                    valid_count += 1
                    continue
                
                is_valid = True
                
                # Check type validity
                if allowed_types:
                    is_valid = is_valid and any(isinstance(value, t) for t in allowed_types)
                
                # Check range validity
                if is_valid and (min_value is not None or max_value is not None):
                    try:
                        numeric_value = float(value)
                        if min_value is not None:
                            is_valid = is_valid and numeric_value >= min_value
                        if max_value is not None:
                            is_valid = is_valid and numeric_value <= max_value
                    except (ValueError, TypeError):
                        is_valid = False
                
                if is_valid:
                    valid_count += 1
            
            validity = (valid_count / len(data)) * 100
            return min(validity, 100.0)
        except Exception as e:
            logger.error(f"Error calculating validity: {str(e)}")
            return 0.0
    
    def calculate_uniqueness(self, data: List) -> float:
        """
        Calculate uniqueness score (percentage of unique values).
        
        Args:
            data (List): List of values
            
        Returns:
            float: Uniqueness score (0-100)
        """
        try:
            if not data:
                return 0.0
            
            # Filter out null values for uniqueness calculation
            non_null_data = [x for x in data if x is not None and x != '']
            if not non_null_data:
                return 0.0
            
            unique_count = len(set(non_null_data))
            uniqueness = (unique_count / len(non_null_data)) * 100
            
            return min(uniqueness, 100.0)
        except Exception as e:
            logger.error(f"Error calculating uniqueness: {str(e)}")
            return 0.0
    
    def calculate_quality_score(
        self,
        metrics: List[QualityMetric]
    ) -> float:
        """
        Calculate overall quality score from individual metrics.
        
        Args:
            metrics (List[QualityMetric]): List of quality metrics
            
        Returns:
            float: Weighted overall quality score (0-100)
        """
        try:
            if not metrics:
                return 0.0
            
            weighted_score = 0.0
            
            for metric in metrics:
                weight = self.weights.get(metric.category, 0.0)
                weighted_score += (metric.value * weight)
            
            return min(max(weighted_score, 0.0), 100.0)
        except Exception as e:
            logger.error(f"Error calculating quality score: {str(e)}")
            return 0.0
    
    def calculate_dataset_quality(
        self,
        dataset: Dict[str, List],
        column_specs: Optional[Dict[str, Dict]] = None
    ) -> QualityScore:
        """
        Calculate comprehensive quality score for an entire dataset.
        
        Args:
            dataset (Dict[str, List]): Dictionary of column_name -> list of values
            column_specs (Optional[Dict[str, Dict]]): Specifications for each column
                containing validation rules, types, formats, etc.
            
        Returns:
            QualityScore: Comprehensive quality score with metrics
        """
        try:
            from datetime import datetime
            
            metrics = []
            issues = []
            
            column_specs = column_specs or {}
            
            # Calculate metrics for each column
            for column_name, values in dataset.items():
                spec = column_specs.get(column_name, {})
                
                # Completeness
                completeness = self.calculate_completeness(
                    values,
                    spec.get('null_indicators')
                )
                metrics.append(QualityMetric(
                    name=f"{column_name}_completeness",
                    value=completeness,
                    weight=self.weights[MetricType.COMPLETENESS],
                    category=MetricType.COMPLETENESS,
                    details={"column": column_name, "null_count": sum(1 for x in values if x is None or x == '')}
                ))
                
                # Accuracy
                accuracy = self.calculate_accuracy(
                    values,
                    spec.get('valid_values'),
                    spec.get('validation_rule')
                )
                metrics.append(QualityMetric(
                    name=f"{column_name}_accuracy",
                    value=accuracy,
                    weight=self.weights[MetricType.ACCURACY],
                    category=MetricType.ACCURACY,
                    details={"column": column_name}
                ))
                
                # Consistency
                consistency = self.calculate_consistency(
                    values,
                    spec.get('expected_type'),
                    spec.get('expected_format')
                )
                metrics.append(QualityMetric(
                    name=f"{column_name}_consistency",
                    value=consistency,
                    weight=self.weights[MetricType.CONSISTENCY],
                    category=MetricType.CONSISTENCY,
                    details={"column": column_name}
                ))
                
                # Validity
                validity = self.calculate_validity(
                    values,
                    spec.get('min_value'),
                    spec.get('max_value'),
                    spec.get('allowed_types')
                )
                metrics.append(QualityMetric(
                    name=f"{column_name}_validity",
                    value=validity,
                    weight=self.weights[MetricType.VALIDITY],
                    category=MetricType.VALIDITY,
                    details={"column": column_name}
                ))
                
                # Uniqueness
                uniqueness = self.calculate_uniqueness(values)
                metrics.append(QualityMetric(
                    name=f"{column_name}_uniqueness",
                    value=uniqueness,
                    weight=self.weights[MetricType.UNIQUENESS],
                    category=MetricType.UNIQUENESS,
                    details={"column": column_name, "unique_count": len(set(values))}
                ))
                
                # Flag low quality metrics
                if completeness < 80:
                    issues.append(f"Column '{column_name}': Low completeness ({completeness:.2f}%)")
                if accuracy < 80:
                    issues.append(f"Column '{column_name}': Low accuracy ({accuracy:.2f}%)")
                if consistency < 80:
                    issues.append(f"Column '{column_name}': Low consistency ({consistency:.2f}%)")
            
            # Calculate overall score
            overall_score = self.calculate_quality_score(metrics)
            
            return QualityScore(
                overall_score=overall_score,
                metrics=metrics,
                timestamp=datetime.utcnow().isoformat(),
                issues=issues
            )
        
        except Exception as e:
            logger.error(f"Error calculating dataset quality: {str(e)}")
            raise


def calculate_quality_score(dataset: Dict[str, List]) -> float:
    """
    Convenience function to calculate quality score for a dataset.
    
    Args:
        dataset (Dict[str, List]): Dictionary of column_name -> list of values
        
    Returns:
        float: Overall quality score (0-100)
    """
    calculator = QualityMetricsCalculator()
    quality = calculator.calculate_dataset_quality(dataset)
    return quality.overall_score
