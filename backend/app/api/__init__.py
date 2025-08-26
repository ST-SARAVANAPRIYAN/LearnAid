"""
API package initialization.
Main API package containing versioned API routes.
"""

from .v1 import auth, admin, faculty, student

__all__ = ["auth", "admin", "faculty", "student"]
