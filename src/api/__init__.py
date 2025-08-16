"""
API layer for ML project.
Provides REST API endpoints for analytics and scheduler.
"""

from .routes import analytics, scheduler

__all__ = [
    "analytics",
    "scheduler"
]