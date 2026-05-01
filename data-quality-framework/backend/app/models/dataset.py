from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    source_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
