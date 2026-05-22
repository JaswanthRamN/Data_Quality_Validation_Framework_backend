"""
Main router file that aggregates all API routes.
"""

from fastapi import APIRouter
from app.api import auth_routes, dataset_routes, validation_routes

api_router = APIRouter(prefix="/api")

# Include authentication routes
api_router.include_router(auth_routes.router)

# Include secured API routes
api_router.include_router(dataset_routes.router)
api_router.include_router(validation_routes.router)
