"""
Security utilities for LearnAid.
Handles password hashing, JWT token generation, and authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a plain password.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: The encoded JWT token
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating access token"
        )


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: The data to encode in the token
        
    Returns:
        str: The encoded JWT refresh token
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating refresh token"
        )


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token_payload(token: str) -> Optional[dict]:
    """
    Get token payload without verification (for debugging).
    
    Args:
        token: The JWT token
        
    Returns:
        dict or None: The token payload or None if invalid
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    except Exception:
        return None


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User email for password reset
        
    Returns:
        str: Password reset token
    """
    try:
        data = {"sub": email, "type": "password_reset"}
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        data.update({"exp": expire})
        
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Error generating password reset token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating reset token"
        )


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and return email.
    
    Args:
        token: Password reset token
        
    Returns:
        str or None: Email if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "password_reset":
            return None
            
        return payload.get("sub")
    except JWTError:
        return None


# Utility functions for role-based access
def check_admin_role(user_role: str) -> bool:
    """Check if user has admin role."""
    return user_role.lower() == "admin"


def check_faculty_role(user_role: str) -> bool:
    """Check if user has faculty role."""
    return user_role.lower() in ["faculty", "admin"]


def check_student_role(user_role: str) -> bool:
    """Check if user has student role."""
    return user_role.lower() in ["student", "faculty", "admin"]


def generate_student_id(department_code: str, batch_year: int, sequence: int) -> str:
    """
    Generate a formatted student ID.
    
    Args:
        department_code: Department code (e.g., "CS", "EC")
        batch_year: Year of admission (e.g., 2024)
        sequence: Sequential number for the student
        
    Returns:
        str: Formatted student ID (e.g., "CS24B001")
    """
    return f"{department_code}{batch_year % 100:02d}B{sequence:03d}"


def generate_employee_id(department_code: str, sequence: int) -> str:
    """
    Generate a formatted employee ID for faculty.
    
    Args:
        department_code: Department code (e.g., "CS", "EC")
        sequence: Sequential number for the employee
        
    Returns:
        str: Formatted employee ID (e.g., "CSF001")
    """
    return f"{department_code}F{sequence:03d}"
