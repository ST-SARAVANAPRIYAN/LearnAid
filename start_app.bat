@echo off
echo ================================
echo Starting LearnAid Application
echo ================================
echo.

echo Starting Frontend (React)...
cd frontend
start "LearnAid Frontend" cmd /k "npm run dev"
echo Frontend starting...
echo.

echo Starting Backend (FastAPI)...
cd ..\backend
start "LearnAid Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo Backend starting...
echo.

echo ================================
echo LearnAid is starting up!
echo ================================
echo.
echo Frontend will be available at: http://localhost:5173
echo Backend will be available at:  http://localhost:8000
echo API Documentation:             http://localhost:8000/api/docs
echo.
echo Wait a few seconds for both services to start completely.
echo.
pause
