"""
Basic tests for LearnAid API.
Tests for authentication, user creation, and basic functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User, UserRole, Department
from app.core.security import get_password_hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestAuth:
    """Test authentication endpoints."""
    
    def setup_method(self):
        """Set up test data before each test."""
        db = TestingSessionLocal()
        
        # Create test department
        self.department = Department(
            name="Test Department",
            code="TEST",
            description="Test Department"
        )
        db.add(self.department)
        db.flush()
        
        # Create test user
        self.test_user = User(
            email="test@test.com",
            username="testuser",
            full_name="Test User",
            hashed_password=get_password_hash("testpass123"),
            role=UserRole.ADMIN
        )
        db.add(self.test_user)
        db.commit()
        db.close()
    
    def teardown_method(self):
        """Clean up after each test."""
        db = TestingSessionLocal()
        db.query(User).delete()
        db.query(Department).delete()
        db.commit()
        db.close()
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "LearnAid API is running" in data["message"]
    
    def test_login_success(self):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect username or password" in data["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "testpass123"}
        )
        assert response.status_code == 401


class TestAdmin:
    """Test admin endpoints."""
    
    def setup_method(self):
        """Set up test data before each test."""
        db = TestingSessionLocal()
        
        # Create test admin user
        self.admin_user = User(
            email="admin@test.com",
            username="admin",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(self.admin_user)
        db.commit()
        
        # Get access token
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        db.close()
    
    def teardown_method(self):
        """Clean up after each test."""
        db = TestingSessionLocal()
        db.query(User).delete()
        db.query(Department).delete()
        db.commit()
        db.close()
    
    def test_create_department(self):
        """Test creating a department."""
        department_data = {
            "name": "Computer Science",
            "code": "CS",
            "description": "Computer Science Department"
        }
        
        response = client.post(
            "/api/v1/admin/departments",
            json=department_data,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Computer Science"
        assert data["code"] == "CS"
    
    def test_get_departments(self):
        """Test getting departments."""
        # First create a department
        department_data = {
            "name": "Information Technology",
            "code": "IT",
            "description": "IT Department"
        }
        
        client.post(
            "/api/v1/admin/departments",
            json=department_data,
            headers=self.headers
        )
        
        # Then get departments
        response = client.get("/api/v1/admin/departments", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(dept["code"] == "IT" for dept in data)
    
    def test_get_dashboard(self):
        """Test getting dashboard summary."""
        response = client.get("/api/v1/admin/dashboard", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_stats" in data
        assert "recent_registrations" in data
        assert data["user_stats"]["total_users"] >= 1  # At least the admin user


def test_unauthorized_access():
    """Test unauthorized access to protected endpoints."""
    response = client.get("/api/v1/admin/departments")
    assert response.status_code == 403  # Should be forbidden without auth


def test_invalid_token():
    """Test access with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/admin/departments", headers=headers)
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
