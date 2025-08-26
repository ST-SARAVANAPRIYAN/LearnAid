# 📋 LearnAid Development Instructions

## 🎯 Development Guidelines

### Code Quality Standards
- **Type Safety**: Use Python type hints and TypeScript for frontend
- **Documentation**: Comprehensive docstrings for all functions and classes
- **Testing**: Minimum 80% code coverage with unit and integration tests
- **Code Style**: Follow PEP 8 for Python, ESLint/Prettier for React
- **Error Handling**: Comprehensive error handling with meaningful messages

### Backend Development (FastAPI)

#### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration management
│   │   ├── security.py         # Authentication & authorization
│   │   └── database.py         # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── course.py
│   │   └── exam.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── course.py
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── admin.py
│   │       ├── faculty.py
│   │       └── student.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── course_service.py
│   │   └── ml_service.py
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── pdf_processor.py
│       └── task_generator.py
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
└── alembic/                   # Database migrations
```

#### Coding Patterns

##### 1. SQLAlchemy Models
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

##### 2. Pydantic Schemas
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: str = Field(..., description="User email address")
    name: str = Field(..., min_length=2, max_length=100)
    
    @validator('email')
    def validate_email(cls, v):
        # Email validation logic
        return v
```

##### 3. API Routes
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db

router = APIRouter(prefix="/api/v1", tags=["users"])

@router.post("/users/", response_model=schemas.UserResponse)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new user with proper error handling"""
    try:
        return await user_service.create_user(db, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

##### 4. Service Layer
```python
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from typing import Optional

class UserService:
    """Service layer for user operations"""
    
    def __init__(self):
        pass
    
    async def create_user(self, db: Session, user: UserCreate) -> User:
        """Create a new user with validation"""
        # Business logic here
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
```

### Frontend Development (React)

#### Project Structure
```
frontend/
├── public/
├── src/
│   ├── components/             # Reusable components
│   │   ├── common/            # Common UI components
│   │   ├── forms/             # Form components
│   │   └── charts/            # Chart components
│   ├── pages/                 # Page components
│   │   ├── admin/
│   │   ├── faculty/
│   │   └── student/
│   ├── hooks/                 # Custom hooks
│   ├── services/              # API service layers
│   ├── store/                 # State management (Context/Redux)
│   ├── types/                 # TypeScript type definitions
│   ├── utils/                 # Utility functions
│   └── constants/             # Constants and enums
├── package.json
└── tsconfig.json
```

#### Coding Patterns

##### 1. Component Structure
```typescript
import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useTheme } from '@mui/material/styles';

interface ComponentProps {
  title: string;
  onAction: () => void;
}

/**
 * Reusable component with proper TypeScript typing
 */
const CustomComponent: React.FC<ComponentProps> = ({ title, onAction }) => {
  const theme = useTheme();
  
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" component="h2">
        {title}
      </Typography>
      <Button variant="contained" onClick={onAction}>
        Action
      </Button>
    </Box>
  );
};

export default CustomComponent;
```

##### 2. API Service Layer
```typescript
import axios, { AxiosResponse } from 'axios';
import { User, CreateUserRequest } from '../types';

class UserService {
  private baseURL = process.env.REACT_APP_API_URL + '/api/v1';
  
  async createUser(userData: CreateUserRequest): Promise<User> {
    try {
      const response: AxiosResponse<User> = await axios.post(
        `${this.baseURL}/users/`,
        userData
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }
  
  private handleError(error: any): Error {
    // Centralized error handling
    return new Error(error.response?.data?.detail || 'An error occurred');
  }
}

export const userService = new UserService();
```

##### 3. Custom Hooks
```typescript
import { useState, useEffect } from 'react';
import { User } from '../types';
import { userService } from '../services';

export const useUsers = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getUsers();
      setUsers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchUsers();
  }, []);
  
  return { users, loading, error, refetch: fetchUsers };
};
```

### Database Design Principles

#### 1. Relationship Mapping
- Use proper foreign key constraints
- Implement cascade delete where appropriate
- Create indexes for frequently queried columns
- Use meaningful table and column names

#### 2. Performance Optimization
- Implement pagination for large datasets
- Use database-level constraints
- Create composite indexes for complex queries
- Consider query optimization for analytics

### Testing Strategy

#### Backend Testing
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

#### Frontend Testing
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CustomComponent from './CustomComponent';

describe('CustomComponent', () => {
  const mockOnAction = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders with correct title', () => {
    render(<CustomComponent title="Test Title" onAction={mockOnAction} />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });
  
  it('calls onAction when button is clicked', () => {
    render(<CustomComponent title="Test" onAction={mockOnAction} />);
    fireEvent.click(screen.getByRole('button'));
    expect(mockOnAction).toHaveBeenCalledTimes(1);
  });
});
```

### Deployment & DevOps

#### Docker Configuration
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Configuration
```python
# config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "LearnAid"
    debug: bool = False
    database_url: str = "sqlite:///./learnaid.db"
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # ML/AI Configuration
    groq_api_key: Optional[str] = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 📋 Sprint Execution Checklist

### Pre-Sprint
- [ ] Sprint planning meeting completed
- [ ] User stories defined with acceptance criteria
- [ ] Technical tasks broken down
- [ ] Dependencies identified
- [ ] Estimation completed

### During Sprint
- [ ] Daily progress tracking
- [ ] Code reviews conducted
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Integration testing completed

### Post-Sprint
- [ ] Sprint review conducted
- [ ] Demo to stakeholders
- [ ] Retrospective meeting
- [ ] Sprint metrics collected
- [ ] Next sprint planning initiated

## 🔄 Continuous Improvement
- Collect and analyze sprint metrics
- Identify bottlenecks and improvement areas
- Update development practices based on learnings
- Maintain high code quality standards
- Foster team collaboration and knowledge sharing
