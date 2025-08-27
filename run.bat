@echo off
echo 🚀🚀 Starting LearnAid Application 🚀🚀
echo.

REM Start the backend in a new command window
echo 🔧 Starting backend server...
start cmd /k "cd backend && start.bat"

REM Wait a moment for backend to start
timeout /t 5 > nul

REM Start the frontend in a new command window
echo 🎨 Starting frontend application...
start cmd /k "cd frontend && start.bat"

echo ✅ LearnAid application is starting!
echo.
echo 📊 Backend will be available at: http://localhost:8000
echo 📱 Frontend will be available at: http://localhost:5173
echo.
echo 🔑 Default Login Credentials:
echo    Admin: admin@learnaid.edu / admin123
echo    Faculty: john.doe@learnaid.edu / faculty123
echo    Student: alice.johnson@student.learnaid.edu / student123
echo.
