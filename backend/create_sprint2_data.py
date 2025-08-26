"""
Enhanced data seeding script for Sprint 2 - Faculty Dashboard.
Creates sample courses, chapters, and exams for testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import logging

from app.core.database import engine, get_db
from app.models.user import User, Department, Student, Faculty
from app.models.course import Course, Chapter
from app.models.exam import Exam, ExamQuestion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_courses_and_exams():
    """Create sample courses, chapters, and exams for testing."""
    
    db: Session = next(get_db())
    
    try:
        logger.info("🌱 Creating sample courses, chapters, and exams...")
        
        # Get existing faculty and departments
        faculty_john = db.query(Faculty).filter(Faculty.employee_id == "CSE001").first()
        faculty_mary = db.query(Faculty).filter(Faculty.employee_id == "ECE001").first()
        dept_cse = db.query(Department).filter(Department.code == "CSE").first()
        dept_ece = db.query(Department).filter(Department.code == "ECE").first()
        
        if not all([faculty_john, faculty_mary, dept_cse, dept_ece]):
            logger.error("Required faculty or departments not found. Run create_initial_data.py first.")
            return
        
        # Sample Courses for CSE Department (Dr. John Doe)
        courses_cse = [
            {
                "name": "Data Structures and Algorithms",
                "code": "CS301",
                "description": "Comprehensive study of data structures, algorithms, and their applications in problem solving.",
                "credits": 4,
                "semester": 5,
                "academic_year": "2024-25",
                "department_id": dept_cse.id,
                "faculty_id": faculty_john.id,
                "chapters": [
                    {
                        "title": "Arrays and Linked Lists",
                        "chapter_number": 1,
                        "description": "Basic data structures: arrays, linked lists, and their operations.",
                        "content_summary": "Introduction to linear data structures, memory allocation, and basic operations.",
                        "key_topics": "Arrays, Linked Lists, Memory Management, Pointer Operations",
                        "estimated_hours": 12.0,
                        "is_published": True
                    },
                    {
                        "title": "Stacks and Queues",
                        "chapter_number": 2,
                        "description": "LIFO and FIFO data structures and their applications.",
                        "content_summary": "Implementation of stacks and queues using arrays and linked lists.",
                        "key_topics": "Stack Operations, Queue Operations, LIFO, FIFO, Applications",
                        "estimated_hours": 10.0,
                        "is_published": True
                    },
                    {
                        "title": "Trees and Binary Trees",
                        "chapter_number": 3,
                        "description": "Hierarchical data structures and tree traversals.",
                        "content_summary": "Binary trees, BST, AVL trees, and traversal algorithms.",
                        "key_topics": "Binary Trees, BST, AVL Trees, Tree Traversal, Recursion",
                        "estimated_hours": 15.0,
                        "is_published": True
                    },
                    {
                        "title": "Graphs and Graph Algorithms",
                        "chapter_number": 4,
                        "description": "Graph representation and fundamental algorithms.",
                        "content_summary": "BFS, DFS, shortest path algorithms, and minimum spanning tree.",
                        "key_topics": "Graph Representation, BFS, DFS, Dijkstra, MST Algorithms",
                        "estimated_hours": 18.0,
                        "is_published": True
                    },
                    {
                        "title": "Sorting and Searching",
                        "chapter_number": 5,
                        "description": "Efficient sorting and searching algorithms.",
                        "content_summary": "Quick sort, merge sort, heap sort, and binary search techniques.",
                        "key_topics": "Sorting Algorithms, Search Techniques, Time Complexity, Optimization",
                        "estimated_hours": 14.0,
                        "is_published": True
                    }
                ]
            },
            {
                "name": "Machine Learning Fundamentals",
                "code": "CS401",
                "description": "Introduction to machine learning concepts, algorithms, and practical applications.",
                "credits": 3,
                "semester": 7,
                "academic_year": "2024-25",
                "department_id": dept_cse.id,
                "faculty_id": faculty_john.id,
                "chapters": [
                    {
                        "title": "Introduction to Machine Learning",
                        "chapter_number": 1,
                        "description": "Overview of ML concepts, types of learning, and applications.",
                        "content_summary": "Supervised, unsupervised, and reinforcement learning paradigms.",
                        "key_topics": "Supervised Learning, Unsupervised Learning, Reinforcement Learning, Applications",
                        "estimated_hours": 8.0,
                        "is_published": True
                    },
                    {
                        "title": "Linear Regression and Classification",
                        "chapter_number": 2,
                        "description": "Linear models for regression and classification problems.",
                        "content_summary": "Linear regression, logistic regression, and gradient descent.",
                        "key_topics": "Linear Regression, Logistic Regression, Gradient Descent, Cost Functions",
                        "estimated_hours": 12.0,
                        "is_published": True
                    },
                    {
                        "title": "Decision Trees and Ensemble Methods",
                        "chapter_number": 3,
                        "description": "Tree-based algorithms and ensemble techniques.",
                        "content_summary": "Decision trees, random forests, and boosting algorithms.",
                        "key_topics": "Decision Trees, Random Forest, Boosting, Bagging, Ensemble Methods",
                        "estimated_hours": 10.0,
                        "is_published": True
                    },
                    {
                        "title": "Neural Networks and Deep Learning",
                        "chapter_number": 4,
                        "description": "Introduction to artificial neural networks.",
                        "content_summary": "Perceptrons, multilayer networks, and backpropagation.",
                        "key_topics": "Neural Networks, Perceptrons, Backpropagation, Deep Learning",
                        "estimated_hours": 15.0,
                        "is_published": True
                    }
                ]
            }
        ]
        
        # Sample Courses for ECE Department (Dr. Mary Smith)
        courses_ece = [
            {
                "name": "Digital Signal Processing",
                "code": "EC301",
                "description": "Digital signal processing techniques and applications in communication systems.",
                "credits": 4,
                "semester": 5,
                "academic_year": "2024-25",
                "department_id": dept_ece.id,
                "faculty_id": faculty_mary.id,
                "chapters": [
                    {
                        "title": "Signals and Systems",
                        "chapter_number": 1,
                        "description": "Introduction to continuous and discrete signals.",
                        "content_summary": "Signal representation, system properties, and basic operations.",
                        "key_topics": "Continuous Signals, Discrete Signals, System Properties, Signal Operations",
                        "estimated_hours": 10.0,
                        "is_published": True
                    },
                    {
                        "title": "Z-Transform and DFT",
                        "chapter_number": 2,
                        "description": "Mathematical tools for discrete signal analysis.",
                        "content_summary": "Z-transform properties, DFT, and frequency domain analysis.",
                        "key_topics": "Z-Transform, DFT, FFT, Frequency Domain Analysis, ROC",
                        "estimated_hours": 12.0,
                        "is_published": True
                    },
                    {
                        "title": "Digital Filters",
                        "chapter_number": 3,
                        "description": "Design and implementation of digital filters.",
                        "content_summary": "FIR and IIR filter design techniques and applications.",
                        "key_topics": "FIR Filters, IIR Filters, Filter Design, Stability, Phase Response",
                        "estimated_hours": 14.0,
                        "is_published": True
                    },
                    {
                        "title": "Applications in Communication",
                        "chapter_number": 4,
                        "description": "DSP applications in modern communication systems.",
                        "content_summary": "Modulation, demodulation, and signal processing in communications.",
                        "key_topics": "Modulation, Demodulation, Communication Systems, Signal Processing",
                        "estimated_hours": 12.0,
                        "is_published": True
                    }
                ]
            }
        ]
        
        # Create all courses with chapters
        all_courses = courses_cse + courses_ece
        created_courses = []
        
        for course_data in all_courses:
            chapters_data = course_data.pop("chapters")
            
            # Check if course already exists
            existing_course = db.query(Course).filter(Course.code == course_data["code"]).first()
            if existing_course:
                logger.info(f"Course {course_data['code']} already exists, skipping...")
                created_courses.append(existing_course)
                continue
            
            # Create course
            course = Course(**course_data)
            db.add(course)
            db.commit()
            db.refresh(course)
            
            logger.info(f"✅ Created course: {course.name} ({course.code})")
            
            # Create chapters for the course
            for chapter_data in chapters_data:
                chapter = Chapter(
                    course_id=course.id,
                    **chapter_data
                )
                db.add(chapter)
            
            db.commit()
            logger.info(f"  📚 Created {len(chapters_data)} chapters for {course.name}")
            created_courses.append(course)
        
        # Create sample exams
        logger.info("📝 Creating sample exams...")
        
        # Get courses for exam creation
        dsa_course = db.query(Course).filter(Course.code == "CS301").first()
        ml_course = db.query(Course).filter(Course.code == "CS401").first()
        dsp_course = db.query(Course).filter(Course.code == "EC301").first()
        
        if dsa_course:
            # CIA1 for Data Structures
            dsa_chapters = db.query(Chapter).filter(Chapter.course_id == dsa_course.id).all()
            
            exam_dsa_cia1 = Exam(
                name="Data Structures CIA-1",
                exam_type="CIA1",
                exam_date=date.today() + timedelta(days=7),
                duration_minutes=180,
                total_marks=100.0,
                instructions="Answer all questions. Each question carries equal marks. Use proper algorithms and data structures.",
                course_id=dsa_course.id,
                faculty_id=faculty_john.id
            )
            db.add(exam_dsa_cia1)
            db.commit()
            db.refresh(exam_dsa_cia1)
            
            # Create questions for DSA CIA1
            dsa_questions = [
                {
                    "question_number": 1,
                    "max_marks": 20.0,
                    "chapter_id": dsa_chapters[0].id,  # Arrays and Linked Lists
                    "question_text": "Implement a singly linked list with insert, delete, and search operations. Analyze the time complexity.",
                    "expected_answer": "Implementation should include proper node structure and O(n) complexity analysis."
                },
                {
                    "question_number": 2,
                    "max_marks": 20.0,
                    "chapter_id": dsa_chapters[0].id,  # Arrays and Linked Lists
                    "question_text": "Compare arrays and linked lists in terms of memory usage and access time.",
                    "expected_answer": "Arrays have O(1) access but fixed size, linked lists have dynamic size but O(n) access."
                },
                {
                    "question_number": 3,
                    "max_marks": 20.0,
                    "chapter_id": dsa_chapters[1].id,  # Stacks and Queues
                    "question_text": "Design a stack-based solution for balanced parentheses checking.",
                    "expected_answer": "Use stack to push opening brackets and pop for closing brackets with validation."
                },
                {
                    "question_number": 4,
                    "max_marks": 20.0,
                    "chapter_id": dsa_chapters[1].id,  # Stacks and Queues
                    "question_text": "Implement a circular queue and explain its advantages over linear queue.",
                    "expected_answer": "Circular queue reuses space efficiently, avoiding the false overflow problem."
                },
                {
                    "question_number": 5,
                    "max_marks": 20.0,
                    "chapter_id": dsa_chapters[2].id,  # Trees
                    "question_text": "Write algorithms for inorder, preorder, and postorder traversal of binary trees.",
                    "expected_answer": "Recursive implementations with proper base cases and traversal order."
                }
            ]
            
            for question_data in dsa_questions:
                question = ExamQuestion(
                    exam_id=exam_dsa_cia1.id,
                    **question_data
                )
                db.add(question)
            
            db.commit()
            logger.info(f"✅ Created exam: {exam_dsa_cia1.name} with {len(dsa_questions)} questions")
        
        if ml_course:
            # CIA1 for Machine Learning
            ml_chapters = db.query(Chapter).filter(Chapter.course_id == ml_course.id).all()
            
            exam_ml_cia1 = Exam(
                name="Machine Learning CIA-1",
                exam_type="CIA1",
                exam_date=date.today() + timedelta(days=14),
                duration_minutes=120,
                total_marks=80.0,
                instructions="Answer all questions. Show all mathematical derivations clearly.",
                course_id=ml_course.id,
                faculty_id=faculty_john.id
            )
            db.add(exam_ml_cia1)
            db.commit()
            db.refresh(exam_ml_cia1)
            
            ml_questions = [
                {
                    "question_number": 1,
                    "max_marks": 15.0,
                    "chapter_id": ml_chapters[0].id,  # Introduction to ML
                    "question_text": "Explain the difference between supervised, unsupervised, and reinforcement learning with examples.",
                    "expected_answer": "Supervised uses labeled data, unsupervised finds patterns, reinforcement learns through rewards."
                },
                {
                    "question_number": 2,
                    "max_marks": 25.0,
                    "chapter_id": ml_chapters[1].id,  # Linear Regression
                    "question_text": "Derive the normal equation for linear regression and implement gradient descent algorithm.",
                    "expected_answer": "θ = (X'X)^-1 X'y for normal equation, iterative update for gradient descent."
                },
                {
                    "question_number": 3,
                    "max_marks": 20.0,
                    "chapter_id": ml_chapters[1].id,  # Classification
                    "question_text": "Explain logistic regression and derive the cost function with regularization.",
                    "expected_answer": "Sigmoid function, log-likelihood cost, L1/L2 regularization terms."
                },
                {
                    "question_number": 4,
                    "max_marks": 20.0,
                    "chapter_id": ml_chapters[2].id,  # Decision Trees
                    "question_text": "Describe the decision tree algorithm and explain entropy and information gain.",
                    "expected_answer": "Greedy splitting based on information gain, entropy measures uncertainty."
                }
            ]
            
            for question_data in ml_questions:
                question = ExamQuestion(
                    exam_id=exam_ml_cia1.id,
                    **question_data
                )
                db.add(question)
            
            db.commit()
            logger.info(f"✅ Created exam: {exam_ml_cia1.name} with {len(ml_questions)} questions")
        
        if dsp_course:
            # CIA1 for Digital Signal Processing
            dsp_chapters = db.query(Chapter).filter(Chapter.course_id == dsp_course.id).all()
            
            exam_dsp_cia1 = Exam(
                name="Digital Signal Processing CIA-1",
                exam_type="CIA1",
                exam_date=date.today() + timedelta(days=10),
                duration_minutes=150,
                total_marks=75.0,
                instructions="Answer all questions. Use proper mathematical notation and show all steps.",
                course_id=dsp_course.id,
                faculty_id=faculty_mary.id
            )
            db.add(exam_dsp_cia1)
            db.commit()
            db.refresh(exam_dsp_cia1)
            
            dsp_questions = [
                {
                    "question_number": 1,
                    "max_marks": 15.0,
                    "chapter_id": dsp_chapters[0].id,  # Signals and Systems
                    "question_text": "Define discrete-time signals and systems. Explain linearity and time-invariance properties.",
                    "expected_answer": "Mathematical definitions and examples of linear time-invariant systems."
                },
                {
                    "question_number": 2,
                    "max_marks": 20.0,
                    "chapter_id": dsp_chapters[1].id,  # Z-Transform
                    "question_text": "Find the Z-transform of the sequence x[n] = a^n u[n] and determine its ROC.",
                    "expected_answer": "X(z) = 1/(1-az^-1), ROC: |z| > |a|"
                },
                {
                    "question_number": 3,
                    "max_marks": 20.0,
                    "chapter_id": dsp_chapters[1].id,  # DFT
                    "question_text": "Derive the N-point DFT equation and explain its relationship with DTFT.",
                    "expected_answer": "DFT formula with twiddle factors and sampling of DTFT."
                },
                {
                    "question_number": 4,
                    "max_marks": 20.0,
                    "chapter_id": dsp_chapters[2].id,  # Digital Filters
                    "question_text": "Compare FIR and IIR filters in terms of stability, phase response, and computational complexity.",
                    "expected_answer": "FIR always stable with linear phase, IIR more efficient but can be unstable."
                }
            ]
            
            for question_data in dsp_questions:
                question = ExamQuestion(
                    exam_id=exam_dsp_cia1.id,
                    **question_data
                )
                db.add(question)
            
            db.commit()
            logger.info(f"✅ Created exam: {exam_dsp_cia1.name} with {len(dsp_questions)} questions")
        
        logger.info("🎉 Successfully created sample courses, chapters, and exams!")
        logger.info(f"📊 Summary:")
        logger.info(f"  - Courses created: {len(all_courses)}")
        logger.info(f"  - Total chapters: {sum(len(course.get('chapters', [])) for course in all_courses)}")
        logger.info(f"  - Exams created: 3 (CIA1 exams for all courses)")
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_courses_and_exams()
