"""
Middleware setup for the FastAPI application.
Includes request logging, error handling, and performance monitoring.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from time import time
from app.utils.logger import logger


def setup_middleware(app: FastAPI):
    """Setup all middleware for the application."""
    
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        """Log all incoming requests and their responses."""
        request_id = request.headers.get("X-Request-ID", str(time()))
        request.state.request_id = request_id
        
        # Log request
        logger.debug(f"[{request_id}] {request.method} {request.url.path}")
        
        # Measure execution time
        start_time = time()
        response = await call_next(request)
        process_time = time() - start_time
        
        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.debug(
            f"[{request_id}] Completed: {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.3f}s"
        )
        
        return response
