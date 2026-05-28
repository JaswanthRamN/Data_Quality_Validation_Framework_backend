"""
Gmail outreach service — prepares email draft data for the Gmail MCP tool.

NOTE: Actual MCP tool calls (create_draft, create_label, label_thread) must be
issued from the Claude agent context. This service provides data preparation.
"""

import logging
from typing import Optional
from app.models.job import Job
from app.models.job_application import JobApplication

logger = logging.getLogger(__name__)


class GmailOutreachService:
    """
    Prepares recruiter outreach email drafts and follow-up label data.
    The caller is responsible for executing the MCP tool calls with the returned payloads.
    """

    def build_outreach_draft(
        self,
        job: Job,
        outreach_message: str,
        recruiter_email: Optional[str] = None,
    ) -> dict:
        """
        Returns a dict with subject and body for the Gmail create_draft MCP call.
        The caller passes this to mcp__f620c10c__create_draft.
        """
        subject = f"Data Analytics Role Inquiry — {job.title} at {job.company}"
        body = f"{outreach_message}\n\nRole: {job.title}\nCompany: {job.company}\nApply: {job.apply_url or 'N/A'}"
        return {
            "to": recruiter_email or "",
            "subject": subject,
            "body": body,
        }

    def build_follow_up_draft(
        self,
        job: Job,
        application: JobApplication,
        days_since_applied: int = 7,
    ) -> dict:
        """Returns follow-up email draft payload."""
        subject = f"Follow-Up: {job.title} Application — {job.company}"
        body = (
            f"Hi,\n\n"
            f"I wanted to follow up on my application for the {job.title} role at {job.company} "
            f"submitted {days_since_applied} days ago. I remain very interested in this opportunity "
            f"and believe my background in SQL, Python, and data analytics would be a strong match "
            f"for your team's needs.\n\n"
            f"Would you be available for a brief call this week?\n\n"
            f"Best regards"
        )
        return {"to": "", "subject": subject, "body": body}

    def build_label_name(self, company: str) -> str:
        """Returns a consistent Gmail label name for a company's job application thread."""
        return f"JobSearch/{company.replace(' ', '_')}"
