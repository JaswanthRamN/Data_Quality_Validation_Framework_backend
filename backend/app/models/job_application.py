"""
Job application tracker ORM model.
"""

import enum
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum
from app.models.base import Base, TimestampMixin, IdMixin


class ApplicationStatus(str, enum.Enum):
    NEW = "NEW"
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"


class JobApplication(Base, TimestampMixin, IdMixin):
    """Tracks the lifecycle of a job application."""

    __tablename__ = "job_applications"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.NEW,
        nullable=False,
        index=True,
    )

    applied_date = Column(DateTime, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)

    # Generated application materials
    cover_letter = Column(Text, nullable=True)
    outreach_message = Column(Text, nullable=True)
    linkedin_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Foreign keys to generated resume version
    resume_version_id = Column(
        Integer, ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True
    )

    # Notion sync
    notion_page_id = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<JobApplication(id={self.id}, job_id={self.job_id}, status={self.status})>"
