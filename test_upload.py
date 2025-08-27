#!/usr/bin/env python3
"""
Test script to verify PDF upload functionality
"""
import requests
import json

def test_backend_health():
    """Test if backend is responding"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_pdf_upload_endpoint():
    """Test PDF upload endpoint"""
    try:
        # Create a test text file to upload (simulating PDF)
        test_content = """
        This is a test document for the LearnAid system.
        It contains sample educational content about machine learning.
        
        Machine learning is a method of data analysis that automates analytical model building.
        It is a branch of artificial intelligence (AI) based on the idea that systems can learn from data,
        identify patterns and make decisions with minimal human intervention.
        
        The goal of machine learning is to automatically learn from data without being explicitly programmed.
        This allows computers to find hidden insights without being specifically programmed where to look.
        """
        
        # Create a mock file for upload
        files = {
            'file': ('test_chapter.txt', test_content, 'text/plain')
        }
        
        data = {
            'course_id': '1',
            'chapter_name': 'Introduction to ML',
            'description': 'Test chapter upload',
            'generate_questions': 'true',
            'num_questions': '5'
        }
        
        response = requests.post("http://localhost:8000/api/v1/llm/upload-chapter-pdf", files=files, data=data)
        print(f"Upload test status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return True
        return False
        
    except Exception as e:
        print(f"Upload test failed: {e}")
        return False

def main():
    print("Testing LearnAid PDF Upload System")
    print("=" * 50)
    
    # Test 1: Backend health
    print("\n1. Testing backend health...")
    if test_backend_health():
        print("✅ Backend is running")
    else:
        print("❌ Backend not responding")
        return
    
    # Test 2: PDF upload endpoint
    print("\n2. Testing PDF upload endpoint...")
    if test_pdf_upload_endpoint():
        print("✅ PDF upload endpoint working")
    else:
        print("❌ PDF upload endpoint failed")

if __name__ == "__main__":
    main()
