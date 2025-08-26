#!/usr/bin/env python3
"""Test authentication logic directly"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from datetime import timedelta

def test_auth_flow():
    """Test complete authentication flow"""
    try:
        print("🧪 Testing Authentication Flow...")
        
        # Get database session
        db = next(get_db())
        
        # Find admin user
        user = db.query(User).filter(
            (User.username == "admin@learnaid.edu") | 
            (User.email == "admin@learnaid.edu")
        ).first()
        
        if not user:
            print("❌ User not found")
            return False
            
        print(f"✅ User found: {user.username}")
        
        # Verify password
        if not verify_password("admin123", user.hashed_password):
            print("❌ Password verification failed")
            return False
            
        print("✅ Password verified")
        
        # Check if user is active
        if not user.is_active:
            print("❌ User is not active")
            return False
            
        print("✅ User is active")
        
        # Create access token
        print(f"🔑 Creating tokens...")
        print(f"📊 Settings - SECRET_KEY exists: {bool(settings.secret_key)}")
        print(f"📊 Settings - Algorithm: {settings.jwt_algorithm}")
        print(f"📊 Settings - Expire minutes: {settings.jwt_access_token_expire_minutes}")
        
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        print(f"✅ Access token created (length: {len(access_token)})")
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        print(f"✅ Refresh token created (length: {len(refresh_token)})")
        
        # Test response format
        response = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
        
        print(f"✅ Response created successfully")
        print(f"🎉 Authentication flow test PASSED!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Authentication flow error: {e}")
        import traceback
        print(f"📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_auth_flow()
