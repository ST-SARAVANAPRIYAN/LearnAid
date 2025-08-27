@echo off
echo 🚀 Starting LearnAid Backend Server...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.11+ first.
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Create upload and vector_db directories
echo 📁 Creating necessary directories...
if not exist uploads mkdir uploads
if not exist vector_db mkdir vector_db

REM Initialize database with sample data if not already initialized
if not exist learnaid_dev.db (
    echo 🗄️ Initializing database with sample data...
    python create_initial_data.py
)

REM Start the FastAPI server
echo 🌟 Starting FastAPI server...
echo 📋 Server will be available at: http://localhost:8000
echo 📋 API Documentation: http://localhost:8000/docs
echo 📋 Press Ctrl+C to stop the server
echo.
echo 🔑 Default Login Credentials:
echo    Admin: admin@learnaid.edu / admin123
echo    Faculty: john.doe@learnaid.edu / faculty123
echo    Student: alice.johnson@student.learnaid.edu / student123
echo.

REM Run the server with auto-reload for development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
