"""
Interquartile Range (IQR) Anomaly Detection Module

Detects anomalies using the IQR method. The IQR is the range between the first
quartile (Q1, 25th percentile) and third quartile (Q3, 75th percentile). 
Values outside the bounds [Q1 - 1.5*IQR, Q3 + 1.5*IQR] are considered anomalies.
"""

import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class IQRDetector:
    """
    Detects anomalies using the Interquartile Range (IQR) method.
    
    IQR-based bounds:
    - Lower bound = Q1 - k * IQR (default k=1.5)
    - Upper bound = Q3 + k * IQR (default k=1.5)
    
    Attributes:
        multiplier (float): Multiplier for IQR bounds (default: 1.5)
    """
    
    def __init__(self, multiplier: float = 1.5):
        """
        Initialize IQR detector.
        
        Args:
            multiplier (float): Multiplier for IQR calculation.
                               Common value is 1.5 (standard outlier detection)
                               Use 3.0 for extreme outliers only
        """
        if multiplier <= 0:
            raise ValueError("Multiplier must be a positive number")
        self.multiplier = multiplier
    
    def detect(self, data: List[float]) -> Dict:
        """
        Detect anomalies in a dataset using IQR method.
        
        Args:
            data (List[float]): Input data values
            
        Returns:
            Dict: Detection results including:
                - anomalies: List of anomalous values
                - indices: Indices of anomalous values
                - q1: First quartile (25th percentile)
                - q3: Third quartile (75th percentile)
                - iqr: Interquartile range (Q3 - Q1)
                - lower_bound: Lower anomaly threshold
                - upper_bound: Upper anomaly threshold
                - multiplier: Used multiplier
        """
        try:
            if not data or len(data) < 4:
                logger.warning("Insufficient data for IQR analysis (need at least 4 values)")
                return {
                    "anomalies": [],
                    "indices": [],
                    "q1": None,
                    "q3": None,
                    "iqr": None,
                    "lower_bound": None,
                    "upper_bound": None,
                    "multiplier": self.multiplier
                }
            
            data_array = np.array(data, dtype=float)
            
            # Calculate quartiles
            q1 = np.percentile(data_array, 25)
            q3 = np.percentile(data_array, 75)
            iqr = q3 - q1
            
            # Handle case where IQR is zero (all values are the same)
            if iqr == 0:
                logger.warning("IQR is zero; all values are identical or in same quartile")
                return {
                    "anomalies": [],
                    "indices": [],
                    "q1": float(q1),
                    "q3": float(q3),
                    "iqr": 0.0,
                    "lower_bound": float(q1),
                    "upper_bound": float(q3),
                    "multiplier": self.multiplier,
                    "total_points": len(data),
                    "anomaly_count": 0,
                    "anomaly_percentage": 0.0
                }
            
            # Calculate bounds
            lower_bound = q1 - self.multiplier * iqr
            upper_bound = q3 + self.multiplier * iqr
            
            # Identify anomalies (values outside bounds)
            anomaly_mask = (data_array < lower_bound) | (data_array > upper_bound)
            anomalous_indices = np.where(anomaly_mask)[0].tolist()
            anomalous_values = data_array[anomaly_mask].tolist()
            
            return {
                "anomalies": anomalous_values,
                "indices": anomalous_indices,
                "q1": float(q1),
                "q3": float(q3),
                "iqr": float(iqr),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "multiplier": self.multiplier,
                "total_points": len(data),
                "anomaly_count": len(anomalous_values),
                "anomaly_percentage": (len(anomalous_values) / len(data) * 100) if len(data) > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Error in IQR detection: {str(e)}")
            raise
    
    def detect_with_details(self, data: List[float]) -> List[Dict]:
        """
        Detect anomalies and return detailed information for each point.
        
        Args:
            data (List[float]): Input data values
            
        Returns:
            List[Dict]: List of dictionaries with details for each point:
                - value: Original value
                - is_anomaly: Boolean indicating if it's an anomaly
                - is_lower_outlier: True if below lower bound
                - is_upper_outlier: True if above upper bound
        """
        try:
            if not data or len(data) < 4:
                return [
                    {"index": idx, "value": v, "is_anomaly": False, 
                     "is_lower_outlier": False, "is_upper_outlier": False}
                    for idx, v in enumerate(data)
                ]
            
            detection_result = self.detect(data)
            anomaly_indices = set(detection_result["indices"])
            lower_bound = detection_result["lower_bound"]
            upper_bound = detection_result["upper_bound"]
            
            details = []
            for idx, value in enumerate(data):
                is_anomaly = idx in anomaly_indices
                is_lower_outlier = value < lower_bound if lower_bound is not None else False
                is_upper_outlier = value > upper_bound if upper_bound is not None else False
                
                details.append({
                    "index": idx,
                    "value": value,
                    "is_anomaly": is_anomaly,
                    "is_lower_outlier": is_lower_outlier,
                    "is_upper_outlier": is_upper_outlier
                })
            
            return details
        
        except Exception as e:
            logger.error(f"Error in detailed IQR detection: {str(e)}")
            raise
    
    @staticmethod
    def calculate_bounds(q1: float, q3: float, multiplier: float = 1.5) -> Dict[str, float]:
        """
        Calculate IQR-based bounds for anomaly detection.
        
        Args:
            q1 (float): First quartile (25th percentile)
            q3 (float): Third quartile (75th percentile)
            multiplier (float): Multiplier for IQR
            
        Returns:
            Dict: Dictionary with 'lower_bound', 'upper_bound', and 'iqr'
            
        Raises:
            ValueError: If q1 or q3 is invalid or q1 >= q3
        """
        if q1 >= q3:
            raise ValueError("Q1 must be less than Q3")
        
        iqr = q3 - q1
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        
        return {
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound
        }
    
    def set_multiplier(self, multiplier: float) -> None:
        """
        Update the IQR multiplier.
        
        Args:
            multiplier (float): New multiplier value
            
        Raises:
            ValueError: If multiplier is not positive
        """
        if multiplier <= 0:
            raise ValueError("Multiplier must be a positive number")
        self.multiplier = multiplier
        logger.info(f"IQR multiplier updated to {multiplier}")
    
    @staticmethod
    def get_quartiles(data: List[float]) -> Dict[str, float]:
        """
        Get quartile information for a dataset.
        
        Args:
            data (List[float]): Input data values
            
        Returns:
            Dict: Dictionary with quartile information:
                - q0 (min): Minimum value
                - q1: First quartile (25th percentile)
                - q2 (median): Second quartile (50th percentile)
                - q3: Third quartile (75th percentile)
                - q4 (max): Maximum value
                - iqr: Interquartile range
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        data_array = np.array(data, dtype=float)
        q0 = float(np.min(data_array))
        q1 = float(np.percentile(data_array, 25))
        q2 = float(np.percentile(data_array, 50))
        q3 = float(np.percentile(data_array, 75))
        q4 = float(np.max(data_array))
        
        return {
            "min": q0,
            "q1": q1,
            "median": q2,
            "q3": q3,
            "max": q4,
            "iqr": q3 - q1
        }


def detect_anomalies(data: List[float], multiplier: float = 1.5) -> Dict:
    """
    Convenience function to detect anomalies using IQR method.
    
    Args:
        data (List[float]): Input data values
        multiplier (float): Multiplier for IQR bounds (default: 1.5)
        
    Returns:
        Dict: Detection results
    """
    detector = IQRDetector(multiplier=multiplier)
    return detector.detect(data)
