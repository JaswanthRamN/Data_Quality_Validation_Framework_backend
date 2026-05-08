from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from datetime import datetime
from app.models.base import Base

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)
    validation_type = Column(String, index=True)
    status = Column(String)  # PASSED or FAILED
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    pass_rate = Column(Float, default=0.0)
    errors = Column(JSON, nullable=True)
    validation_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
