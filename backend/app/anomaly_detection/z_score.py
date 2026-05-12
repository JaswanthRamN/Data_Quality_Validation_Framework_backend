"""
Z-Score Anomaly Detection Module

Detects anomalies using the z-score method. A z-score measures how many standard
deviations a value is from the mean. Values with z-scores beyond a threshold
(typically 2 or 3) are considered anomalies.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ZScoreDetector:
    """
    Detects anomalies using the Z-Score method.
    
    Z-Score formula: z = (x - mean) / std_dev
    
    Attributes:
        threshold (float): Z-score threshold for anomaly detection (default: 3.0)
    """
    
    def __init__(self, threshold: float = 3.0):
        """
        Initialize Z-Score detector.
        
        Args:
            threshold (float): Z-score threshold. Values with |z| > threshold are anomalies.
                             Common thresholds: 2.0 (95% confidence), 3.0 (99.7% confidence)
        """
        if threshold <= 0:
            raise ValueError("Threshold must be a positive number")
        self.threshold = threshold
    
    def detect(self, data: List[float]) -> Dict:
        """
        Detect anomalies in a dataset using z-score method.
        
        Args:
            data (List[float]): Input data values
            
        Returns:
            Dict: Detection results including:
                - anomalies: List of anomalous values
                - indices: Indices of anomalous values
                - z_scores: Z-scores for all values
                - mean: Mean of the dataset
                - std_dev: Standard deviation of the dataset
                - threshold: Used threshold
        """
        try:
            if not data or len(data) < 2:
                logger.warning("Insufficient data for z-score analysis")
                return {
                    "anomalies": [],
                    "indices": [],
                    "z_scores": [],
                    "mean": None,
                    "std_dev": None,
                    "threshold": self.threshold
                }
            
            data_array = np.array(data, dtype=float)
            
            # Calculate mean and standard deviation
            mean = np.mean(data_array)
            std_dev = np.std(data_array)
            
            # Handle case where standard deviation is zero
            if std_dev == 0:
                logger.warning("Standard deviation is zero; all values are identical")
                return {
                    "anomalies": [],
                    "indices": [],
                    "z_scores": [0.0] * len(data),
                    "mean": float(mean),
                    "std_dev": 0.0,
                    "threshold": self.threshold
                }
            
            # Calculate z-scores
            z_scores = (data_array - mean) / std_dev
            
            # Identify anomalies
            anomaly_mask = np.abs(z_scores) > self.threshold
            anomalous_indices = np.where(anomaly_mask)[0].tolist()
            anomalous_values = data_array[anomaly_mask].tolist()
            
            return {
                "anomalies": anomalous_values,
                "indices": anomalous_indices,
                "z_scores": z_scores.tolist(),
                "mean": float(mean),
                "std_dev": float(std_dev),
                "threshold": self.threshold,
                "total_points": len(data),
                "anomaly_count": len(anomalous_values),
                "anomaly_percentage": (len(anomalous_values) / len(data) * 100) if len(data) > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Error in z-score detection: {str(e)}")
            raise
    
    def detect_with_details(self, data: List[float]) -> List[Dict]:
        """
        Detect anomalies and return detailed information for each point.
        
        Args:
            data (List[float]): Input data values
            
        Returns:
            List[Dict]: List of dictionaries with details for each point:
                - value: Original value
                - z_score: Z-score of the value
                - is_anomaly: Boolean indicating if it's an anomaly
        """
        try:
            if not data or len(data) < 2:
                return [{"value": v, "z_score": 0.0, "is_anomaly": False} for v in data]
            
            detection_result = self.detect(data)
            anomaly_indices = set(detection_result["indices"])
            z_scores = detection_result["z_scores"]
            
            details = []
            for idx, value in enumerate(data):
                details.append({
                    "index": idx,
                    "value": value,
                    "z_score": z_scores[idx],
                    "is_anomaly": idx in anomaly_indices
                })
            
            return details
        
        except Exception as e:
            logger.error(f"Error in detailed z-score detection: {str(e)}")
            raise
    
    @staticmethod
    def calculate_z_score(value: float, mean: float, std_dev: float) -> float:
        """
        Calculate z-score for a single value.
        
        Args:
            value (float): The value to calculate z-score for
            mean (float): Mean of the reference dataset
            std_dev (float): Standard deviation of the reference dataset
            
        Returns:
            float: Z-score of the value
            
        Raises:
            ValueError: If std_dev is zero
        """
        if std_dev == 0:
            raise ValueError("Standard deviation cannot be zero")
        return (value - mean) / std_dev
    
    def set_threshold(self, threshold: float) -> None:
        """
        Update the anomaly detection threshold.
        
        Args:
            threshold (float): New threshold value
            
        Raises:
            ValueError: If threshold is not positive
        """
        if threshold <= 0:
            raise ValueError("Threshold must be a positive number")
        self.threshold = threshold
        logger.info(f"Z-score threshold updated to {threshold}")


def detect_anomalies(data: List[float], threshold: float = 3.0) -> Dict:
    """
    Convenience function to detect anomalies using z-score method.
    
    Args:
        data (List[float]): Input data values
        threshold (float): Z-score threshold for anomaly detection
        
    Returns:
        Dict: Detection results
    """
    detector = ZScoreDetector(threshold=threshold)
    return detector.detect(data)
