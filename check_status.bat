@echo off
echo ================================
echo LearnAid Application Status Check
echo ================================
echo.

echo Checking Frontend (React)...
curl -s http://localhost:5173 > nul
if %errorlevel% == 0 (
    echo ✓ Frontend is running at http://localhost:5173
) else (
    echo ✗ Frontend is not running
)
echo.

echo Checking Backend (FastAPI)...
curl -s http://localhost:8000/health > nul
if %errorlevel% == 0 (
    echo ✓ Backend is running at http://localhost:8000
    echo ✓ API Documentation: http://localhost:8000/api/docs
) else (
    echo ✗ Backend is not running
)
echo.

echo ================================
echo Application URLs:
echo ================================
echo Frontend:     http://localhost:5173
echo Backend:      http://localhost:8000  
echo API Docs:     http://localhost:8000/api/docs
echo Health Check: http://localhost:8000/health
echo ================================
pause
