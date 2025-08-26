"""
Schemas package for LearnAid API.
Contains Pydantic models for request/response validation.
"""

# Import all schemas
from .user import (
    UserRole, UserBase, UserCreate, UserUpdate, UserInDB, UserResponse,
    DepartmentBase, DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    StudentBase, StudentCreate, StudentUpdate, StudentResponse,
    FacultyBase, FacultyCreate, FacultyUpdate, FacultyResponse,
    Token, TokenData, LoginRequest, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
    BulkStudentCreate, BulkFacultyCreate,
    UserStats, DashboardSummary
)

from .course import (
    CourseBase, CourseCreate, CourseUpdate, CourseResponse,
    ChapterBase, ChapterCreate, ChapterUpdate, ChapterResponse,
    ChapterFileUpload,
    CourseEnrollmentBase, CourseEnrollmentCreate, CourseEnrollmentUpdate, CourseEnrollmentResponse,
    BulkEnrollmentCreate, BulkEnrollmentByClass,
    CourseAnalytics, ChapterAnalytics, CourseProgressSummary,
    CourseSearchFilters, CourseListResponse
)

# Make all schemas available for import
__all__ = [
    # User schemas
    "UserRole", "UserBase", "UserCreate", "UserUpdate", "UserInDB", "UserResponse",
    "DepartmentBase", "DepartmentCreate", "DepartmentUpdate", "DepartmentResponse",
    "StudentBase", "StudentCreate", "StudentUpdate", "StudentResponse",
    "FacultyBase", "FacultyCreate", "FacultyUpdate", "FacultyResponse",
    "Token", "TokenData", "LoginRequest", "RefreshTokenRequest",
    "PasswordResetRequest", "PasswordResetConfirm", "ChangePasswordRequest",
    "BulkStudentCreate", "BulkFacultyCreate",
    "UserStats", "DashboardSummary",
    
    # Course schemas
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse",
    "ChapterBase", "ChapterCreate", "ChapterUpdate", "ChapterResponse",
    "ChapterFileUpload",
    "CourseEnrollmentBase", "CourseEnrollmentCreate", "CourseEnrollmentUpdate", "CourseEnrollmentResponse",
    "BulkEnrollmentCreate", "BulkEnrollmentByClass",
    "CourseAnalytics", "ChapterAnalytics", "CourseProgressSummary",
    "CourseSearchFilters", "CourseListResponse"
]