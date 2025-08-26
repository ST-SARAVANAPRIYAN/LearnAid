"""
User schemas for LearnAid API.
Pydantic models for user-related requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles enum."""
    ADMIN = "admin"
    FACULTY = "faculty"
    STUDENT = "student"


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_picture: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_picture: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User schema with database fields."""
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User schema for API responses."""
    id: int
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


# Department schemas
class DepartmentBase(BaseModel):
    """Base department schema."""
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=10)
    description: Optional[str] = None
    head_of_department: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    """Schema for creating a department."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating department information."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    head_of_department: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    """Department schema for API responses."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Student schemas
class StudentBase(BaseModel):
    """Base student schema."""
    student_id: str = Field(..., min_length=5, max_length=20)
    class_name: str = Field(..., min_length=2, max_length=100)
    semester: int = Field(..., ge=1, le=8)
    academic_year: str = Field(..., regex=r'^\d{4}-\d{2}$')
    cgpa: Optional[str] = Field(None, max_length=5)
    batch_year: int = Field(..., ge=2020, le=2030)


class StudentCreate(StudentBase):
    """Schema for creating a student profile."""
    user_id: int
    department_id: int
    
    # User creation fields
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)


class StudentUpdate(BaseModel):
    """Schema for updating student information."""
    class_name: Optional[str] = Field(None, min_length=2, max_length=100)
    semester: Optional[int] = Field(None, ge=1, le=8)
    academic_year: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}$')
    cgpa: Optional[str] = Field(None, max_length=5)


class StudentResponse(StudentBase):
    """Student schema for API responses."""
    id: int
    user: UserResponse
    department: DepartmentResponse
    total_points: int
    current_streak: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Faculty schemas
class FacultyBase(BaseModel):
    """Base faculty schema."""
    employee_id: str = Field(..., min_length=5, max_length=20)
    designation: str = Field(..., min_length=2, max_length=100)
    qualification: Optional[str] = Field(None, max_length=255)
    specialization: Optional[str] = Field(None, max_length=255)
    experience_years: int = Field(default=0, ge=0)
    office_location: Optional[str] = Field(None, max_length=100)
    office_hours: Optional[str] = Field(None, max_length=200)


class FacultyCreate(FacultyBase):
    """Schema for creating a faculty profile."""
    user_id: int
    department_id: int
    
    # User creation fields
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)


class FacultyUpdate(BaseModel):
    """Schema for updating faculty information."""
    designation: Optional[str] = Field(None, min_length=2, max_length=100)
    qualification: Optional[str] = Field(None, max_length=255)
    specialization: Optional[str] = Field(None, max_length=255)
    experience_years: Optional[int] = Field(None, ge=0)
    office_location: Optional[str] = Field(None, max_length=100)
    office_hours: Optional[str] = Field(None, max_length=200)


class FacultyResponse(FacultyBase):
    """Faculty schema for API responses."""
    id: int
    user: UserResponse
    department: DepartmentResponse
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# Bulk operations schemas
class BulkStudentCreate(BaseModel):
    """Schema for bulk student creation."""
    students: List[StudentCreate]
    send_welcome_email: bool = True


class BulkFacultyCreate(BaseModel):
    """Schema for bulk faculty creation."""
    faculty: List[FacultyCreate]
    send_welcome_email: bool = True


# Dashboard schemas
class UserStats(BaseModel):
    """User statistics schema."""
    total_users: int
    active_users: int
    students: int
    faculty: int
    admins: int


class DashboardSummary(BaseModel):
    """Dashboard summary schema."""
    user_stats: UserStats
    recent_registrations: List[UserResponse]
