"""
Daily report ORM model — stores the generated daily job search summary.
"""

from sqlalchemy import Column, String, Text, Integer, JSON, Date, ForeignKey
from app.models.base import Base, TimestampMixin, IdMixin


class DailyReport(Base, TimestampMixin, IdMixin):
    """Persists the AI-generated daily job search summary."""

    __tablename__ = "daily_reports"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    report_date = Column(Date, nullable=False, index=True)

    total_new_jobs = Column(Integer, default=0, nullable=False)
    top_jobs = Column(JSON, nullable=True)         # list of top-10 job summary dicts
    skill_gaps = Column(JSON, nullable=True)        # list[str]
    interview_topics = Column(JSON, nullable=True)  # list[str]
    report_html = Column(Text, nullable=True)

    notion_page_id = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<DailyReport(id={self.id}, date={self.report_date}, jobs={self.total_new_jobs})>"
