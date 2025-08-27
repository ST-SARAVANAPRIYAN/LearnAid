"""
Main FastAPI application for LearnAid.
Entry point with app configuration, middleware, and route registration.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# Import configuration and database
from app.core.config import settings
from app.core.database import create_tables, get_db
from app.core.security import verify_token

# Import API routers
from app.api.v1 import auth, admin, faculty, student
from app.api.v1.performance import router as performance_router
from app.api.v1.student_dashboard import router as student_dashboard_router
# from app.api.v1.llm_tasks import router as llm_tasks_router
from app.api.v1.llm import router as llm_router
# from app.api.v1.chatbot import router as chatbot_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting LearnAid application...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
        
        # Create upload directory
        upload_dir = Path(settings.upload_directory)
        upload_dir.mkdir(exist_ok=True)
        logger.info(f"Upload directory created: {upload_dir}")
        
        # Create vector database directory
        vector_dir = Path(settings.vector_db_path)
        vector_dir.mkdir(exist_ok=True)
        logger.info(f"Vector DB directory created: {vector_dir}")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LearnAid application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligent Learning & Performance Support System",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Mount static files for uploads
upload_path = Path(settings.upload_directory)
if upload_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    """
    Get current authenticated user from JWT token.
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify and decode token
        payload = verify_token(token)
        
        # Extract user information from payload
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        from app.models.user import User
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Role-based authentication dependencies
async def get_current_admin_user(current_user = Depends(get_current_user)):
    """Get current user with admin role verification."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_faculty_user(current_user = Depends(get_current_user)):
    """Get current user with faculty role verification."""
    if current_user.role.value not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty access required"
        )
    return current_user


async def get_current_student_user(current_user = Depends(get_current_user)):
    """Get current user with student role verification."""
    if current_user.role.value not in ["admin", "faculty", "student"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "message": "LearnAid API is running",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/api/docs" if settings.debug else "disabled"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    try:
        # Test database connection
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"  # This would be dynamic
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


# Include API routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)]
)

app.include_router(
    faculty.router,
    prefix="/api/v1/faculty",
    tags=["Faculty"],
    dependencies=[Depends(get_current_faculty_user)]
)

app.include_router(
    student.router,
    prefix="/api/v1/student",
    tags=["Student"],
    dependencies=[Depends(get_current_student_user)]
)

app.include_router(
    performance_router,
    prefix="/api/v1",
    tags=["Performance Analytics"],
    dependencies=[Depends(get_current_faculty_user)]  # Faculty can access performance data
)

app.include_router(
    student_dashboard_router,
    prefix="/api/v1",
    tags=["Student Dashboard"],
    dependencies=[Depends(get_current_student_user)]  # Students can access their own data
)

# app.include_router(
#     llm_tasks_router,
#     prefix="/api/v1/llm",
#     tags=["LLM & Task Generation"],
#     dependencies=[Depends(get_current_faculty_user)]  # Faculty can access LLM features
# )

app.include_router(
    llm_router,
    prefix="/api/v1",
    tags=["LLM Processing"]
    # dependencies=[Depends(get_current_faculty_user)]  # Temporarily disabled for testing
)

# Temporary LLM endpoints (placeholders until full implementation)
@app.get("/api/v1/llm/task-generation-stats", tags=["LLM Placeholder"])
async def get_task_generation_stats():
    """Placeholder endpoint for task generation stats."""
    return {
        "success": True,
        "stats": {
            "total_tasks_generated": 0,
            "total_questions_generated": 0,
            "active_courses": 0,
            "weekly_schedule_status": "inactive"
        }
    }

@app.post("/api/v1/llm/generate-questions", tags=["LLM Placeholder"])
async def generate_questions():
    """Placeholder endpoint for question generation."""
    return {
        "success": True,
        "questions": [],
        "message": "LLM service not configured. Please set up Groq API key."
    }

@app.post("/api/v1/llm/generate-personalized-task", tags=["LLM Placeholder"])
async def generate_personalized_task():
    """Placeholder endpoint for task generation."""
    return {
        "success": False,
        "message": "LLM service not configured. Please set up Groq API key and dependencies."
    }

@app.post("/api/v1/llm/schedule-weekly-tasks", tags=["LLM Placeholder"])
async def schedule_weekly_tasks():
    """Placeholder endpoint for weekly task scheduling."""
    return {
        "success": False,
        "message": "LLM service not configured. Please set up Groq API key and dependencies."
    }

@app.get("/api/v1/test-pdf-upload", tags=["Test Endpoints"])
async def test_pdf_upload():
    """Test endpoint to verify PDF upload with vector database storage."""
    try:
        from app.services.vector_service import vector_service
        vector_stats = await vector_service.get_statistics()
        
        return {
            "success": True,
            "message": "PDF upload system ready",
            "vector_database": {
                "available": True,
                "total_chunks": vector_stats.get("total_chunks", 0),
                "courses_indexed": vector_stats.get("courses_indexed", 0),
                "embedding_model": vector_stats.get("embedding_model", "unknown"),
                "vector_dimension": vector_stats.get("vector_dimension", 384)
            },
            "chunking_config": {
                "chunk_size": 500,
                "overlap": 100,
                "unit": "characters"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"PDF upload system error: {str(e)}",
            "error": str(e)
        }

# app.include_router(
#     chatbot_router,
#     tags=["AI Chatbot & Self-Learning"]
#     # Note: Chatbot endpoints will have student authentication
# )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal server error occurred",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
