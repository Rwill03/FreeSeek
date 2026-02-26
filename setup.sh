#!/bin/bash

# Freelance Auto Hunter - Setup Script
# This script helps you set up the application quickly

echo "=================================="
echo "Freelance Auto Hunter - Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Check Node version
echo "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js version: $NODE_VERSION"
echo ""

# Backend setup
echo "=================================="
echo "Setting up Backend..."
echo "=================================="
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright
echo "Installing Playwright browsers..."
playwright install chromium

echo "✅ Backend setup complete!"
echo ""

cd ..

# Frontend setup
echo "=================================="
echo "Setting up Frontend..."
echo "=================================="
cd frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"
echo ""

cd ..

# Check for .env file
echo "=================================="
echo "Configuration Check"
echo "=================================="

if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your settings:"
    echo "   1. Add your LLM API key"
    echo "   2. Set your target location"
    echo "   3. Configure CV file path"
    echo ""
else
    echo "✅ .env file exists"
fi

# Check for CV file
if [ ! -f "cv.pdf" ]; then
    echo "⚠️  No cv.pdf found"
    echo "   Please add your CV as cv.pdf in the project root"
    echo "   Or update CV_FILE_PATH in .env"
    echo ""
else
    echo "✅ CV file found"
fi

echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your configuration:"
echo "   - Add LLM API key (get free key from https://console.groq.com)"
echo "   - Set target location"
echo "   - Add CV file path"
echo ""
echo "2. Start the backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python -m app.main"
echo ""
echo "3. Start the frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open browser to: http://localhost:5173"
echo ""
echo "For more information, see README.md"
echo ""
