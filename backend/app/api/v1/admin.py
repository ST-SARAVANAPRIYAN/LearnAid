"""
Admin API routes for LearnAid.
Handles faculty and student management, departments, and system administration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole, Department, Student, Faculty
from app.models.course import Course
from app.schemas.user import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    StudentCreate, StudentUpdate, StudentResponse,
    FacultyCreate, FacultyUpdate, FacultyResponse,
    UserResponse, UserStats, DashboardSummary
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Department Management
@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new department."""
    try:
        # Check if department already exists
        existing_dept = db.query(Department).filter(
            (Department.name == department.name) |
            (Department.code == department.code)
        ).first()
        
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with this name or code already exists"
            )
        
        # Create new department
        db_department = Department(**department.dict())
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        
        logger.info(f"Created department: {db_department.name}")
        return db_department
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating department: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create department"
        )


@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all departments."""
    try:
        departments = db.query(Department).offset(skip).limit(limit).all()
        return departments
    except Exception as e:
        logger.error(f"Error fetching departments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch departments"
        )


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific department."""
    try:
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        return department
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching department {department_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch department"
        )


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_update: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    """Update a department."""
    try:
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Update fields
        update_data = department_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(department, field, value)
        
        db.commit()
        db.refresh(department)
        
        logger.info(f"Updated department: {department.name}")
        return department
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating department {department_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update department"
        )


# Faculty Management
@router.post("/faculty", response_model=FacultyResponse)
async def create_faculty(
    faculty_data: FacultyCreate,
    db: Session = Depends(get_db)
):
    """Create a new faculty member."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == faculty_data.email) |
            (User.username == faculty_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Check if employee ID already exists
        existing_faculty = db.query(Faculty).filter(
            Faculty.employee_id == faculty_data.employee_id
        ).first()
        
        if existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Faculty with this employee ID already exists"
            )
        
        # Create user account
        user = User(
            email=faculty_data.email,
            username=faculty_data.username,
            full_name=faculty_data.full_name,
            hashed_password=get_password_hash(faculty_data.password),
            role=UserRole.FACULTY,
            phone_number=faculty_data.phone_number
        )
        db.add(user)
        db.flush()  # Get user ID
        
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
        db.add(faculty)
        db.commit()
        db.refresh(faculty)
        
        logger.info(f"Created faculty: {faculty.employee_id}")
        return faculty
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating faculty: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create faculty"
        )


@router.get("/faculty", response_model=List[FacultyResponse])
async def get_faculty(
    department_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all faculty members."""
    try:
        query = db.query(Faculty)
        
        if department_id:
            query = query.filter(Faculty.department_id == department_id)
        
        faculty = query.offset(skip).limit(limit).all()
        return faculty
    except Exception as e:
        logger.error(f"Error fetching faculty: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch faculty"
        )


@router.get("/faculty/{faculty_id}", response_model=FacultyResponse)
async def get_faculty_member(
    faculty_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific faculty member."""
    try:
        faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found"
            )
        return faculty
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching faculty {faculty_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch faculty"
        )


# Student Management
@router.post("/students", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db)
):
    """Create a new student."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == student_data.email) |
            (User.username == student_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Check if student ID already exists
        existing_student = db.query(Student).filter(
            Student.student_id == student_data.student_id
        ).first()
        
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this ID already exists"
            )
        
        # Create user account
        user = User(
            email=student_data.email,
            username=student_data.username,
            full_name=student_data.full_name,
            hashed_password=get_password_hash(student_data.password),
            role=UserRole.STUDENT,
            phone_number=student_data.phone_number
        )
        db.add(user)
        db.flush()  # Get user ID
        
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
        db.add(student)
        db.commit()
        db.refresh(student)
        
        logger.info(f"Created student: {student.student_id}")
        return student
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create student"
        )


@router.get("/students", response_model=List[StudentResponse])
async def get_students(
    department_id: Optional[int] = Query(None),
    class_name: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all students with optional filters."""
    try:
        query = db.query(Student)
        
        if department_id:
            query = query.filter(Student.department_id == department_id)
        if class_name:
            query = query.filter(Student.class_name == class_name)
        if semester:
            query = query.filter(Student.semester == semester)
        
        students = query.offset(skip).limit(limit).all()
        return students
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch students"
        )


# Dashboard and Analytics
@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """Get admin dashboard summary."""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        students = db.query(User).filter(User.role == UserRole.STUDENT).count()
        faculty = db.query(User).filter(User.role == UserRole.FACULTY).count()
        admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
        
        user_stats = UserStats(
            total_users=total_users,
            active_users=active_users,
            students=students,
            faculty=faculty,
            admins=admins
        )
        
        # Recent registrations (last 10)
        recent_registrations = db.query(User).order_by(
            User.created_at.desc()
        ).limit(10).all()
        
        return DashboardSummary(
            user_stats=user_stats,
            recent_registrations=recent_registrations
        )
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch dashboard data"
        )


@router.get("/statistics")
async def get_system_statistics(
    db: Session = Depends(get_db)
):
    """Get detailed system statistics."""
    try:
        # User statistics
        user_stats = db.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        # Department statistics
        dept_stats = db.query(
            Department.name,
            func.count(Student.id).label('student_count'),
            func.count(Faculty.id).label('faculty_count')
        ).outerjoin(Student).outerjoin(Faculty).group_by(Department.id).all()
        
        # Course statistics
        course_count = db.query(Course).count()
        active_courses = db.query(Course).filter(Course.is_active == True).count()
        
        return {
            "users": {role.value: count for role, count in user_stats},
            "departments": [
                {
                    "name": name,
                    "students": student_count or 0,
                    "faculty": faculty_count or 0
                }
                for name, student_count, faculty_count in dept_stats
            ],
            "courses": {
                "total": course_count,
                "active": active_courses
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch statistics"
        )
