"""
Validation Result ORM model with ownership tracking.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from datetime import datetime
from app.models.base import Base, IdMixin, TimestampMixin


class ValidationResult(Base, IdMixin, TimestampMixin):
    """Validation result model with creator and dataset tracking."""
    
    __tablename__ = "validation_results"
    
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    validation_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # PASSED, FAILED, WARNING
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    pass_rate = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    errors = Column(JSON, nullable=True)  # Detailed error information
    validation_details = Column(JSON, nullable=True)  # Validation rules and results
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    execution_time_ms = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<ValidationResult(id={self.id}, dataset_id={self.dataset_id}, status={self.status})>"
