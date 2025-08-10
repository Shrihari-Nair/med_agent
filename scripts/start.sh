#!/bin/bash

# Medicine Alternative System Startup Script

echo "🚀 Starting Medicine Alternative System..."

# Check if we're in the right directory
if [ ! -f "src/api/backend.py" ]; then
    echo "❌ Please run this script from the med_agent directory"
    exit 1
fi

# Using existing virtual environment (assumed to be active)

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# Check environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️ Warning: GOOGLE_API_KEY environment variable not set"
    echo "   Set it with: export GOOGLE_API_KEY='your_api_key'"
    echo ""
fi

# Create database if it doesn't exist
if [ ! -f "data/medicines.db" ]; then
    echo "🗄️ Creating medicine database..."
    python3 src/database/create_db.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create database"
        exit 1
    fi
fi

# Kill any existing processes on ports 8001 and 8080  
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn.*backend" 2>/dev/null || true
pkill -f "python.*backend" 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Start the development servers
echo "🌟 Starting development servers..."
cd "$(dirname "$0")/.." && python3 scripts/start.py 