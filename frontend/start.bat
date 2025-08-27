@echo off
echo 🚀 Starting LearnAid Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed or not in PATH. Please install Node.js first.
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist node_modules (
    echo 📦 Installing dependencies...
    npm install
)

REM Start the development server
echo 🌟 Starting development server...
echo 📋 Frontend will be available at: http://localhost:5173
echo 📋 Press Ctrl+C to stop the server
echo.

npm run dev
