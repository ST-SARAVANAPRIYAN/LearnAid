"""
Configuration settings for LearnAid application with robust error handling.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with comprehensive error handling."""
    
    # Application Settings
    app_name: str = "LearnAid"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Database Configuration
    database_url: str = "sqlite:///./learnaid_dev.db"
    
    # Security Configuration
    secret_key: str = "dev-secret-key-change-in-production-this-is-not-secure"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # CORS Settings
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5174,http://127.0.0.1:5174"
    
    # File Upload Settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: str = ".pdf,.doc,.docx,.txt"
    upload_directory: str = "uploads"
    
    # AI/ML Configuration
    groq_api_key: Optional[str] = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_db_path: str = "vector_db"
    
    def get_allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list."""
        try:
            return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        except Exception as e:
            logger.warning(f"Error parsing allowed origins: {e}")
            return ["http://localhost:3000"]
    
    def get_allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        try:
            return [ft.strip() for ft in self.allowed_file_types.split(",") if ft.strip()]
        except Exception as e:
            logger.warning(f"Error parsing file types: {e}")
            return [".pdf", ".doc", ".docx", ".txt"]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Allow extra fields
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Failed to create settings: {e}")
        # Return minimal fallback settings
        return Settings()


def get_database_config() -> dict:
    """Get database configuration based on current environment."""
    settings = get_settings()
    
    if settings.environment == "development":
        return {
            "url": "sqlite:///./learnaid_dev.db",
            "echo": True,
            "pool_pre_ping": True,
        }
    elif settings.environment == "testing":
        return {
            "url": "sqlite:///./learnaid_test.db",
            "echo": False,
            "pool_pre_ping": True,
        }
    else:  # production
        return {
            "url": settings.database_url,
            "echo": False,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }


# Create settings instance
settings = get_settings()
