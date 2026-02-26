@echo off
REM Quick Start Script - Frontend (Windows)

echo Starting Freelance Auto Hunter Frontend...
echo.

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo X node_modules not found!
    echo    Please run setup.bat first
    exit /b 1
)

echo √ Starting frontend server on http://localhost:5173
echo.
echo Press Ctrl+C to stop
echo.

REM Start server
call npm run dev
