#!/usr/bin/env python3
"""Test script to check database and authentication"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password

def test_database():
    """Test database connection and user data"""
    try:
        # Get database session
        db = next(get_db())
        
        # Query users
        users = db.query(User).all()
        print(f"✅ Database connected successfully")
        print(f"📊 Total users: {len(users)}")
        
        for user in users:
            print(f"👤 User: {user.username} | Email: {user.email} | Role: {user.role} | Active: {user.is_active}")
        
        # Test admin user specifically
        admin = db.query(User).filter(User.email == "admin@learnaid.edu").first()
        if admin:
            print(f"🔑 Admin user found: {admin.username}")
            print(f"🔐 Stored password hash: {admin.hashed_password}")
            # Test password verification
            test_password = verify_password("admin123", admin.hashed_password)
            print(f"🔐 Password verification test: {'✅ PASS' if test_password else '❌ FAIL'}")
        else:
            print("❌ Admin user not found!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LearnAid Database...")
    test_database()
