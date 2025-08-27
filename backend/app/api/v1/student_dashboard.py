"""
Student API endpoints for LearnAid system.
Handles student course access, CIA results, task retrieval, and performance tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.user import Student, User, Faculty
from app.models.course import Course, Chapter, CourseEnrollment
from app.models.exam import Exam, ExamResult, ExamResponse, StudentChapterPerformance
from app.models.task import Task, TaskAssignment, TaskAttempt
from app.schemas.user import StudentResponse
from app.schemas.course import CourseResponse, ChapterResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/dashboard/{student_id}")
async def get_student_dashboard(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard data for a student including:
    - Enrolled courses
    - Recent CIA exam results
    - Pending tasks
    - Performance summary
    """
    try:
        # Get student with user info
        student = db.query(Student).options(
            joinedload(Student.user),
            joinedload(Student.department)
        ).filter(Student.id == student_id).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get enrolled courses
        enrollments = db.query(CourseEnrollment).options(
            joinedload(CourseEnrollment.course).joinedload(Course.faculty).joinedload(Faculty.user)
        ).filter(CourseEnrollment.student_id == student_id).all()
        
        courses_data = []
        total_chapters = 0
        completed_chapters = 0
        
        for enrollment in enrollments:
            course = enrollment.course
            chapters = db.query(Chapter).filter(Chapter.course_id == course.id).all()
            
            courses_data.append({
                "course_id": course.id,
                "course_name": course.name,
                "course_code": course.code,
                "faculty_name": course.faculty.user.full_name,
                "semester": course.semester,
                "credits": course.credits,
                "total_chapters": len(chapters),
                "current_chapter": enrollment.current_chapter,
                "completion_percentage": enrollment.completion_percentage,
                "enrollment_date": enrollment.enrollment_date
            })
            
            total_chapters += len(chapters)
            completed_chapters += enrollment.current_chapter - 1 if enrollment.current_chapter > 1 else 0
        
        # Get recent CIA exam results
        recent_results = db.query(ExamResult).options(
            joinedload(ExamResult.exam).joinedload(Exam.course)
        ).filter(
            ExamResult.student_id == student_id
        ).order_by(ExamResult.created_at.desc()).limit(5).all()
        
        exam_results = []
        for result in recent_results:
            exam_results.append({
                "exam_id": result.exam.id,
                "exam_title": result.exam.title,
                "course_name": result.exam.course.name,
                "exam_type": result.exam.exam_type,
                "marks_obtained": result.total_marks_obtained,
                "total_marks": result.total_marks_possible,
                "percentage": result.percentage,
                "grade": result.grade,
                "exam_date": result.exam.exam_date,
                "submission_time": result.submission_time
            })
        
        # Get pending tasks
        pending_assignments = db.query(TaskAssignment).options(
            joinedload(TaskAssignment.task).joinedload(Task.course),
            joinedload(TaskAssignment.task).joinedload(Task.chapter)
        ).filter(
            TaskAssignment.student_id == student_id,
            TaskAssignment.is_completed == False,
            TaskAssignment.due_date >= datetime.utcnow()
        ).order_by(TaskAssignment.due_date.asc()).all()
        
        pending_tasks = []
        for assignment in pending_assignments:
            task = assignment.task
            pending_tasks.append({
                "assignment_id": assignment.id,
                "task_id": task.id,
                "task_title": task.title,
                "course_name": task.course.name,
                "chapter_title": task.chapter.title,
                "task_type": task.task_type,
                "difficulty": task.difficulty_level,
                "time_limit": task.time_limit_minutes,
                "due_date": assignment.due_date,
                "assignment_reason": assignment.assignment_reason,
                "priority": assignment.priority
            })
        
        # Get overall performance summary
        performance_records = db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id == student_id
        ).all()
        
        total_performance = sum(record.chapter_accuracy_percentage for record in performance_records)
        avg_performance = total_performance / len(performance_records) if performance_records else 0
        
        weak_chapters = len([r for r in performance_records if r.is_weak_chapter])
        total_tasks_assigned = sum(record.tasks_assigned for record in performance_records)
        total_tasks_completed = sum(record.tasks_completed for record in performance_records)
        
        return {
            "student_info": {
                "student_id": student.id,
                "name": student.user.full_name,
                "student_reg_no": student.student_id,
                "class": student.class_name,
                "semester": student.semester,
                "department": student.department.name,
                "cgpa": student.cgpa,
                "total_points": student.total_points,
                "current_streak": student.current_streak
            },
            "academic_summary": {
                "enrolled_courses": len(courses_data),
                "total_chapters": total_chapters,
                "completed_chapters": completed_chapters,
                "overall_completion": (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0,
                "average_performance": round(avg_performance, 2),
                "weak_chapters_count": weak_chapters
            },
            "courses": courses_data,
            "recent_exam_results": exam_results,
            "pending_tasks": pending_tasks,
            "performance_summary": {
                "total_tasks_assigned": total_tasks_assigned,
                "total_tasks_completed": total_tasks_completed,
                "completion_rate": (total_tasks_completed / total_tasks_assigned * 100) if total_tasks_assigned > 0 else 0,
                "weak_chapters": weak_chapters,
                "improvement_needed": weak_chapters > 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching student dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")


@router.get("/courses/{student_id}")
async def get_student_courses(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed course information for a student including chapters and progress.
    """
    try:
        enrollments = db.query(CourseEnrollment).options(
            joinedload(CourseEnrollment.course).joinedload(Course.chapters),
            joinedload(CourseEnrollment.course).joinedload(Course.faculty).joinedload(Faculty.user)
        ).filter(CourseEnrollment.student_id == student_id).all()
        
        courses = []
        for enrollment in enrollments:
            course = enrollment.course
            chapters = db.query(Chapter).filter(
                Chapter.course_id == course.id
            ).order_by(Chapter.chapter_number).all()
            
            # Get student's performance for each chapter
            chapter_performances = db.query(StudentChapterPerformance).filter(
                StudentChapterPerformance.student_id == student_id,
                StudentChapterPerformance.chapter_id.in_([ch.id for ch in chapters])
            ).all()
            
            performance_map = {perf.chapter_id: perf for perf in chapter_performances}
            
            chapters_data = []
            for chapter in chapters:
                performance = performance_map.get(chapter.id)
                chapters_data.append({
                    "chapter_id": chapter.id,
                    "chapter_number": chapter.chapter_number,
                    "title": chapter.title,
                    "description": chapter.description,
                    "estimated_hours": chapter.estimated_hours,
                    "is_published": chapter.is_published,
                    "performance": {
                        "accuracy_percentage": performance.chapter_accuracy_percentage if performance else None,
                        "performance_level": performance.performance_level if performance else "not_assessed",
                        "is_weak": performance.is_weak_chapter if performance else False,
                        "tasks_assigned": performance.tasks_assigned if performance else 0,
                        "tasks_completed": performance.tasks_completed if performance else 0
                    }
                })
            
            courses.append({
                "course_id": course.id,
                "course_name": course.name,
                "course_code": course.code,
                "description": course.description,
                "faculty_name": course.faculty.user.full_name,
                "semester": course.semester,
                "credits": course.credits,
                "current_chapter": enrollment.current_chapter,
                "completion_percentage": enrollment.completion_percentage,
                "chapters": chapters_data
            })
        
        return {"courses": courses}
        
    except Exception as e:
        logger.error(f"Error fetching student courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch course data")


@router.get("/exam-results/{student_id}")
async def get_student_exam_results(
    student_id: int,
    course_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get detailed CIA exam results with chapter-wise breakdown.
    """
    try:
        query = db.query(ExamResult).options(
            joinedload(ExamResult.exam).joinedload(Exam.course),
            joinedload(ExamResult.responses).joinedload(ExamResponse.question).joinedload(ExamQuestion.chapter)
        ).filter(ExamResult.student_id == student_id)
        
        if course_id:
            query = query.join(Exam).filter(Exam.course_id == course_id)
        
        exam_results = query.order_by(ExamResult.created_at.desc()).all()
        
        results = []
        for result in exam_results:
            # Calculate chapter-wise performance
            chapter_performance = {}
            
            for response in result.responses:
                chapter_id = response.question.chapter_id
                chapter_title = response.question.chapter.title
                
                if chapter_id not in chapter_performance:
                    chapter_performance[chapter_id] = {
                        "chapter_title": chapter_title,
                        "total_marks": 0,
                        "obtained_marks": 0,
                        "questions_count": 0
                    }
                
                chapter_performance[chapter_id]["total_marks"] += response.max_marks
                chapter_performance[chapter_id]["obtained_marks"] += response.marks_obtained
                chapter_performance[chapter_id]["questions_count"] += 1
            
            # Calculate percentages
            for chapter_data in chapter_performance.values():
                chapter_data["percentage"] = (
                    chapter_data["obtained_marks"] / chapter_data["total_marks"] * 100
                ) if chapter_data["total_marks"] > 0 else 0
            
            results.append({
                "result_id": result.id,
                "exam": {
                    "exam_id": result.exam.id,
                    "title": result.exam.title,
                    "course_name": result.exam.course.name,
                    "exam_type": result.exam.exam_type,
                    "exam_date": result.exam.exam_date,
                    "total_marks": result.exam.total_marks
                },
                "overall_performance": {
                    "marks_obtained": result.total_marks_obtained,
                    "total_marks": result.total_marks_possible,
                    "percentage": result.percentage,
                    "grade": result.grade,
                    "submission_time": result.submission_time,
                    "time_taken": result.time_taken_minutes
                },
                "chapter_wise_performance": list(chapter_performance.values())
            })
        
        return {"exam_results": results}
        
    except Exception as e:
        logger.error(f"Error fetching exam results: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch exam results")


@router.get("/tasks/{student_id}")
async def get_student_tasks(
    student_id: int,
    status: Optional[str] = Query(None, pattern="^(pending|completed|overdue)$"),
    db: Session = Depends(get_db)
):
    """
    Get student's assigned tasks with filtering options.
    """
    try:
        query = db.query(TaskAssignment).options(
            joinedload(TaskAssignment.task).joinedload(Task.course),
            joinedload(TaskAssignment.task).joinedload(Task.chapter),
            joinedload(TaskAssignment.task).joinedload(Task.questions)
        ).filter(TaskAssignment.student_id == student_id)
        
        now = datetime.utcnow()
        
        if status == "pending":
            query = query.filter(
                TaskAssignment.is_completed == False,
                TaskAssignment.due_date >= now
            )
        elif status == "completed":
            query = query.filter(TaskAssignment.is_completed == True)
        elif status == "overdue":
            query = query.filter(
                TaskAssignment.is_completed == False,
                TaskAssignment.due_date < now
            )
        
        assignments = query.order_by(TaskAssignment.assigned_date.desc()).all()
        
        tasks = []
        for assignment in assignments:
            task = assignment.task
            
            # Get student's attempts for this task
            attempts = db.query(TaskAttempt).filter(
                TaskAttempt.task_id == task.id,
                TaskAttempt.student_id == student_id
            ).order_by(TaskAttempt.created_at.desc()).all()
            
            task_status = "pending"
            if assignment.is_completed:
                task_status = "completed"
            elif assignment.due_date < now and not assignment.is_completed:
                task_status = "overdue"
            
            tasks.append({
                "assignment_id": assignment.id,
                "task": {
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "course_name": task.course.name,
                    "chapter_title": task.chapter.title,
                    "task_type": task.task_type,
                    "difficulty_level": task.difficulty_level,
                    "total_questions": task.total_questions,
                    "time_limit_minutes": task.time_limit_minutes,
                    "study_time_minutes": task.study_time_minutes,
                    "study_material": task.study_material
                },
                "assignment": {
                    "assigned_date": assignment.assigned_date,
                    "due_date": assignment.due_date,
                    "status": task_status,
                    "priority": assignment.priority,
                    "assignment_reason": assignment.assignment_reason,
                    "target_improvement": assignment.target_improvement_percentage
                },
                "attempts": [
                    {
                        "attempt_id": attempt.id,
                        "attempt_number": attempt.attempt_number,
                        "start_time": attempt.start_time,
                        "end_time": attempt.end_time,
                        "marks_obtained": attempt.total_marks_obtained,
                        "total_marks": attempt.total_marks_possible,
                        "percentage": attempt.percentage,
                        "is_completed": attempt.is_completed
                    }
                    for attempt in attempts
                ],
                "max_attempts": task.max_attempts,
                "attempts_remaining": task.max_attempts - len(attempts)
            })
        
        return {"tasks": tasks}
        
    except Exception as e:
        logger.error(f"Error fetching student tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")


@router.get("/performance/{student_id}")
async def get_student_performance(
    student_id: int,
    course_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive performance analytics for a student.
    """
    try:
        query = db.query(StudentChapterPerformance).options(
            joinedload(StudentChapterPerformance.chapter).joinedload(Chapter.course)
        ).filter(StudentChapterPerformance.student_id == student_id)
        
        if course_id:
            query = query.join(Chapter).filter(Chapter.course_id == course_id)
        
        performance_records = query.all()
        
        # Aggregate performance data
        course_performance = {}
        overall_stats = {
            "total_chapters": 0,
            "weak_chapters": 0,
            "average_performance": 0,
            "total_tasks_assigned": 0,
            "total_tasks_completed": 0,
            "improvement_areas": []
        }
        
        for record in performance_records:
            course = record.chapter.course
            course_id = course.id
            
            if course_id not in course_performance:
                course_performance[course_id] = {
                    "course_name": course.name,
                    "course_code": course.code,
                    "chapters": [],
                    "course_average": 0,
                    "weak_chapters_count": 0
                }
            
            chapter_data = {
                "chapter_id": record.chapter_id,
                "chapter_title": record.chapter.title,
                "chapter_number": record.chapter.chapter_number,
                "performance_percentage": record.chapter_accuracy_percentage,
                "performance_level": record.performance_level,
                "is_weak": record.is_weak_chapter,
                "tasks_assigned": record.tasks_assigned,
                "tasks_completed": record.tasks_completed,
                "improvement_trend": record.improvement_trend,
                "last_exam_date": record.last_cia_exam_date,
                "cia_exams_taken": record.cia_exams_taken
            }
            
            course_performance[course_id]["chapters"].append(chapter_data)
            
            # Update overall stats
            overall_stats["total_chapters"] += 1
            if record.is_weak_chapter:
                overall_stats["weak_chapters"] += 1
                course_performance[course_id]["weak_chapters_count"] += 1
                overall_stats["improvement_areas"].append({
                    "course": course.name,
                    "chapter": record.chapter.title,
                    "performance": record.chapter_accuracy_percentage
                })
            
            overall_stats["total_tasks_assigned"] += record.tasks_assigned
            overall_stats["total_tasks_completed"] += record.tasks_completed
        
        # Calculate averages
        if performance_records:
            total_performance = sum(r.chapter_accuracy_percentage for r in performance_records)
            overall_stats["average_performance"] = total_performance / len(performance_records)
            
            for course_data in course_performance.values():
                if course_data["chapters"]:
                    course_avg = sum(ch["performance_percentage"] for ch in course_data["chapters"])
                    course_data["course_average"] = course_avg / len(course_data["chapters"])
        
        overall_stats["task_completion_rate"] = (
            overall_stats["total_tasks_completed"] / overall_stats["total_tasks_assigned"] * 100
        ) if overall_stats["total_tasks_assigned"] > 0 else 0
        
        return {
            "overall_stats": overall_stats,
            "course_performance": list(course_performance.values()),
            "performance_trend": "improving" if overall_stats["average_performance"] > 60 else "needs_attention"
        }
        
    except Exception as e:
        logger.error(f"Error fetching student performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance data")
