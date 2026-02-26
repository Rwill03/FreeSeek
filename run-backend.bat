@echo off
REM Quick Start Script - Backend (Windows)

echo Starting Freelance Auto Hunter Backend...
echo.

cd backend

REM Check if venv exists
if not exist "venv" (
    echo X Virtual environment not found!
    echo    Please run setup.bat first
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist "..\\.env" (
    echo ! Warning: .env file not found!
    echo    Using default settings
)

echo √ Starting backend server on http://localhost:8000
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

REM Start server
python -m app.main
