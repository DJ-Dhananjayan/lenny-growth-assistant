#!/bin/bash

# The Lenny Growth Assistant - Shutdown & Kill Script

echo "🛑 Stopping The Lenny Growth Assistant and clearing background tasks..."

# 1. Stop Docker Compose containers if running
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "🐳 Stopping Docker Compose services..."
    docker compose down --remove-orphans > /dev/null 2>&1
fi

# 2. Kill background process PIDs saved in .pid files
if [ -f .backend.pid ]; then
    BPID=$(cat .backend.pid)
    echo "🔪 Killing backend process (PID: $BPID)..."
    kill -9 $BPID > /dev/null 2>&1 || true
    rm -f .backend.pid
fi

if [ -f .frontend.pid ]; then
    FPID=$(cat .frontend.pid)
    echo "🔪 Killing frontend process (PID: $FPID)..."
    kill -9 $FPID > /dev/null 2>&1 || true
    rm -f .frontend.pid
fi

# 3. Kill any remaining processes occupying ports 8000 and 5173
lsof -ti :8000 | xargs kill -9 > /dev/null 2>&1 || true
lsof -ti :5173 | xargs kill -9 > /dev/null 2>&1 || true

# 4. Kill any background uvicorn or vite processes matching this workspace
pkill -f "app.main:app" > /dev/null 2>&1 || true
pkill -f "vite" > /dev/null 2>&1 || true

echo "✅ All background activities and processes for The Lenny Growth Assistant have been killed."
