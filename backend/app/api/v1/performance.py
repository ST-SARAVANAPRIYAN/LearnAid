"""
Performance analysis API endpoints.
Handles student performance tracking, weak chapter identification, and task assignment.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.exam import StudentChapterPerformance, ExamResult, ExamResponse
from app.models.task import TaskAssignment, Task
from app.models.user import Student
from app.models.course import Chapter, Course
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/students/{student_id}/chapter-performance")
async def get_student_chapter_performance(
    student_id: int,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get student's performance across all chapters or specific course chapters.
    Shows which chapters the student is struggling with.
    """
    try:
        query = db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id == student_id
        )
        
        if course_id:
            # Join with Chapter to filter by course
            query = query.join(Chapter).filter(Chapter.course_id == course_id)
        
        performance_records = query.all()
        
        if not performance_records:
            # If no performance records exist, create initial ones based on exam results
            await _initialize_student_performance(student_id, course_id, db)
            performance_records = query.all()
        
        return {
            "student_id": student_id,
            "course_id": course_id,
            "performance_records": [
                {
                    "chapter_id": record.chapter_id,
                    "chapter_title": record.chapter.title if hasattr(record, 'chapter') else None,
                    "accuracy_percentage": record.chapter_accuracy_percentage,
                    "performance_level": record.performance_level,
                    "is_weak_chapter": record.is_weak_chapter,
                    "tasks_assigned": record.tasks_assigned,
                    "tasks_completed": record.tasks_completed,
                    "improvement_trend": record.improvement_trend,
                    "last_exam_date": record.last_cia_exam_date,
                    "next_task_due": record.next_task_due_date
                }
                for record in performance_records
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching student performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance data")


@router.get("/courses/{course_id}/weak-students")
async def get_weak_students_by_chapter(
    course_id: int,
    chapter_id: Optional[int] = None,
    threshold: float = 50.0,
    db: Session = Depends(get_db)
):
    """
    Get students who are performing poorly in specific chapters.
    Used for identifying students who need task assignments.
    """
    try:
        query = db.query(StudentChapterPerformance).join(Chapter).filter(
            Chapter.course_id == course_id,
            StudentChapterPerformance.chapter_accuracy_percentage < threshold,
            StudentChapterPerformance.is_weak_chapter == True
        )
        
        if chapter_id:
            query = query.filter(StudentChapterPerformance.chapter_id == chapter_id)
        
        weak_performance_records = query.all()
        
        result = []
        for record in weak_performance_records:
            student = db.query(Student).filter(Student.id == record.student_id).first()
            if student:
                result.append({
                    "student_id": record.student_id,
                    "student_name": student.user.full_name,
                    "student_reg_no": student.student_id,
                    "chapter_id": record.chapter_id,
                    "chapter_title": record.chapter.title,
                    "performance_percentage": record.chapter_accuracy_percentage,
                    "performance_level": record.performance_level,
                    "tasks_assigned": record.tasks_assigned,
                    "tasks_completed": record.tasks_completed,
                    "last_exam_date": record.last_cia_exam_date,
                    "needs_task_assignment": record.tasks_assigned == 0 or 
                                           (record.next_task_due_date and record.next_task_due_date <= datetime.utcnow())
                })
        
        return {
            "course_id": course_id,
            "chapter_id": chapter_id,
            "performance_threshold": threshold,
            "weak_students": result,
            "total_weak_students": len(result)
        }
    except Exception as e:
        logger.error(f"Error fetching weak students: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weak students data")


@router.post("/students/{student_id}/assign-task")
async def assign_task_to_student(
    student_id: int,
    task_id: int,
    chapter_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """
    Assign a specific task to a student based on poor chapter performance.
    """
    try:
        # Check if student and task exist
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if assignment already exists
        existing_assignment = db.query(TaskAssignment).filter(
            TaskAssignment.student_id == student_id,
            TaskAssignment.task_id == task_id,
            TaskAssignment.is_completed == False
        ).first()
        
        if existing_assignment:
            return {"message": "Task already assigned to student", "assignment_id": existing_assignment.id}
        
        # Get student's current performance for this chapter
        performance_record = db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id == student_id,
            StudentChapterPerformance.chapter_id == chapter_id
        ).first()
        
        current_performance = performance_record.chapter_accuracy_percentage if performance_record else 0.0
        
        # Create new task assignment
        assignment = TaskAssignment(
            task_id=task_id,
            student_id=student_id,
            assignment_reason=reason,
            student_chapter_performance=current_performance,
            target_improvement_percentage=70.0,
            due_date=datetime.utcnow() + timedelta(days=2),  # 2 days to complete
            is_auto_assigned=False
        )
        
        db.add(assignment)
        
        # Update performance record
        if performance_record:
            performance_record.tasks_assigned += 1
            performance_record.next_task_due_date = assignment.due_date
        
        db.commit()
        db.refresh(assignment)
        
        return {
            "message": "Task assigned successfully",
            "assignment_id": assignment.id,
            "student_name": student.user.full_name,
            "task_title": task.title,
            "due_date": assignment.due_date,
            "current_performance": current_performance
        }
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to assign task")


@router.post("/auto-assign-tasks")
async def auto_assign_tasks_to_weak_students(
    course_id: int,
    chapter_id: Optional[int] = None,
    performance_threshold: float = 50.0,
    db: Session = Depends(get_db)
):
    """
    Automatically assign tasks to students performing poorly in chapters.
    """
    try:
        # Get all weak students for the course/chapter
        weak_students = await get_weak_students_by_chapter(
            course_id=course_id,
            chapter_id=chapter_id,
            threshold=performance_threshold,
            db=db
        )
        
        assignments_created = 0
        
        for weak_student in weak_students["weak_students"]:
            if weak_student["needs_task_assignment"]:
                # Find available tasks for this chapter
                available_tasks = db.query(Task).filter(
                    Task.chapter_id == weak_student["chapter_id"],
                    Task.is_published == True,
                    Task.is_active == True,
                    Task.auto_assign_to_poor_performers == True
                ).all()
                
                if available_tasks:
                    # Assign the first suitable task
                    task = available_tasks[0]
                    
                    assignment = TaskAssignment(
                        task_id=task.id,
                        student_id=weak_student["student_id"],
                        assignment_reason=f"Poor performance in {weak_student['chapter_title']} ({weak_student['performance_percentage']:.1f}%)",
                        student_chapter_performance=weak_student["performance_percentage"],
                        target_improvement_percentage=70.0,
                        due_date=datetime.utcnow() + timedelta(days=2),
                        is_auto_assigned=True,
                        auto_assignment_algorithm="weak_chapter_detection_v1"
                    )
                    
                    db.add(assignment)
                    assignments_created += 1
                    
                    # Update performance record
                    performance_record = db.query(StudentChapterPerformance).filter(
                        StudentChapterPerformance.student_id == weak_student["student_id"],
                        StudentChapterPerformance.chapter_id == weak_student["chapter_id"]
                    ).first()
                    
                    if performance_record:
                        performance_record.tasks_assigned += 1
                        performance_record.next_task_due_date = assignment.due_date
                        performance_record.last_task_assigned_date = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"Auto-assigned {assignments_created} tasks to weak students",
            "course_id": course_id,
            "chapter_id": chapter_id,
            "assignments_created": assignments_created,
            "performance_threshold": performance_threshold
        }
    except Exception as e:
        logger.error(f"Error in auto-assignment: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to auto-assign tasks")


async def _initialize_student_performance(student_id: int, course_id: Optional[int], db: Session):
    """
    Initialize student performance records based on existing exam results.
    This runs when a student has no performance records yet.
    """
    try:
        # Get all exam results for this student
        query = db.query(ExamResult).filter(ExamResult.student_id == student_id)
        
        if course_id:
            query = query.join(Exam).filter(Exam.course_id == course_id)
        
        exam_results = query.all()
        
        # Group responses by chapter
        chapter_performance = {}
        
        for result in exam_results:
            for response in result.responses:
                chapter_id = response.question.chapter_id
                
                if chapter_id not in chapter_performance:
                    chapter_performance[chapter_id] = {
                        'total_marks_obtained': 0.0,
                        'total_marks_possible': 0.0,
                        'questions_count': 0,
                        'exams_count': 0
                    }
                
                chapter_performance[chapter_id]['total_marks_obtained'] += response.marks_obtained
                chapter_performance[chapter_id]['total_marks_possible'] += response.max_marks
                chapter_performance[chapter_id]['questions_count'] += 1
        
        # Create performance records
        for chapter_id, perf_data in chapter_performance.items():
            accuracy = (perf_data['total_marks_obtained'] / perf_data['total_marks_possible'] * 100) if perf_data['total_marks_possible'] > 0 else 0
            
            performance_record = StudentChapterPerformance(
                student_id=student_id,
                chapter_id=chapter_id,
                cia_exams_taken=len(exam_results),
                total_questions_attempted=perf_data['questions_count'],
                total_marks_obtained=perf_data['total_marks_obtained'],
                total_marks_possible=perf_data['total_marks_possible'],
                chapter_accuracy_percentage=accuracy,
                performance_score=accuracy,  # Simple scoring for now
                performance_level="needs_improvement" if accuracy < 50 else "average" if accuracy < 70 else "good" if accuracy < 85 else "excellent",
                is_weak_chapter=accuracy < 50.0,
                last_cia_exam_date=max([result.created_at for result in exam_results], default=None)
            )
            
            db.add(performance_record)
        
        db.commit()
    except Exception as e:
        logger.error(f"Error initializing student performance: {e}")
        db.rollback()
