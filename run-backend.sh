#!/bin/bash

# Quick Start Script - Backend
# Run this from the project root

echo "Starting Freelance Auto Hunter Backend..."
echo ""

cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Using default settings"
fi

echo "✅ Starting backend server on http://localhost:8000"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start server
python -m app.main
