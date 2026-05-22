"""
Dataset ORM model with ownership tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.models.base import Base, IdMixin, TimestampMixin


class Dataset(Base, IdMixin, TimestampMixin):
    """Dataset model with creator tracking."""
    
    __tablename__ = "datasets"
    
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    source_type = Column(String(50), nullable=False, index=True)  # csv, json, parquet, database
    file_path = Column(String(500), nullable=True)
    record_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_active = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, source_type={self.source_type})>"
