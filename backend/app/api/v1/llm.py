"""
API routes for LLM integration and PDF processing
Handles file uploads, question generation, and task creation
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel

from ..services.llm_service import llm_service
from ..services.pdf_service import pdf_processor, content_manager, process_uploaded_pdf
from ..services.task_service import task_generator
from ..core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["llm"])

# Request/Response models
class QuestionGenerationRequest(BaseModel):
    content: str
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"

class QuestionGenerationResponse(BaseModel):
    success: bool
    questions: List[Dict[str, Any]]
    message: str

class PDFUploadResponse(BaseModel):
    success: bool
    content_id: str
    filename: str
    text_length: int
    chunk_count: int
    generated_questions: int
    message: str

class TaskGenerationRequest(BaseModel):
    student_id: int
    performance_data: Dict[str, float]  # chapter -> performance score

class TaskGenerationResponse(BaseModel):
    success: bool
    tasks: List[Dict[str, Any]]
    message: str

@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """Generate MCQ questions from provided content"""
    
    try:
        questions = await llm_service.generate_mcq_from_content(
            content=request.content,
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        # Convert Pydantic models to dictionaries
        questions_dict = [
            {
                "question": q.question,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "difficulty": q.difficulty,
                "chapter_topic": q.chapter_topic
            }
            for q in questions
        ]
        
        return QuestionGenerationResponse(
            success=True,
            questions=questions_dict,
            message=f"Generated {len(questions)} questions successfully"
        )
        
    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    course_id: str = Form(...),
    chapter_name: str = Form(...),
    description: str = Form(""),
    generate_questions: bool = Form(True),
    num_questions: int = Form(10),
    difficulty: str = Form("medium"),
    db: Session = Depends(get_db)
):
    """
    Upload PDF and optionally generate questions
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process the PDF
        processing_result = await process_uploaded_pdf(
            file_content=file_content,
            filename=file.filename,
            course_id=course_id,
            chapter_name=chapter_name,
            description=description
        )
        
        if not processing_result["success"]:
            raise HTTPException(status_code=500, detail=processing_result["error"])
        
        generated_questions_count = 0
        
        # Generate questions if requested
        if generate_questions and processing_result["text_length"] > 100:
            try:
                # Get the processed content
                content_data = await content_manager.get_content(processing_result["content_id"])
                
                if content_data:
                    questions = await llm_service.generate_mcq_from_content(
                        content=content_data["original_text"][:4000],  # Limit content for LLM
                        topic=chapter_name,
                        num_questions=num_questions,
                        difficulty=difficulty
                    )
                    
                    generated_questions_count = len(questions)
                    
                    # TODO: Store questions in database
                    # For now, we'll just count them
                    logger.info(f"Generated {generated_questions_count} questions for {chapter_name}")
                
            except Exception as e:
                logger.warning(f"Question generation failed, but PDF processing succeeded: {e}")
        
        return PDFUploadResponse(
            success=True,
            content_id=processing_result["content_id"],
            filename=file.filename,
            text_length=processing_result["text_length"],
            chunk_count=processing_result["chunk_count"],
            generated_questions=generated_questions_count,
            message=f"PDF processed successfully. Generated {generated_questions_count} questions."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{content_id}")
async def get_content(content_id: str):
    """Retrieve processed content by ID"""
    
    try:
        content_data = await content_manager.get_content(content_id)
        
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {
            "success": True,
            "content": content_data,
            "message": "Content retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/course/{course_id}/content")
async def list_course_content(course_id: str):
    """List all processed content for a course"""
    
    try:
        content_list = await content_manager.list_course_content(course_id)
        
        return {
            "success": True,
            "content_list": content_list,
            "count": len(content_list),
            "message": f"Found {len(content_list)} content items for course {course_id}"
        }
        
    except Exception as e:
        logger.error(f"Content listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-tasks", response_model=TaskGenerationResponse)
async def generate_performance_based_tasks(
    request: TaskGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate personalized tasks based on student performance"""
    
    try:
        # Get course content for weak chapters
        weak_chapters = {
            chapter: score for chapter, score in request.performance_data.items()
            if score < 0.6  # Threshold for weak performance
        }
        
        if not weak_chapters:
            return TaskGenerationResponse(
                success=True,
                tasks=[],
                message="No weak areas identified. Student performance is satisfactory."
            )
        
        # For now, create mock course content
        # In production, this would fetch from the database
        course_content = {}
        for chapter in weak_chapters.keys():
            # Try to get content from content manager
            course_content_list = await content_manager.list_course_content("1")  # Mock course ID
            
            for content_item in course_content_list:
                if chapter.lower() in content_item["chapter_name"].lower():
                    content_data = await content_manager.get_content(content_item["content_id"])
                    if content_data:
                        course_content[chapter] = content_data["original_text"]
                    break
            
            # Fallback to mock content if not found
            if chapter not in course_content:
                course_content[chapter] = f"Study materials for {chapter} chapter..."
        
        # Generate tasks
        tasks = await task_generator.create_performance_based_tasks(
            student_performance=request.performance_data,
            course_content=course_content
        )
        
        return TaskGenerationResponse(
            success=True,
            tasks=tasks,
            message=f"Generated {len(tasks)} personalized tasks for improvement"
        )
        
    except Exception as e:
        logger.error(f"Task generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_llm_service():
    """Test endpoint to verify LLM service functionality"""
    
    test_content = """
    Machine learning is a method of data analysis that automates analytical model building.
    It is a branch of artificial intelligence based on the idea that systems can learn from data,
    identify patterns and make decisions with minimal human intervention.
    """
    
    try:
        questions = await llm_service.generate_mcq_from_content(
            content=test_content,
            topic="Introduction to Machine Learning",
            num_questions=2,
            difficulty="easy"
        )
        
        return {
            "success": True,
            "service_status": "operational",
            "test_questions": len(questions),
            "message": "LLM service is working correctly"
        }
        
    except Exception as e:
        return {
            "success": False,
            "service_status": "error",
            "error": str(e),
            "message": "LLM service test failed"
        }

@router.get("/stats")
async def get_llm_stats():
    """Get statistics about LLM usage and content processing"""
    
    try:
        # Mock statistics - in production this would query the database
        stats = {
            "total_pdfs_processed": 15,
            "total_questions_generated": 247,
            "total_tasks_created": 89,
            "courses_with_content": 5,
            "avg_questions_per_pdf": 16.5,
            "processing_success_rate": 0.94
        }
        
        return {
            "success": True,
            "stats": stats,
            "message": "LLM service statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """Check the health of LLM and PDF processing services"""
    
    try:
        # Test LLM service
        llm_status = "healthy" if llm_service.client else "unavailable"
        
        # Test PDF processor
        pdf_status = "healthy" if pdf_processor.upload_dir.exists() else "configuration_error"
        
        # Test content manager
        content_status = "healthy" if content_manager.content_dir.exists() else "configuration_error"
        
        overall_status = "healthy" if all(
            status == "healthy" for status in [llm_status, pdf_status, content_status]
        ) else "degraded"
        
        return {
            "status": overall_status,
            "services": {
                "llm_service": llm_status,
                "pdf_processor": pdf_status,
                "content_manager": content_status
            },
            "timestamp": "2025-08-27T09:30:00Z"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-08-27T09:30:00Z"
        }
