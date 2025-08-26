"""
Initial data creation script for LearnAid.
Creates sample departments, admin user, faculty, and students for testing.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, create_tables
from app.core.security import get_password_hash
from app.models.user import User, UserRole, Department, Student, Faculty
from app.models.course import Course, Chapter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_initial_data():
    """Create initial data for the application."""
    
    # Create database tables
    create_tables()
    
    # Create a database session
    db: Session = SessionLocal()
    
    try:
        # Create departments
        departments_data = [
            {
                "name": "Computer Science Engineering",
                "code": "CSE",
                "description": "Department of Computer Science and Engineering",
                "head_of_department": "Dr. Smith Johnson"
            },
            {
                "name": "Electronics and Communication Engineering", 
                "code": "ECE",
                "description": "Department of Electronics and Communication Engineering",
                "head_of_department": "Dr. Jane Wilson"
            },
            {
                "name": "Mechanical Engineering",
                "code": "MECH",
                "description": "Department of Mechanical Engineering", 
                "head_of_department": "Dr. Bob Anderson"
            },
            {
                "name": "Information Technology",
                "code": "IT",
                "description": "Department of Information Technology",
                "head_of_department": "Dr. Alice Brown"
            }
        ]
        
        logger.info("Creating departments...")
        created_departments = {}
        for dept_data in departments_data:
            existing_dept = db.query(Department).filter(
                Department.code == dept_data["code"]
            ).first()
            
            if not existing_dept:
                department = Department(**dept_data)
                db.add(department)
                db.flush()
                created_departments[dept_data["code"]] = department
                logger.info(f"Created department: {dept_data['name']}")
            else:
                created_departments[dept_data["code"]] = existing_dept
                logger.info(f"Department already exists: {dept_data['name']}")
        
        db.commit()
        
        # Create admin user
        logger.info("Creating admin user...")
        admin_email = "admin@learnaid.edu"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                phone_number="+1234567890"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Created admin user - Email: admin@learnaid.edu, Password: admin123")
        else:
            logger.info("Admin user already exists")
        
        # Create sample faculty
        logger.info("Creating sample faculty...")
        faculty_data = [
            {
                "email": "john.doe@learnaid.edu",
                "username": "john.doe",
                "full_name": "Dr. John Doe",
                "password": "faculty123",
                "phone_number": "+1234567891",
                "employee_id": "CSE001",
                "department_code": "CSE",
                "designation": "Associate Professor",
                "qualification": "Ph.D. in Computer Science",
                "specialization": "Machine Learning, Data Science",
                "experience_years": 8,
                "office_location": "Block A, Room 301",
                "office_hours": "Mon-Fri 10:00-12:00"
            },
            {
                "email": "mary.smith@learnaid.edu",
                "username": "mary.smith",
                "full_name": "Dr. Mary Smith",
                "password": "faculty123",
                "phone_number": "+1234567892",
                "employee_id": "ECE001", 
                "department_code": "ECE",
                "designation": "Assistant Professor",
                "qualification": "Ph.D. in Electronics",
                "specialization": "Signal Processing, IoT",
                "experience_years": 5,
                "office_location": "Block B, Room 201",
                "office_hours": "Tue-Thu 14:00-16:00"
            }
        ]
        
        created_faculty = {}
        for faculty_info in faculty_data:
            existing_user = db.query(User).filter(
                User.email == faculty_info["email"]
            ).first()
            
            if not existing_user:
                # Create user account
                user = User(
                    email=faculty_info["email"],
                    username=faculty_info["username"],
                    full_name=faculty_info["full_name"],
                    hashed_password=get_password_hash(faculty_info["password"]),
                    role=UserRole.FACULTY,
                    phone_number=faculty_info["phone_number"]
                )
                db.add(user)
                db.flush()
                
                # Create faculty profile
                faculty = Faculty(
                    user_id=user.id,
                    employee_id=faculty_info["employee_id"],
                    department_id=created_departments[faculty_info["department_code"]].id,
                    designation=faculty_info["designation"],
                    qualification=faculty_info["qualification"],
                    specialization=faculty_info["specialization"],
                    experience_years=faculty_info["experience_years"],
                    office_location=faculty_info["office_location"],
                    office_hours=faculty_info["office_hours"]
                )
                db.add(faculty)
                db.flush()
                created_faculty[faculty_info["employee_id"]] = faculty
                logger.info(f"Created faculty: {faculty_info['full_name']}")
            else:
                logger.info(f"Faculty user already exists: {faculty_info['full_name']}")
        
        db.commit()
        
        # Create sample students
        logger.info("Creating sample students...")
        student_data = [
            {
                "email": "alice.johnson@student.learnaid.edu",
                "username": "alice.johnson",
                "full_name": "Alice Johnson",
                "password": "student123",
                "phone_number": "+1234567893",
                "student_id": "CS21B001",
                "department_code": "CSE",
                "class_name": "IV CSE A",
                "semester": 7,
                "academic_year": "2024-25",
                "cgpa": "8.5",
                "batch_year": 2021
            },
            {
                "email": "bob.wilson@student.learnaid.edu",
                "username": "bob.wilson",
                "full_name": "Bob Wilson",
                "password": "student123",
                "phone_number": "+1234567894",
                "student_id": "CS21B002", 
                "department_code": "CSE",
                "class_name": "IV CSE A",
                "semester": 7,
                "academic_year": "2024-25",
                "cgpa": "7.8",
                "batch_year": 2021
            },
            {
                "email": "carol.davis@student.learnaid.edu",
                "username": "carol.davis",
                "full_name": "Carol Davis",
                "password": "student123",
                "phone_number": "+1234567895",
                "student_id": "EC21B001",
                "department_code": "ECE",
                "class_name": "IV ECE B",
                "semester": 7,
                "academic_year": "2024-25", 
                "cgpa": "9.1",
                "batch_year": 2021
            }
        ]
        
        for student_info in student_data:
            existing_user = db.query(User).filter(
                User.email == student_info["email"]
            ).first()
            
            if not existing_user:
                # Create user account
                user = User(
                    email=student_info["email"],
                    username=student_info["username"],
                    full_name=student_info["full_name"],
                    hashed_password=get_password_hash(student_info["password"]),
                    role=UserRole.STUDENT,
                    phone_number=student_info["phone_number"]
                )
                db.add(user)
                db.flush()
                
                # Create student profile
                student = Student(
                    user_id=user.id,
                    student_id=student_info["student_id"],
                    department_id=created_departments[student_info["department_code"]].id,
                    class_name=student_info["class_name"],
                    semester=student_info["semester"],
                    academic_year=student_info["academic_year"],
                    cgpa=student_info["cgpa"],
                    batch_year=student_info["batch_year"]
                )
                db.add(student)
                logger.info(f"Created student: {student_info['full_name']}")
            else:
                logger.info(f"Student user already exists: {student_info['full_name']}")
        
        db.commit()
        
        # Create sample courses
        logger.info("Creating sample courses...")
        if created_faculty:
            cse_faculty = list(created_faculty.values())[0]  # Get first CSE faculty
            
            course_data = [
                {
                    "name": "Machine Learning",
                    "code": "CS401",
                    "description": "Introduction to machine learning algorithms and applications",
                    "department_id": created_departments["CSE"].id,
                    "faculty_id": cse_faculty.id,
                    "credits": 4,
                    "semester": 7,
                    "academic_year": "2024-25",
                    "course_type": "core"
                },
                {
                    "name": "Database Management Systems",
                    "code": "CS301",
                    "description": "Comprehensive study of database design and management",
                    "department_id": created_departments["CSE"].id,
                    "faculty_id": cse_faculty.id,
                    "credits": 3,
                    "semester": 5,
                    "academic_year": "2024-25",
                    "course_type": "core"
                }
            ]
            
            for course_info in course_data:
                existing_course = db.query(Course).filter(
                    Course.code == course_info["code"]
                ).first()
                
                if not existing_course:
                    course = Course(**course_info)
                    db.add(course)
                    logger.info(f"Created course: {course_info['name']}")
                else:
                    logger.info(f"Course already exists: {course_info['name']}")
        
        db.commit()
        
        logger.info("Initial data creation completed successfully!")
        logger.info("=" * 50)
        logger.info("LOGIN CREDENTIALS:")
        logger.info("Admin: admin@learnaid.edu / admin123")
        logger.info("Faculty: john.doe@learnaid.edu / faculty123")
        logger.info("Student: alice.johnson@student.learnaid.edu / student123")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_data()
