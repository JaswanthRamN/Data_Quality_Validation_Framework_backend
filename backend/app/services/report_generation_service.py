"""
Daily report generation service — assembles the top-10 job summary and insights.
"""

import logging
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.crud.job_crud import get_top_jobs
from app.models.daily_report import DailyReport
from app.schemas.job_schema import JobSummary

logger = logging.getLogger(__name__)


class ReportGenerationService:
    """Builds and persists the daily job search summary."""

    def generate(self, db: Session, user_id: int, report_date: Optional[date] = None) -> DailyReport:
        target_date = report_date or date.today()

        # Check if report already exists for today
        existing = (
            db.query(DailyReport)
            .filter(DailyReport.user_id == user_id, DailyReport.report_date == target_date)
            .first()
        )

        top_jobs_orm = get_top_jobs(db, limit=10)
        top_jobs_data = []
        all_skill_gaps: list[str] = []
        all_interview_topics: list[str] = []

        for rank, job in enumerate(top_jobs_orm, start=1):
            analysis = job.raw_analysis or {}
            summary = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "is_remote": job.is_remote,
                "is_hybrid": job.is_hybrid,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "composite_score": job.composite_score,
                "ats_score": job.ats_score,
                "skill_match_pct": job.skill_match_pct,
                "sponsorship_likely": job.sponsorship_likely,
                "apply_url": job.apply_url,
                "role_category": job.role_category,
                "missing_keywords": job.missing_keywords,
                "why_it_fits": analysis.get("why_it_fits", ""),
                "priority_rank": rank,
            }
            top_jobs_data.append(summary)

            # Aggregate skill gaps and interview topics
            for gap in analysis.get("skill_gaps", []):
                if gap and gap not in all_skill_gaps:
                    all_skill_gaps.append(gap)
            for topic in analysis.get("interview_topics", []):
                if topic and topic not in all_interview_topics:
                    all_interview_topics.append(topic)

        # Build HTML report
        report_html = self._build_html(target_date, top_jobs_data, all_skill_gaps, all_interview_topics)

        if existing:
            existing.total_new_jobs = len(top_jobs_data)
            existing.top_jobs = top_jobs_data
            existing.skill_gaps = all_skill_gaps[:10]
            existing.interview_topics = all_interview_topics[:10]
            existing.report_html = report_html
            db.commit()
            db.refresh(existing)
            return existing

        report = DailyReport(
            user_id=user_id,
            report_date=target_date,
            total_new_jobs=len(top_jobs_data),
            top_jobs=top_jobs_data,
            skill_gaps=all_skill_gaps[:10],
            interview_topics=all_interview_topics[:10],
            report_html=report_html,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def _build_html(
        self,
        report_date: date,
        top_jobs: list,
        skill_gaps: list,
        interview_topics: list,
    ) -> str:
        rows = ""
        for job in top_jobs:
            salary = ""
            if job.get("salary_min") and job.get("salary_max"):
                salary = f"${job['salary_min']:,.0f}–${job['salary_max']:,.0f}"
            elif job.get("salary_min"):
                salary = f"${job['salary_min']:,.0f}+"
            location_tag = "Remote" if job.get("is_remote") else ("Hybrid" if job.get("is_hybrid") else job.get("location", ""))
            rows += f"""
            <tr>
              <td>{job['priority_rank']}</td>
              <td><a href="{job.get('apply_url','#')}">{job['title']}</a></td>
              <td>{job['company']}</td>
              <td>{location_tag}</td>
              <td>{salary or 'N/A'}</td>
              <td>{job.get('composite_score', 0):.1f}</td>
              <td>{job.get('ats_score', 0):.1f}%</td>
              <td>{'Yes' if job.get('sponsorship_likely') else 'Maybe'}</td>
            </tr>"""

        gaps_html = "".join(f"<li>{g}</li>" for g in skill_gaps[:5])
        topics_html = "".join(f"<li>{t}</li>" for t in interview_topics[:5])

        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Job Report {report_date}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 20px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #4F46E5; color: white; }}
  tr:nth-child(even) {{ background: #f9f9f9; }}
  h2 {{ color: #4F46E5; }}
</style>
</head>
<body>
<h1>Daily Job Report — {report_date.strftime('%B %d, %Y')}</h1>
<h2>Top 10 Best-Fit Jobs</h2>
<table>
  <tr><th>#</th><th>Role</th><th>Company</th><th>Location</th><th>Salary</th>
  <th>Score</th><th>ATS%</th><th>Sponsor</th></tr>
  {rows}
</table>
<h2>Skill Gaps to Address</h2><ul>{gaps_html}</ul>
<h2>Likely Interview Topics</h2><ul>{topics_html}</ul>
</body></html>"""
