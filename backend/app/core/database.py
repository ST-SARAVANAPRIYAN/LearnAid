"""
Database configuration and session management for LearnAid.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_database_config, settings
import logging

logger = logging.getLogger(__name__)

# Get database configuration
db_config = get_database_config()
DATABASE_URL = db_config["url"]

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=db_config.get("echo", False),
    pool_pre_ping=db_config.get("pool_pre_ping", True),
    pool_recycle=db_config.get("pool_recycle", -1),
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()


def create_tables():
    """Create all database tables."""
    try:
        # Import all models to ensure they're registered with Base
        from app.models import user, course, exam, task  # noqa
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_db():
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_tables():
    """Drop all database tables (use with caution)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise
