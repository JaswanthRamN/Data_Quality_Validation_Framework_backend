"""
SQLAlchemy declarative base and common model utilities.
Provides base class for all models and timestamp mixins.
"""

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid


# Create declarative base for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )


class IdMixin:
    """Mixin to add auto-incrementing ID primary key."""

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )


class BaseModel(Base, IdMixin, TimestampMixin):
    """
    Abstract base model with common fields.
    All models should inherit from this.
    """

    __abstract__ = True

    def __repr__(self) -> str:
        """String representation of model."""
        class_name = self.__class__.__name__
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        )
        return f"<{class_name}({attrs})>"

    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns
        }
