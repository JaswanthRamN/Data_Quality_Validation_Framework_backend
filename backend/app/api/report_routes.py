"""
Daily report API routes — retrieve job search summary reports.
"""

import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.models.user import User
from app.models.daily_report import DailyReport
from app.schemas.report_schema import DailyReportResponse, DailyReportSummary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/latest", response_model=DailyReportResponse)
def get_latest_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent daily job report for the current user."""
    report = (
        db.query(DailyReport)
        .filter(DailyReport.user_id == current_user.id)
        .order_by(DailyReport.report_date.desc())
        .first()
    )
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No reports yet. Trigger one via POST /api/reports/trigger",
        )
    return report


@router.get("/", response_model=list[DailyReportSummary])
def list_reports(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List daily reports with optional date range filter."""
    query = db.query(DailyReport).filter(DailyReport.user_id == current_user.id)
    if start_date:
        query = query.filter(DailyReport.report_date >= start_date)
    if end_date:
        query = query.filter(DailyReport.report_date <= end_date)
    reports = query.order_by(DailyReport.report_date.desc()).offset(skip).limit(limit).all()

    return [
        DailyReportSummary(
            id=r.id,
            report_date=r.report_date,
            total_new_jobs=r.total_new_jobs,
            top_score=max(
                (j.get("composite_score", 0) for j in (r.top_jobs or [])), default=None
            ),
            notion_page_id=r.notion_page_id,
            created_at=r.created_at,
        )
        for r in reports
    ]


@router.post("/trigger", summary="Generate a daily report on demand (admin)")
def trigger_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Manually generate the daily report for the current user."""
    from app.services.report_generation_service import ReportGenerationService
    service = ReportGenerationService()
    report = service.generate(db, current_user.id)
    return {
        "status": "generated",
        "report_id": report.id,
        "report_date": str(report.report_date),
        "total_jobs": report.total_new_jobs,
    }
