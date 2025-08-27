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
from app.api.v1.llm_tasks import router as llm_tasks_router
from app.api.v1.chatbot import router as chatbot_router

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

app.include_router(
    llm_tasks_router,
    tags=["LLM & Task Generation"]
    # Note: LLM endpoints have individual authentication as needed
)

app.include_router(
    chatbot_router,
    tags=["AI Chatbot & Self-Learning"]
    # Note: Chatbot endpoints will have student authentication
)


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
