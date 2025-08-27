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
    FREQUENT_ASSESSMENT = "frequent_assessment"  # Main type for poor-performing students
    DAILY = "daily"
    BI_DAILY = "bi_daily"  # Every 2 days
    WEEKLY = "weekly"
    REMEDIAL = "remedial"  # For students who performed poorly in CIA exams
    PRACTICE = "practice"  # Regular practice tasks
    ASSIGNMENT = "assignment"


class TaskDifficulty(enum.Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Task(Base):
    """
    Task model for frequent assessments and student improvement.
    Tasks are assigned to students who performed poorly in specific chapters during CIA exams.
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("faculty.id"), nullable=True)  # Can be auto-generated
    
    # Task details
    description = Column(Text, nullable=True)
    task_type = Column(String(30), nullable=False)  # frequent_assessment, daily, bi_daily, remedial
    difficulty_level = Column(String(20), default="medium")
    
    # Target audience (students who need improvement)
    target_performance_threshold = Column(Float, default=50.0)  # Students below this % get this task
    target_student_count = Column(Integer, default=0)  # Number of students this task is assigned to
    
    # Content and Study Material
    study_material = Column(Text, nullable=True)  # Reading material before test
    study_time_minutes = Column(Integer, default=15)  # Time to study before test
    reading_material = Column(Text, nullable=True)  # Additional reading content
    
    # Test Configuration
    total_questions = Column(Integer, default=0)
    total_marks = Column(Float, default=0.0)
    
    # Timing and Scheduling
    estimated_duration_minutes = Column(Integer, default=30)  # Test duration
    due_date = Column(DateTime, nullable=True)
    is_timed = Column(Boolean, default=True)  # Frequent assessments should be timed
    time_limit_minutes = Column(Integer, default=20)  # Test time limit
    
    # Assignment settings for frequent assessments
    max_attempts = Column(Integer, default=2)  # Limited attempts for assessments
    show_answers_after = Column(String(20), default="submission")  # Show answers after submission
    is_mandatory = Column(Boolean, default=True)  # Frequent assessments are mandatory
    
    # Auto-generation for LLM-based tasks
    is_auto_generated = Column(Boolean, default=False)
    llm_generation_prompt = Column(Text, nullable=True)  # Prompt used for LLM generation
    source_pdf_content = Column(Text, nullable=True)  # PDF content used for generation
    llm_model_used = Column(String(100), nullable=True)  # Which LLM model was used
    
    # Assignment tracking
    auto_assign_to_poor_performers = Column(Boolean, default=False)  # Auto-assign to students with low performance
    performance_improvement_target = Column(Float, default=70.0)  # Target improvement percentage
    
    # Status
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="tasks")
    chapter = relationship("Chapter", back_populates="tasks")
    created_by = relationship("Faculty", back_populates="tasks")
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
    Model for assigning tasks to specific students based on their poor performance in chapters.
    Tracks which students get which tasks and why.
    """
    __tablename__ = "task_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Assignment details and reasoning
    assigned_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="normal")  # high, normal, low
    
    # Assignment reason - why this student got this task
    assignment_reason = Column(String(200), nullable=True)  # "Poor CIA1 performance in Chapter 3 (35%)"
    triggering_exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)  # Which exam triggered this assignment
    student_chapter_performance = Column(Float, nullable=True)  # The poor performance % that triggered assignment
    target_improvement_percentage = Column(Float, default=70.0)  # Target performance after this task
    
    # Assignment frequency settings
    is_recurring = Column(Boolean, default=False)  # For daily/bi-daily assignments
    recurrence_pattern = Column(String(50), nullable=True)  # "daily", "every_2_days", "weekly"
    next_assignment_date = Column(DateTime, nullable=True)  # When to assign next similar task
    
    # Status tracking
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    performance_after_completion = Column(Float, nullable=True)  # Performance improvement measurement
    
    # Notifications and reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_count = Column(Integer, default=0)
    last_reminder_date = Column(DateTime, nullable=True)
    
    # Auto-assignment metadata
    is_auto_assigned = Column(Boolean, default=False)  # Was this auto-assigned by system?
    auto_assignment_algorithm = Column(String(100), nullable=True)  # Which algorithm assigned this
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="assignments")
    student = relationship("Student", back_populates="task_assignments")
    triggering_exam = relationship("Exam")  # Which exam caused this assignment
    
    def __repr__(self):
        return f"<TaskAssignment(id={self.id}, task_id={self.task_id}, student_id={self.student_id}, reason={self.assignment_reason})>"


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
