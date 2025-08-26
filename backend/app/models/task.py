"""
Task models for LearnAid system.
Includes Task, TaskQuestion, and TaskAttempt models for student assignments.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class TaskType(enum.Enum):
    """Types of tasks in the system."""
    DAILY = "daily"
    WEEKLY = "weekly"
    REMEDIAL = "remedial"  # For weak chapters
    SELF_STUDY = "self_study"
    ASSIGNMENT = "assignment"


class TaskDifficulty(enum.Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Task(Base):
    """
    Task model for student assignments and practice.
    Tasks can be auto-generated based on weak chapters or manually created.
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    
    # Task details
    description = Column(Text, nullable=True)
    task_type = Column(String(20), nullable=False)  # daily, weekly, remedial
    difficulty_level = Column(String(20), default="medium")
    
    # Content
    reading_material = Column(Text, nullable=True)  # Study material/instructions
    total_questions = Column(Integer, default=0)
    total_marks = Column(Float, default=0.0)
    
    # Timing and deadlines
    estimated_duration_minutes = Column(Integer, default=30)
    due_date = Column(DateTime, nullable=True)
    is_timed = Column(Boolean, default=False)
    time_limit_minutes = Column(Integer, nullable=True)
    
    # Assignment settings
    max_attempts = Column(Integer, default=3)
    show_answers_after = Column(String(20), default="submission")  # submission, deadline, never
    is_mandatory = Column(Boolean, default=True)
    
    # AI Generation metadata
    is_auto_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
    source_content = Column(Text, nullable=True)  # PDF content used for generation
    
    # Status
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="tasks")
    chapter = relationship("Chapter", back_populates="tasks")
    questions = relationship("TaskQuestion", back_populates="task", cascade="all, delete-orphan")
    attempts = relationship("TaskAttempt", back_populates="task")
    assignments = relationship("TaskAssignment", back_populates="task")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, type={self.task_type})>"


class TaskQuestion(Base):
    """
    Model for individual questions within a task.
    Supports MCQ, True/False, and short answer questions.
    """
    __tablename__ = "task_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    # Question details
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="mcq")  # mcq, true_false, short_answer
    marks = Column(Float, default=1.0)
    
    # MCQ options (JSON format)
    options = Column(JSON, nullable=True)  # {"A": "option1", "B": "option2", ...}
    correct_answer = Column(String(500), nullable=False)  # For MCQ: "A", for others: actual answer
    
    # Additional answer options for flexibility
    alternative_answers = Column(JSON, nullable=True)  # List of acceptable answers
    
    # Question metadata
    explanation = Column(Text, nullable=True)  # Explanation of correct answer
    difficulty_level = Column(String(20), default="medium")
    learning_objective = Column(String(255), nullable=True)
    
    # AI generation metadata
    is_auto_generated = Column(Boolean, default=False)
    source_text = Column(Text, nullable=True)  # Text from PDF that inspired this question
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="questions")
    responses = relationship("TaskResponse", back_populates="question")
    
    def __repr__(self):
        return f"<TaskQuestion(id={self.id}, task_id={self.task_id}, q_no={self.question_number})>"


class TaskAssignment(Base):
    """
    Model for assigning tasks to specific students or classes.
    Allows for personalized task distribution based on performance.
    """
    __tablename__ = "task_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Assignment details
    assigned_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="normal")  # high, normal, low
    
    # Assignment reason (for auto-generated tasks)
    assignment_reason = Column(String(100), nullable=True)  # "weak_chapter", "regular_practice"
    performance_threshold = Column(Float, nullable=True)  # Performance that triggered this assignment
    
    # Status tracking
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    
    # Notifications
    reminder_sent = Column(Boolean, default=False)
    reminder_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="assignments")
    student = relationship("Student")  # Simple relationship for now
    
    def __repr__(self):
        return f"<TaskAssignment(id={self.id}, task_id={self.task_id}, student_id={self.student_id})>"


class TaskAttempt(Base):
    """
    Model for tracking student attempts at tasks.
    Stores attempt details and responses.
    """
    __tablename__ = "task_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Attempt details
    attempt_number = Column(Integer, default=1)  # 1st, 2nd, 3rd attempt
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    time_taken_minutes = Column(Integer, nullable=True)
    
    # Results
    total_marks_obtained = Column(Float, default=0.0)
    total_marks_possible = Column(Float, nullable=False)
    percentage = Column(Float, default=0.0)
    
    # Performance metrics
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    unanswered = Column(Integer, default=0)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_submitted = Column(Boolean, default=False)
    is_graded = Column(Boolean, default=False)
    
    # Feedback and points
    feedback = Column(Text, nullable=True)  # Auto-generated or manual feedback
    points_earned = Column(Integer, default=0)  # Gamification points
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="attempts")
    student = relationship("Student", back_populates="task_attempts")
    responses = relationship("TaskResponse", back_populates="attempt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TaskAttempt(id={self.id}, task_id={self.task_id}, attempt={self.attempt_number})>"


class TaskResponse(Base):
    """
    Model for individual question responses within a task attempt.
    Stores student answers and grading information.
    """
    __tablename__ = "task_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("task_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("task_questions.id"), nullable=False)
    
    # Student response
    student_answer = Column(Text, nullable=True)  # The answer provided by student
    is_correct = Column(Boolean, nullable=True)  # True/False for correctness
    
    # Grading
    marks_obtained = Column(Float, default=0.0)
    max_marks = Column(Float, nullable=False)
    
    # Timing (optional)
    time_taken_seconds = Column(Integer, nullable=True)
    
    # Auto-grading metadata
    confidence_score = Column(Float, nullable=True)  # AI confidence in grading
    requires_manual_review = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempt = relationship("TaskAttempt", back_populates="responses")
    question = relationship("TaskQuestion", back_populates="responses")
    
    def __repr__(self):
        return f"<TaskResponse(id={self.id}, question_id={self.question_id}, correct={self.is_correct})>"
