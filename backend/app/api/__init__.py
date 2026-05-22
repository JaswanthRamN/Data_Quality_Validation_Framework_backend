"""
API routes package initialization.
Exports route modules for easy importing.
"""

from app.api import auth_routes, dataset_routes, validation_routes

__all__ = [
    "auth_routes",
    "dataset_routes",
    "validation_routes",
]
