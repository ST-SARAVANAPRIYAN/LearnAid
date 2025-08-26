"""
Course models for LearnAid system.
Includes Course, Chapter, and enrollment models.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Course(Base):
    """
    Course model representing academic courses.
    Contains course information, chapters, and enrollments.
    """
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, nullable=False)  # e.g., "CS301"
    description = Column(Text, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    
    # Course details
    credits = Column(Integer, default=3)
    semester = Column(Integer, nullable=False)
    academic_year = Column(String(10), nullable=False)  # e.g., "2024-25"
    course_type = Column(String(50), default="core")  # core, elective, lab
    
    # Course settings
    is_active = Column(Boolean, default=True)
    max_students = Column(Integer, default=60)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="courses")
    faculty = relationship("Faculty", back_populates="courses")
    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    exams = relationship("Exam", back_populates="course")
    tasks = relationship("Task", back_populates="course")
    
    def __repr__(self):
        return f"<Course(id={self.id}, code={self.code}, name={self.name})>"


class Chapter(Base):
    """
    Chapter model for course content organization.
    Each chapter can have associated PDFs and learning materials.
    """
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Chapter details
    title = Column(String(255), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Content information
    pdf_file_path = Column(String(500), nullable=True)  # Path to uploaded PDF
    content_summary = Column(Text, nullable=True)  # AI-generated summary
    key_topics = Column(Text, nullable=True)  # JSON list of topics
    
    # Learning objectives
    learning_objectives = Column(Text, nullable=True)  # JSON list
    estimated_hours = Column(Float, default=2.0)  # Estimated study hours
    
    # Chapter status
    is_published = Column(Boolean, default=False)
    upload_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="chapters")
    exam_questions = relationship("ExamQuestion", back_populates="chapter")
    tasks = relationship("Task", back_populates="chapter")
    performance_records = relationship("StudentPerformance", back_populates="chapter")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, number={self.chapter_number}, title={self.title})>"


class CourseEnrollment(Base):
    """
    Model for student course enrollments.
    Tracks which students are enrolled in which courses.
    """
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Enrollment details
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="active")  # active, completed, dropped
    
    # Academic progress
    current_chapter = Column(Integer, default=1)
    completion_percentage = Column(Float, default=0.0)
    
    # Final grades (filled at end of semester)
    internal_marks = Column(Float, nullable=True)  # CIA marks
    external_marks = Column(Float, nullable=True)  # End semester marks
    total_marks = Column(Float, nullable=True)
    grade = Column(String(2), nullable=True)  # A+, A, B+, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<CourseEnrollment(student_id={self.student_id}, course_id={self.course_id}, status={self.status})>"
