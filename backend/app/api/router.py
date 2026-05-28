"""
Main router file that aggregates all API routes.
"""

from fastapi import APIRouter
from app.api import (
    auth_routes,
    dataset_routes,
    validation_routes,
    job_routes,
    application_routes,
    resume_routes,
    report_routes,
)

api_router = APIRouter(prefix="/api")

# Core data quality routes
api_router.include_router(auth_routes.router)
api_router.include_router(dataset_routes.router)
api_router.include_router(validation_routes.router)

# Job search automation routes
api_router.include_router(job_routes.router)
api_router.include_router(application_routes.router)
api_router.include_router(resume_routes.router)
api_router.include_router(report_routes.router)
