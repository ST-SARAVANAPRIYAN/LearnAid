"""
API v1 package initialization.
Imports and registers all API routers.
"""

from . import auth, admin, faculty, student

__all__ = ["auth", "admin", "faculty", "student"]
