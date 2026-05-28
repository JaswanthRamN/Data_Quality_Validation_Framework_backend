"""
Job listing ORM model for the job search automation system.
"""

from sqlalchemy import (
    Column, String, Text, Float, Boolean, DateTime, JSON, UniqueConstraint
)
from app.models.base import Base, TimestampMixin, IdMixin


class Job(Base, TimestampMixin, IdMixin):
    """Stores scraped job listings from all sources."""

    __tablename__ = "jobs"

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),
    )

    # Source metadata
    source = Column(String(50), nullable=False, index=True)          # "indeed", "greenhouse"
    external_id = Column(String(255), nullable=False, index=True)    # platform job ID

    # Job info
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    is_remote = Column(Boolean, default=False, nullable=False)
    is_hybrid = Column(Boolean, default=False, nullable=False)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    apply_url = Column(String(1024), nullable=True)
    posted_date = Column(DateTime, nullable=True)

    # Classification
    role_category = Column(String(100), nullable=True, index=True)
    sponsorship_likely = Column(Boolean, default=False, nullable=False)
    is_excluded = Column(Boolean, default=False, nullable=False)

    # ATS analysis results (populated after Claude/fallback analysis)
    composite_score = Column(Float, nullable=True)
    ats_score = Column(Float, nullable=True)
    skill_match_pct = Column(Float, nullable=True)
    missing_keywords = Column(JSON, nullable=True)   # list[str]
    raw_analysis = Column(JSON, nullable=True)        # full analysis payload

    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title!r}, company={self.company!r}, score={self.composite_score})>"
