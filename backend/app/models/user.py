"""
User models for LearnAid system.
Includes base User class and specialized Student/Faculty models.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import Base
from datetime import datetime
import enum


class UserRole(enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    FACULTY = "faculty" 
    STUDENT = "student"


class User(Base):
    """
    Base User model for all system users.
    Contains common fields shared by all user types.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile fields
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(String(500), nullable=True)  # URL or file path
    
    # Relationships based on role
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    faculty_profile = relationship("Faculty", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Department(Base):
    """Department model for organizing courses and faculty."""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)  # e.g., "CSE", "ECE"
    description = Column(Text, nullable=True)
    head_of_department = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = relationship("Course", back_populates="department")
    faculty_members = relationship("Faculty", back_populates="department")
    students = relationship("Student", back_populates="department")
    
    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name}, code={self.code})>"


class Student(Base):
    """
    Student profile extending base User.
    Contains student-specific information and relationships.
    """
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Student-specific fields
    student_id = Column(String(20), unique=True, nullable=False)  # e.g., "CS21B001"
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    class_name = Column(String(100), nullable=False)  # e.g., "IV CSE A"
    semester = Column(Integer, nullable=False)
    academic_year = Column(String(10), nullable=False)  # e.g., "2024-25"
    
    # Academic information
    cgpa = Column(String(5), nullable=True)
    batch_year = Column(Integer, nullable=False)  # Year of joining
    
    # Gamification fields
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    badges_earned = Column(Text, nullable=True)  # JSON string of badges
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    department = relationship("Department", back_populates="students")
    enrollments = relationship("CourseEnrollment", back_populates="student")
    exam_results = relationship("ExamResult", back_populates="student")
    task_attempts = relationship("TaskAttempt", back_populates="student")
    performance_records = relationship("StudentPerformance", back_populates="student")
    
    def __repr__(self):
        return f"<Student(id={self.id}, student_id={self.student_id}, class={self.class_name})>"


class Faculty(Base):
    """
    Faculty profile extending base User.
    Contains faculty-specific information and relationships.
    """
    __tablename__ = "faculty"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Faculty-specific fields
    employee_id = Column(String(20), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation = Column(String(100), nullable=False)  # e.g., "Assistant Professor"
    qualification = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    experience_years = Column(Integer, default=0)
    
    # Contact and office information
    office_location = Column(String(100), nullable=True)
    office_hours = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department", back_populates="faculty_members")
    courses = relationship("Course", back_populates="faculty")
    exams = relationship("Exam", back_populates="created_by")
    
    def __repr__(self):
        return f"<Faculty(id={self.id}, employee_id={self.employee_id}, designation={self.designation})>"
