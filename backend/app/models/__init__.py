"""
Models package for LearnAid.
Import all models to ensure they are registered with SQLAlchemy.
"""

# Import all models to register them with SQLAlchemy
from .user import User, UserRole, Department, Student, Faculty
from .course import Course, Chapter, CourseEnrollment
from .exam import (
    Exam, ExamType, ExamQuestion, ExamResult, 
    ExamResponse, StudentChapterPerformance
)
from .task import (
    Task, TaskType, TaskDifficulty, TaskQuestion,
    TaskAssignment, TaskAttempt, TaskResponse
)

# Make all models available for import
__all__ = [
    # User models
    "User", "UserRole", "Department", "Student", "Faculty",
    
    # Course models
    "Course", "Chapter", "CourseEnrollment",
    
    # Exam models
    "Exam", "ExamType", "ExamQuestion", "ExamResult", 
    "ExamResponse", "StudentChapterPerformance",
    
    # Task models
    "Task", "TaskType", "TaskDifficulty", "TaskQuestion",
    "TaskAssignment", "TaskAttempt", "TaskResponse"
]