@echo off
REM Freelance Auto Hunter - Setup Script for Windows
REM This script helps you set up the application quickly

echo ==================================
echo Freelance Auto Hunter - Setup
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo √ Python version: %PYTHON_VERSION%
echo.

REM Check Node version
echo Checking Node.js version...
node --version >nul 2>&1
if errorlevel 1 (
    echo X Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo √ Node.js version: %NODE_VERSION%
echo.

REM Backend setup
echo ==================================
echo Setting up Backend...
echo ==================================
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo √ Virtual environment created
) else (
    echo √ Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright
echo Installing Playwright browsers...
playwright install chromium

echo √ Backend setup complete!
echo.

cd ..

REM Frontend setup
echo ==================================
echo Setting up Frontend...
echo ==================================
cd frontend

REM Install Node dependencies
echo Installing Node.js dependencies...
call npm install

echo √ Frontend setup complete!
echo.

cd ..

REM Check for .env file
echo ==================================
echo Configuration Check
echo ==================================

if not exist ".env" (
    echo ! No .env file found. Creating from .env.example...
    copy .env.example .env
    echo √ .env file created
    echo.
    echo ! IMPORTANT: Edit .env file with your settings:
    echo    1. Add your LLM API key
    echo    2. Set your target location
    echo    3. Configure CV file path
    echo.
) else (
    echo √ .env file exists
)

REM Check for CV file
if not exist "cv.pdf" (
    echo ! No cv.pdf found
    echo    Please add your CV as cv.pdf in the project root
    echo    Or update CV_FILE_PATH in .env
    echo.
) else (
    echo √ CV file found
)

echo ==================================
echo Setup Complete! 🎉
echo ==================================
echo.
echo Next steps:
echo.
echo 1. Edit .env file with your configuration:
echo    - Add LLM API key (get free key from https://console.groq.com)
echo    - Set target location
echo    - Add CV file path
echo.
echo 2. Start the backend (Terminal 1):
echo    cd backend
echo    venv\Scripts\activate
echo    python -m app.main
echo.
echo 3. Start the frontend (Terminal 2):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open browser to: http://localhost:5173
echo.
echo For more information, see README.md
echo.

pause
