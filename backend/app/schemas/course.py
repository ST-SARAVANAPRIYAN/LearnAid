"""
Course schemas for LearnAid API.
Pydantic models for course-related requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# Base course schemas
class CourseBase(BaseModel):
    """Base course schema."""
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=3, max_length=20)
    description: Optional[str] = None
    credits: int = Field(default=3, ge=1, le=6)
    semester: int = Field(..., ge=1, le=8)
    academic_year: str = Field(..., regex=r'^\d{4}-\d{2}$')
    course_type: str = Field(default="core")  # core, elective, lab
    max_students: int = Field(default=60, ge=1, le=200)


class CourseCreate(CourseBase):
    """Schema for creating a course."""
    department_id: int
    faculty_id: int


class CourseUpdate(BaseModel):
    """Schema for updating course information."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=6)
    course_type: Optional[str] = None
    max_students: Optional[int] = Field(None, ge=1, le=200)
    is_active: Optional[bool] = None


class CourseResponse(CourseBase):
    """Course schema for API responses."""
    id: int
    department_id: int
    faculty_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Related data
    faculty_name: Optional[str] = None
    department_name: Optional[str] = None
    enrolled_students: int = 0
    total_chapters: int = 0
    
    class Config:
        from_attributes = True


# Chapter schemas
class ChapterBase(BaseModel):
    """Base chapter schema."""
    title: str = Field(..., min_length=2, max_length=255)
    chapter_number: int = Field(..., ge=1)
    description: Optional[str] = None
    learning_objectives: Optional[str] = None
    estimated_hours: float = Field(default=2.0, ge=0.5, le=10.0)


class ChapterCreate(ChapterBase):
    """Schema for creating a chapter."""
    course_id: int


class ChapterUpdate(BaseModel):
    """Schema for updating chapter information."""
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    learning_objectives: Optional[str] = None
    estimated_hours: Optional[float] = Field(None, ge=0.5, le=10.0)
    is_published: Optional[bool] = None


class ChapterResponse(ChapterBase):
    """Chapter schema for API responses."""
    id: int
    course_id: int
    pdf_file_path: Optional[str] = None
    content_summary: Optional[str] = None
    key_topics: Optional[str] = None
    is_published: bool
    upload_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Chapter file upload schema
class ChapterFileUpload(BaseModel):
    """Schema for chapter file upload response."""
    chapter_id: int
    filename: str
    file_path: str
    file_size: int
    upload_date: datetime
    content_summary: Optional[str] = None
    key_topics: Optional[List[str]] = None


# Course enrollment schemas
class CourseEnrollmentBase(BaseModel):
    """Base course enrollment schema."""
    status: str = Field(default="active")  # active, completed, dropped


class CourseEnrollmentCreate(BaseModel):
    """Schema for enrolling a student in a course."""
    student_id: int
    course_id: int


class CourseEnrollmentUpdate(BaseModel):
    """Schema for updating enrollment status."""
    status: Optional[str] = None
    current_chapter: Optional[int] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    internal_marks: Optional[float] = None
    external_marks: Optional[float] = None
    total_marks: Optional[float] = None
    grade: Optional[str] = Field(None, max_length=2)


class CourseEnrollmentResponse(CourseEnrollmentBase):
    """Course enrollment schema for API responses."""
    id: int
    student_id: int
    course_id: int
    enrollment_date: datetime
    current_chapter: int
    completion_percentage: float
    internal_marks: Optional[float] = None
    external_marks: Optional[float] = None
    total_marks: Optional[float] = None
    grade: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    student_name: Optional[str] = None
    student_id_number: Optional[str] = None
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    
    class Config:
        from_attributes = True


# Bulk enrollment schemas
class BulkEnrollmentCreate(BaseModel):
    """Schema for bulk student enrollment."""
    student_ids: List[int]
    course_id: int


class BulkEnrollmentByClass(BaseModel):
    """Schema for bulk enrollment by class."""
    class_name: str
    course_id: int
    department_id: Optional[int] = None


# Course analytics schemas
class CourseAnalytics(BaseModel):
    """Course analytics schema."""
    course_id: int
    total_enrolled: int
    active_students: int
    completion_rate: float
    average_performance: float
    
    # Chapter-wise data
    chapters_completed: int
    total_chapters: int
    
    # Engagement metrics
    active_last_week: int
    tasks_completed: int
    average_task_score: float


class ChapterAnalytics(BaseModel):
    """Chapter analytics schema."""
    chapter_id: int
    chapter_title: str
    
    # Student progress
    students_completed: int
    students_in_progress: int
    average_completion_time: float
    
    # Performance metrics
    average_performance: float
    tasks_generated: int
    total_task_attempts: int


class CourseProgressSummary(BaseModel):
    """Course progress summary for students."""
    course_id: int
    course_name: str
    course_code: str
    
    # Progress metrics
    current_chapter: int
    total_chapters: int
    completion_percentage: float
    
    # Performance
    internal_marks: Optional[float] = None
    current_grade: Optional[str] = None
    performance_trend: str  # improving, declining, stable
    
    # Tasks and activities
    pending_tasks: int
    completed_tasks: int
    total_points: int


# Course search and filter schemas
class CourseSearchFilters(BaseModel):
    """Schema for course search and filtering."""
    department_id: Optional[int] = None
    faculty_id: Optional[int] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    course_type: Optional[str] = None
    is_active: Optional[bool] = True
    
    # Search parameters
    search_query: Optional[str] = None  # Search in name, code, description
    
    # Pagination
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class CourseListResponse(BaseModel):
    """Response schema for course list with pagination."""
    courses: List[CourseResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
