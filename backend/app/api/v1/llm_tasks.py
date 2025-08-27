"""
LLM Tasks API - Handles task generation, PDF processing, and LLM integration
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.models.course import Course, Chapter
from app.models.task import Task, TaskQuestion
from app.services.llm_service import GroqLLMService, MCQQuestion
from app.services.pdf_service import PDFProcessingService
from app.services.task_service import TaskGenerationService
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.course import Course, Chapter
from app.models.task import Task, TaskQuestion
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
llm_service = GroqLLMService()
pdf_service = PDFProcessingService()
task_generator = TaskGenerationService()

# Pydantic models for request/response
class MCQGenerationRequest(BaseModel):
    content: str
    num_questions: int = 5
    difficulty: str = "medium"
    chapter_topic: Optional[str] = None

class GenerateTaskRequest(BaseModel):
    student_id: int
    course_id: int
    task_type: str  # "improvement", "reinforcement", "challenge"

class TaskGenerationResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[int] = None
    questions_generated: Optional[int] = None

class PDFUploadResponse(BaseModel):
    success: bool
    message: str
    file_path: str
    pdf_info: Optional[dict] = None

@router.post("/generate-mcq")
async def generate_mcq_questions(
    request: MCQGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate MCQ questions from provided content using LLM
    """
    try:
        # Generate questions using LLM service
        questions = await llm_service.generate_mcq_questions(
            content=request.content,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            topic=request.chapter_topic
        )
        
        if not questions:
            raise HTTPException(status_code=400, detail="Failed to generate questions from content")
        
        # Validate questions
        validated_questions = []
        for question in questions:
            validation = await llm_service.validate_question_quality(question)
            if validation["is_valid"]:
                validated_questions.append({
                    "question": question.question,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "explanation": question.explanation,
                    "difficulty": question.difficulty,
                    "topic": question.chapter_topic,
                    "quality_score": validation["quality_score"]
                })
        
        return JSONResponse({
            "success": True,
            "message": f"Generated {len(validated_questions)} quality questions",
            "questions": validated_questions,
            "total_generated": len(questions),
            "quality_filtered": len(validated_questions)
        })
        
    except Exception as e:
        logger.error(f"Error generating MCQ questions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

@router.post("/upload-chapter-pdf")
async def upload_chapter_pdf(
    background_tasks: BackgroundTasks,
    course_id: int = Form(...),
    chapter_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> PDFUploadResponse:
    """
    Upload PDF file for a course chapter
    """
    try:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Verify course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Read file content
        file_content = await file.read()
        
        # Save PDF file
        file_path = await pdf_service.save_uploaded_file(
            file_content=file_content,
            filename=file.filename,
            course_id=course_id,
            chapter_name=chapter_name
        )
        
        # Process PDF in background
        background_tasks.add_task(process_pdf_background, file_path, course_id, chapter_name, db)
        
        # Get basic PDF info
        pdf_info = await pdf_service.get_pdf_info(file_path)
        
        return PDFUploadResponse(
            success=True,
            message="PDF uploaded successfully and is being processed",
            file_path=file_path,
            pdf_info=pdf_info
        )
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")

async def process_pdf_background(file_path: str, course_id: int, chapter_name: str, db: Session):
    """Background task to process uploaded PDF"""
    try:
        # Process PDF content
        pdf_content = await pdf_service.process_pdf(file_path)
        
        # Update or create chapter with PDF info
        chapter = db.query(Chapter).filter(
            Chapter.course_id == course_id,
            Chapter.name == chapter_name
        ).first()
        
        if not chapter:
            chapter = Chapter(
                name=chapter_name,
                course_id=course_id,
                description=f"Chapter content from uploaded PDF: {pdf_content.filename}",
                order_index=1
            )
            db.add(chapter)
        
        # Store PDF path and metadata (would need to add these fields to Chapter model)
        # chapter.pdf_path = file_path
        # chapter.pdf_metadata = pdf_content.metadata
        
        db.commit()
        logger.info(f"PDF processing completed for {file_path}")
        
    except Exception as e:
        logger.error(f"Background PDF processing failed for {file_path}: {e}")

@router.post("/generate-personalized-task")
async def generate_personalized_task(
    request: GenerateTaskRequest,
    db: Session = Depends(get_db)
) -> TaskGenerationResponse:
    """
    Generate a personalized task for a student based on their performance
    """
    try:
        # Validate request
        if request.task_type not in ["improvement", "reinforcement", "challenge"]:
            raise HTTPException(
                status_code=400, 
                detail="Task type must be 'improvement', 'reinforcement', or 'challenge'"
            )
        
        # Generate task
        task_id = await task_generator.generate_personalized_task(
            db=db,
            student_id=request.student_id,
            course_id=request.course_id,
            task_type=request.task_type
        )
        
        if not task_id:
            raise HTTPException(status_code=400, detail="Failed to generate task - insufficient performance data")
        
        # Get task details
        from app.models.task import Task, TaskQuestion
        task = db.query(Task).filter(Task.id == task_id).first()
        questions_count = db.query(TaskQuestion).filter(TaskQuestion.task_id == task_id).count()
        
        return TaskGenerationResponse(
            success=True,
            message=f"Generated personalized {request.task_type} task successfully",
            task_id=task_id,
            questions_generated=questions_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating personalized task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate task: {str(e)}")

@router.get("/analyze-student-performance/{student_id}")
async def analyze_student_performance(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Analyze student performance and identify weak areas
    """
    try:
        analysis = await task_generator.analyze_student_performance(db, student_id)
        
        return JSONResponse({
            "success": True,
            "data": analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing student performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze performance: {str(e)}")

@router.post("/schedule-weekly-tasks")
async def schedule_weekly_tasks(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Schedule weekly tasks for all active students (admin function)
    """
    try:
        # Run task scheduling in background
        background_tasks.add_task(run_weekly_scheduling, db)
        
        return JSONResponse({
            "success": True,
            "message": "Weekly task scheduling initiated. Tasks will be generated in the background."
        })
        
    except Exception as e:
        logger.error(f"Error initiating weekly task scheduling: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule tasks: {str(e)}")

async def run_weekly_scheduling(db: Session):
    """Background task for weekly scheduling"""
    try:
        results = await task_generator.schedule_weekly_tasks(db)
        logger.info(f"Weekly scheduling completed: {results}")
    except Exception as e:
        logger.error(f"Weekly scheduling failed: {e}")

@router.get("/task-generation-stats")
async def get_task_generation_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics about task generation and LLM usage
    """
    try:
        from app.models.task import Task, TaskQuestion
        from sqlalchemy import func
        
        # Get task statistics
        total_tasks = db.query(Task).count()
        active_tasks = db.query(Task).filter(Task.is_active == True).count()
        total_questions = db.query(TaskQuestion).count()
        
        # Get tasks by type
        task_types = db.query(
            Task.task_type,
            func.count(Task.id).label('count')
        ).group_by(Task.task_type).all()
        
        # Get difficulty distribution
        difficulty_dist = db.query(
            TaskQuestion.difficulty_level,
            func.count(TaskQuestion.id).label('count')
        ).group_by(TaskQuestion.difficulty_level).all()
        
        return JSONResponse({
            "success": True,
            "stats": {
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
                "total_questions": total_questions,
                "task_types": [{"type": t[0], "count": t[1]} for t in task_types],
                "difficulty_distribution": [{"level": d[0], "count": d[1]} for d in difficulty_dist]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting task generation stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
