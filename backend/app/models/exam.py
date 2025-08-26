"""
Exam models for LearnAid system.
Includes Exam, ExamQuestion, and ExamResult models for CIA management.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class ExamType(enum.Enum):
    """Types of exams in the system."""
    CIA1 = "cia1"
    CIA2 = "cia2" 
    CIA3 = "cia3"
    SEMESTER = "semester"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"


class Exam(Base):
    """
    Exam model for managing CIA and other assessments.
    Faculty can create exams and map questions to chapters.
    """
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    
    # Exam details
    exam_type = Column(String(20), nullable=False)  # CIA1, CIA2, etc.
    total_marks = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, default=180)  # 3 hours default
    
    # Scheduling
    exam_date = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    # Instructions and settings
    instructions = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)
    results_published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="exams")
    created_by = relationship("Faculty", back_populates="exams")
    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")
    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Exam(id={self.id}, title={self.title}, type={self.exam_type})>"


class ExamQuestion(Base):
    """
    Model for individual exam questions.
    Maps questions to specific chapters for performance analysis.
    """
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    
    # Question details
    question_number = Column(Integer, nullable=False)  # Q1, Q2, etc.
    question_text = Column(Text, nullable=True)  # Optional: store actual question
    max_marks = Column(Float, nullable=False)
    
    # Question metadata
    difficulty_level = Column(String(20), default="medium")  # easy, medium, hard
    question_type = Column(String(50), default="descriptive")  # mcq, descriptive, numerical
    
    # Learning outcome mapping
    learning_outcome = Column(String(255), nullable=True)
    bloom_taxonomy_level = Column(String(50), nullable=True)  # remember, understand, apply, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exam = relationship("Exam", back_populates="questions")
    chapter = relationship("Chapter", back_populates="exam_questions")
    student_responses = relationship("ExamResponse", back_populates="question")
    
    def __repr__(self):
        return f"<ExamQuestion(id={self.id}, exam_id={self.exam_id}, q_no={self.question_number})>"


class ExamResult(Base):
    """
    Model for storing student exam results.
    Contains overall exam performance for each student.
    """
    __tablename__ = "exam_results"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Overall performance
    total_marks_obtained = Column(Float, default=0.0)
    total_marks_possible = Column(Float, nullable=False)
    percentage = Column(Float, default=0.0)
    grade = Column(String(2), nullable=True)  # A+, A, B+, etc.
    
    # Exam metadata
    submission_time = Column(DateTime, nullable=True)
    time_taken_minutes = Column(Integer, nullable=True)
    
    # Status tracking
    is_submitted = Column(Boolean, default=False)
    is_graded = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exam = relationship("Exam", back_populates="results")
    student = relationship("Student", back_populates="exam_results")
    responses = relationship("ExamResponse", back_populates="exam_result", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ExamResult(id={self.id}, student_id={self.student_id}, percentage={self.percentage})>"


class ExamResponse(Base):
    """
    Model for storing individual question responses.
    Used for detailed question-wise performance analysis.
    """
    __tablename__ = "exam_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_result_id = Column(Integer, ForeignKey("exam_results.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("exam_questions.id"), nullable=False)
    
    # Response details
    marks_obtained = Column(Float, default=0.0)
    max_marks = Column(Float, nullable=False)
    
    # Response content (optional)
    student_answer = Column(Text, nullable=True)
    
    # Grading details
    is_correct = Column(Boolean, nullable=True)  # For MCQ
    partial_credit = Column(Float, nullable=True)  # For partial marking
    
    # Feedback
    feedback = Column(Text, nullable=True)  # Faculty feedback
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exam_result = relationship("ExamResult", back_populates="responses")
    question = relationship("ExamQuestion", back_populates="student_responses")
    
    def __repr__(self):
        return f"<ExamResponse(id={self.id}, question_id={self.question_id}, marks={self.marks_obtained})>"


class StudentPerformance(Base):
    """
    Model for tracking student performance by chapter.
    Auto-calculated from exam results and task completions.
    """
    __tablename__ = "student_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    
    # Performance metrics
    total_assessments = Column(Integer, default=0)  # Total questions/tasks in this chapter
    correct_answers = Column(Integer, default=0)
    total_marks_obtained = Column(Float, default=0.0)
    total_marks_possible = Column(Float, default=0.0)
    
    # Calculated performance
    accuracy_percentage = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)  # Weighted score
    
    # Performance categorization
    performance_level = Column(String(20), default="needs_improvement")  # excellent, good, average, needs_improvement
    weakness_areas = Column(Text, nullable=True)  # JSON list of specific weak topics
    
    # Progress tracking
    improvement_trend = Column(String(20), default="stable")  # improving, declining, stable
    last_assessment_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="performance_records")
    chapter = relationship("Chapter", back_populates="performance_records")
    
    def __repr__(self):
        return f"<StudentPerformance(student_id={self.student_id}, chapter_id={self.chapter_id}, level={self.performance_level})>"
