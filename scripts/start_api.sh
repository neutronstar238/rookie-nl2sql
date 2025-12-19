#!/bin/bash
# Start NL2SQL Web API Server
# M12: FastAPI service with HTML/CSS frontend

echo "Starting NL2SQL API Server..."
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit .env file with your API keys"
    fi
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the server
echo ""
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🎨 Web Interface: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd apps/api && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
