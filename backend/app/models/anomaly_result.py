"""
Anomaly Detection Result Model

Stores results from anomaly detection operations including z-score and IQR methods.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class AnomalyResult(Base):
    """
    SQLAlchemy model for storing anomaly detection results.
    
    Attributes:
        id: Unique identifier for the anomaly result
        dataset_id: Foreign key reference to the dataset
        detection_method: Method used for detection (e.g., 'z_score', 'iqr')
        column_name: Name of the column analyzed
        value: The data point value that was analyzed
        anomaly_score: Numerical score indicating degree of anomaly (z-score, percentile, etc.)
        is_anomaly: Boolean indicating if the value is an anomaly
        lower_bound: Lower threshold/bound for anomaly detection
        upper_bound: Upper threshold/bound for anomaly detection
        threshold: Detection threshold used (for z-score method)
        extra_metadata: Additional metadata as JSON (e.g., statistics used in detection)
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    
    __tablename__ = "anomaly_results"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    detection_method = Column(String(50), nullable=False, index=True)  # 'z_score', 'iqr', etc.
    column_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)  # Z-score, outlier measure, etc.
    is_anomaly = Column(Boolean, default=False, index=True)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    extra_metadata = Column(JSON, nullable=True)  # Additional context (mean, std_dev, q1, q3, iqr, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dataset = relationship("Dataset")
    
    def __repr__(self):
        return f"<AnomalyResult(id={self.id}, dataset_id={self.dataset_id}, method={self.detection_method}, is_anomaly={self.is_anomaly})>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "detection_method": self.detection_method,
            "column_name": self.column_name,
            "value": self.value,
            "anomaly_score": self.anomaly_score,
            "is_anomaly": self.is_anomaly,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "threshold": self.threshold,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
