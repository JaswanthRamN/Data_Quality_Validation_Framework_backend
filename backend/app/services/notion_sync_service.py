"""
Notion sync service — creates and updates a Job Applications tracker database
in the user's Notion workspace using the Notion MCP tools.

NOTE: The actual MCP tool calls (notion-create-database, notion-create-pages,
notion-update-page) must be issued from the Claude agent context. This service
provides the data-preparation layer and stores results back to the database.
The Celery tasks and API routes call the MCP tools directly and pass results here.
"""

import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from app.config import settings
from app.models.job import Job
from app.models.job_application import JobApplication
from app.models.daily_report import DailyReport

logger = logging.getLogger(__name__)


class NotionSyncService:
    """
    Prepares payloads for Notion MCP tool calls and persists returned page IDs.
    """

    def build_job_tracker_schema(self) -> str:
        """Returns the SQL DDL schema string for the Notion job tracker database."""
        return """CREATE TABLE (
            "Job Title" TITLE,
            "Company" RICH_TEXT,
            "Location" RICH_TEXT,
            "Status" SELECT('New':blue, 'Saved':gray, 'Applied':yellow, 'Interview':orange, 'Offer':green, 'Rejected':red),
            "Match Score" NUMBER,
            "ATS Score" NUMBER,
            "Salary Range" RICH_TEXT,
            "Remote" CHECKBOX,
            "Sponsorship" CHECKBOX,
            "Apply URL" URL,
            "Applied Date" DATE,
            "Follow Up Date" DATE,
            "Notes" RICH_TEXT
        )"""

    def build_job_page_properties(self, job: Job, application: Optional[JobApplication]) -> dict:
        """Build Notion page properties dict for a job listing."""
        salary = ""
        if job.salary_min and job.salary_max:
            salary = f"${job.salary_min:,.0f}–${job.salary_max:,.0f}"
        elif job.salary_min:
            salary = f"${job.salary_min:,.0f}+"

        props = {
            "Job Title": f"{job.title} — {job.company}",
            "Company": job.company,
            "Location": job.location or ("Remote" if job.is_remote else ""),
            "Status": (application.status.value if application else "New"),
            "Match Score": job.composite_score or 0,
            "ATS Score": job.ats_score or 0,
            "Salary Range": salary,
            "Remote": "__YES__" if job.is_remote else "__NO__",
            "Sponsorship": "__YES__" if job.sponsorship_likely else "__NO__",
            "userDefined:Apply URL": job.apply_url or "",
            "Notes": "",
        }
        if application and application.applied_date:
            props["date:Applied Date:start"] = application.applied_date.strftime("%Y-%m-%d")
            props["date:Applied Date:is_datetime"] = 0
        if application and application.follow_up_date:
            props["date:Follow Up Date:start"] = application.follow_up_date.strftime("%Y-%m-%d")
            props["date:Follow Up Date:is_datetime"] = 0
        return props

    def build_daily_report_content(self, report: DailyReport) -> str:
        """Build Notion page content markdown for the daily report."""
        top_jobs = report.top_jobs or []
        job_lines = "\n".join(
            f"| {j.get('priority_rank', i+1)} | [{j['title']}]({j.get('apply_url','#')}) "
            f"| {j['company']} | {j.get('composite_score', 0):.1f} | "
            f"{'Yes' if j.get('sponsorship_likely') else 'Maybe'} |"
            for i, j in enumerate(top_jobs)
        )
        gaps = "\n".join(f"- {g}" for g in (report.skill_gaps or [])[:5])
        topics = "\n".join(f"- {t}" for t in (report.interview_topics or [])[:5])

        return f"""## Daily Job Report — {report.report_date}

**{report.total_new_jobs} new opportunities analyzed**

### Top 10 Best-Fit Jobs

| # | Role | Company | Score | Sponsor |
|---|------|---------|-------|---------|
{job_lines}

### Skill Gaps to Address
{gaps or "_No gaps identified_"}

### Likely Interview Topics
{topics or "_No topics available_"}
"""

    def save_notion_page_id(
        self, db: Session, application_id: int, notion_page_id: str
    ) -> None:
        """Persist the returned Notion page ID to the application record."""
        from app.crud.application_crud import set_notion_page_id
        set_notion_page_id(db, application_id, notion_page_id)

    def save_report_notion_id(
        self, db: Session, report_id: int, notion_page_id: str
    ) -> None:
        """Persist Notion page ID to a daily report."""
        report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
        if report:
            report.notion_page_id = notion_page_id
            db.commit()
