#!/bin/bash

# LearnAid Backend Startup Script
# This script sets up and starts the LearnAid backend server

echo "🚀 Starting LearnAid Backend Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create upload and vector_db directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p vector_db

# Initialize database with sample data
echo "🗄️  Initializing database with sample data..."
python create_initial_data.py

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
echo "📋 Server will be available at: http://localhost:8000"
echo "📋 API Documentation: http://localhost:8000/api/docs"
echo "📋 Press Ctrl+C to stop the server"
echo ""
echo "🔑 Default Login Credentials:"
echo "   Admin: admin@learnaid.edu / admin123"
echo "   Faculty: john.doe@learnaid.edu / faculty123"
echo "   Student: alice.johnson@student.learnaid.edu / student123"
echo ""

# Run the server with auto-reload for development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
