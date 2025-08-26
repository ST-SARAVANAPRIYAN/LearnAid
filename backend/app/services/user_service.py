"""
User service layer for LearnAid.
Contains business logic for user management operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.user import User, UserRole, Department, Student, Faculty
from app.schemas.user import (
    UserCreate, UserUpdate, StudentCreate, FacultyCreate,
    DepartmentCreate, DepartmentUpdate
)
from app.core.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        user = self.db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
        
        if user and verify_password(password, user.hashed_password):
            return user
        return None
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            or_(User.email == user_data.email, User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            phone_number=user_data.phone_number,
            profile_picture=user_data.profile_picture
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created user: {user.username}")
        return user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Updated user: {user.username}")
        return user
    
    def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Deactivated user: {user.username}")
        return user
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        return True


class DepartmentService:
    """Service class for department-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_departments(self, skip: int = 0, limit: int = 100) -> List[Department]:
        """Get all departments."""
        return self.db.query(Department).offset(skip).limit(limit).all()
    
    def get_department_by_id(self, department_id: int) -> Optional[Department]:
        """Get department by ID."""
        return self.db.query(Department).filter(Department.id == department_id).first()
    
    def get_department_by_code(self, code: str) -> Optional[Department]:
        """Get department by code."""
        return self.db.query(Department).filter(Department.code == code).first()
    
    def create_department(self, dept_data: DepartmentCreate) -> Department:
        """Create a new department."""
        # Check if department already exists
        existing_dept = self.db.query(Department).filter(
            or_(Department.name == dept_data.name, Department.code == dept_data.code)
        ).first()
        
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with this name or code already exists"
            )
        
        department = Department(**dept_data.dict())
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        
        logger.info(f"Created department: {department.name}")
        return department
    
    def update_department(self, department_id: int, dept_data: DepartmentUpdate) -> Department:
        """Update department information."""
        department = self.get_department_by_id(department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Update fields
        update_data = dept_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(department, field, value)
        
        self.db.commit()
        self.db.refresh(department)
        
        logger.info(f"Updated department: {department.name}")
        return department


class StudentService:
    """Service class for student-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Get student by ID."""
        return self.db.query(Student).filter(Student.id == student_id).first()
    
    def get_student_by_student_id(self, student_id: str) -> Optional[Student]:
        """Get student by student ID."""
        return self.db.query(Student).filter(Student.student_id == student_id).first()
    
    def get_students_by_class(self, class_name: str, department_id: Optional[int] = None) -> List[Student]:
        """Get students by class."""
        query = self.db.query(Student).filter(Student.class_name == class_name)
        if department_id:
            query = query.filter(Student.department_id == department_id)
        return query.all()
    
    def create_student(self, student_data: StudentCreate) -> Student:
        """Create a new student with user account."""
        # Check if student ID already exists
        existing_student = self.get_student_by_student_id(student_data.student_id)
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this ID already exists"
            )
        
        # Create user account first
        user_data = UserCreate(
            email=student_data.email,
            username=student_data.username,
            full_name=student_data.full_name,
            password=student_data.password,
            role=UserRole.STUDENT,
            phone_number=student_data.phone_number
        )
        user = self.user_service.create_user(user_data)
        
        # Create student profile
        student = Student(
            user_id=user.id,
            student_id=student_data.student_id,
            department_id=student_data.department_id,
            class_name=student_data.class_name,
            semester=student_data.semester,
            academic_year=student_data.academic_year,
            cgpa=student_data.cgpa,
            batch_year=student_data.batch_year
        )
        
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        
        logger.info(f"Created student: {student.student_id}")
        return student


class FacultyService:
    """Service class for faculty-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    def get_faculty_by_id(self, faculty_id: int) -> Optional[Faculty]:
        """Get faculty by ID."""
        return self.db.query(Faculty).filter(Faculty.id == faculty_id).first()
    
    def get_faculty_by_employee_id(self, employee_id: str) -> Optional[Faculty]:
        """Get faculty by employee ID."""
        return self.db.query(Faculty).filter(Faculty.employee_id == employee_id).first()
    
    def get_faculty_by_department(self, department_id: int) -> List[Faculty]:
        """Get faculty by department."""
        return self.db.query(Faculty).filter(Faculty.department_id == department_id).all()
    
    def create_faculty(self, faculty_data: FacultyCreate) -> Faculty:
        """Create a new faculty with user account."""
        # Check if employee ID already exists
        existing_faculty = self.get_faculty_by_employee_id(faculty_data.employee_id)
        if existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Faculty with this employee ID already exists"
            )
        
        # Create user account first
        user_data = UserCreate(
            email=faculty_data.email,
            username=faculty_data.username,
            full_name=faculty_data.full_name,
            password=faculty_data.password,
            role=UserRole.FACULTY,
            phone_number=faculty_data.phone_number
        )
        user = self.user_service.create_user(user_data)
        
        # Create faculty profile
        faculty = Faculty(
            user_id=user.id,
            employee_id=faculty_data.employee_id,
            department_id=faculty_data.department_id,
            designation=faculty_data.designation,
            qualification=faculty_data.qualification,
            specialization=faculty_data.specialization,
            experience_years=faculty_data.experience_years,
            office_location=faculty_data.office_location,
            office_hours=faculty_data.office_hours
        )
        
        self.db.add(faculty)
        self.db.commit()
        self.db.refresh(faculty)
        
        logger.info(f"Created faculty: {faculty.employee_id}")
        return faculty
