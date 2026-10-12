#!/bin/bash

# The Lenny Growth Assistant - Startup Script

echo "🚀 Starting The Lenny Growth Assistant..."

# 1. Ensure .env exists
if [ ! -f .env ]; then
    echo "📋 Copying .env.example to .env..."
    cp .env.example .env
fi

# 2. Check if Docker daemon is active and responsive
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "🐳 Docker daemon detected. Starting services with Docker Compose..."
    docker compose up --build -d
    echo ""
    echo "✅ Application successfully started in Docker!"
    echo "🌐 Frontend UI: http://localhost:5173"
    echo "⚙️ Backend API: http://localhost:8000/docs"
    echo "🏥 Health Check: http://localhost:8000/api/v1/health"
    exit 0
fi

# 3. Fallback to local background processes if Docker daemon is not active
echo "💻 Docker daemon not running. Launching local background services..."

# Create Python virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
else
    source .venv/bin/activate
fi

# Install frontend node modules if missing
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    (cd frontend && npm install)
fi

# Start Backend API in background
echo "🔥 Starting Backend API server on port 8000..."
PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

# Start Frontend Vite Dev Server in background
echo "⚡ Starting Frontend Vite server on port 5173..."
(cd frontend && npm run dev) > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✅ The Lenny Growth Assistant is running in background!"
echo "📍 Backend PID: $BACKEND_PID | Frontend PID: $FRONTEND_PID"
echo "🌐 Frontend UI: http://localhost:5173"
echo "⚙️ Backend API: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/api/v1/health"
echo "🛑 Run './end.sh' anytime to kill all background processes."
