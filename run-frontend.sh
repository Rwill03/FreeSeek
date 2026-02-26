#!/bin/bash

# Quick Start Script - Frontend
# Run this from the project root

echo "Starting Freelance Auto Hunter Frontend..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found!"
    echo "   Please run setup.sh first"
    exit 1
fi

echo "✅ Starting frontend server on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start server
npm run dev
