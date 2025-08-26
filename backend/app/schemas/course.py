"""
Course and Exam schemas for LearnAid.
Handles course creation, chapter management, exam creation, and performance tracking.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


# Course Management Schemas
class ChapterBase(BaseModel):
    """Base schema for chapter information."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content: Optional[str] = Field(None, max_length=10000)
    order_index: int = Field(..., ge=1, description="Chapter order in course")
    estimated_hours: Optional[float] = Field(None, ge=0.1, le=100)


class ChapterCreate(ChapterBase):
    """Schema for creating a new chapter."""
    pass


class ChapterUpdate(BaseModel):
    """Schema for updating chapter information."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content: Optional[str] = Field(None, max_length=10000)
    order_index: Optional[int] = Field(None, ge=1)
    estimated_hours: Optional[float] = Field(None, ge=0.1, le=100)
    is_active: Optional[bool] = None


class ChapterResponse(ChapterBase):
    """Schema for chapter response."""
    id: int
    course_id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    upload_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    """Base schema for course information."""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=2, max_length=10)
    description: Optional[str] = Field(None, max_length=2000)
    credits: int = Field(..., ge=1, le=10)
    semester: int = Field(..., ge=1, le=8)
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Format: YYYY-YY")


class CourseCreate(CourseBase):
    """Schema for creating a new course."""
    department_id: int
    chapters: Optional[List[ChapterCreate]] = []


class CourseUpdate(BaseModel):
    """Schema for updating course information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    description: Optional[str] = Field(None, max_length=2000)
    credits: Optional[int] = Field(None, ge=1, le=10)
    semester: Optional[int] = Field(None, ge=1, le=8)
    academic_year: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")
    is_active: Optional[bool] = None


class CourseResponse(CourseBase):
    """Schema for course response."""
    id: int
    department_id: int
    faculty_id: int
    department: Optional[Dict[str, Any]] = None
    faculty: Optional[Dict[str, Any]] = None
    chapters: List[ChapterResponse] = []
    total_chapters: int = 0
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Exam Management Schemas
class ExamType(str, Enum):
    """Enum for exam types."""
    CIA1 = "CIA1"
    CIA2 = "CIA2"
    CIA3 = "CIA3"
    END_SEM = "END_SEM"
    QUIZ = "QUIZ"
    ASSIGNMENT = "ASSIGNMENT"


class QuestionBase(BaseModel):
    """Base schema for exam question."""
    question_number: int = Field(..., ge=1, le=100)
    max_marks: float = Field(..., ge=0.5, le=100)
    chapter_id: int
    question_text: Optional[str] = Field(None, max_length=2000)
    expected_answer: Optional[str] = Field(None, max_length=5000)


class QuestionCreate(QuestionBase):
    """Schema for creating exam question."""
    pass


class QuestionUpdate(BaseModel):
    """Schema for updating exam question."""
    max_marks: Optional[float] = Field(None, ge=0.5, le=100)
    chapter_id: Optional[int] = None
    question_text: Optional[str] = Field(None, max_length=2000)
    expected_answer: Optional[str] = Field(None, max_length=5000)


class QuestionResponse(QuestionBase):
    """Schema for question response."""
    id: int
    exam_id: int
    chapter: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExamBase(BaseModel):
    """Base schema for exam information."""
    name: str = Field(..., min_length=1, max_length=200)
    exam_type: ExamType
    exam_date: date
    duration_minutes: int = Field(..., ge=30, le=300, description="Exam duration in minutes")
    total_marks: float = Field(..., ge=1, le=500)
    instructions: Optional[str] = Field(None, max_length=2000)


class ExamCreate(ExamBase):
    """Schema for creating a new exam."""
    course_id: int
    questions: List[QuestionCreate] = Field(..., min_items=1, max_items=100)

    @validator('questions')
    def validate_questions_total_marks(cls, questions, values):
        """Validate that total marks of questions match exam total marks."""
        if 'total_marks' in values:
            total_question_marks = sum(q.max_marks for q in questions)
            if abs(total_question_marks - values['total_marks']) > 0.01:
                raise ValueError(f"Total marks of questions ({total_question_marks}) must equal exam total marks ({values['total_marks']})")
        return questions

    @validator('questions')
    def validate_question_numbers(cls, questions):
        """Validate that question numbers are unique and sequential."""
        question_numbers = [q.question_number for q in questions]
        expected_numbers = list(range(1, len(questions) + 1))
        if sorted(question_numbers) != expected_numbers:
            raise ValueError("Question numbers must be unique and sequential starting from 1")
        return questions


class ExamUpdate(BaseModel):
    """Schema for updating exam information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    exam_date: Optional[date] = None
    duration_minutes: Optional[int] = Field(None, ge=30, le=300)
    instructions: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None


class ExamResponse(ExamBase):
    """Schema for exam response."""
    id: int
    course_id: int
    faculty_id: int
    course: Optional[Dict[str, Any]] = None
    faculty: Optional[Dict[str, Any]] = None
    questions: List[QuestionResponse] = []
    total_questions: int = 0
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Student Response and Performance Schemas
class StudentResponseBase(BaseModel):
    """Base schema for student exam response."""
    question_id: int
    student_id: int
    marks_obtained: float = Field(..., ge=0, description="Marks obtained by student")
    answer_text: Optional[str] = Field(None, max_length=5000)
    is_correct: Optional[bool] = None
    feedback: Optional[str] = Field(None, max_length=1000)


class StudentResponseCreate(StudentResponseBase):
    """Schema for creating student response."""
    pass


class StudentResponseBulkCreate(BaseModel):
    """Schema for bulk creating student responses."""
    exam_id: int
    responses: List[StudentResponseCreate] = Field(..., min_items=1)


class StudentResponseUpdate(BaseModel):
    """Schema for updating student response."""
    marks_obtained: Optional[float] = Field(None, ge=0)
    answer_text: Optional[str] = Field(None, max_length=5000)
    is_correct: Optional[bool] = None
    feedback: Optional[str] = Field(None, max_length=1000)


class StudentResponseResponse(StudentResponseBase):
    """Schema for student response response."""
    id: int
    exam_id: int
    question: Optional[Dict[str, Any]] = None
    student: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChapterPerformance(BaseModel):
    """Schema for chapter-wise performance."""
    chapter_id: int
    chapter_name: str
    total_marks: float
    obtained_marks: float
    percentage: float
    questions_count: int


class StudentExamResult(BaseModel):
    """Schema for student exam result."""
    exam_id: int
    student_id: int
    student_name: str
    student_id_number: str
    total_marks: float
    obtained_marks: float
    percentage: float
    grade: Optional[str] = None
    chapter_performance: List[ChapterPerformance] = []
    exam_date: date
    submitted_at: Optional[datetime] = None


class ExamResultsSummary(BaseModel):
    """Schema for exam results summary."""
    exam_id: int
    exam_name: str
    exam_type: ExamType
    total_students: int
    submitted_count: int
    average_marks: float
    highest_marks: float
    lowest_marks: float
    pass_percentage: float
    student_results: List[StudentExamResult] = []


# Analytics Schemas
class FacultyDashboardStats(BaseModel):
    """Schema for faculty dashboard statistics."""
    total_courses: int
    active_courses: int
    total_students: int
    total_exams: int
    recent_exams: int
    pending_evaluations: int


class CourseAnalytics(BaseModel):
    """Schema for course analytics."""
    course_id: int
    course_name: str
    enrolled_students: int
    completed_exams: int
    average_performance: float
    weak_chapters: List[Dict[str, Any]] = []
    strong_chapters: List[Dict[str, Any]] = []


class FacultyDashboard(BaseModel):
    """Schema for complete faculty dashboard."""
    stats: FacultyDashboardStats
    recent_courses: List[CourseResponse] = []
    recent_exams: List[ExamResponse] = []
    course_analytics: List[CourseAnalytics] = []
    pending_tasks: List[str] = []
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
