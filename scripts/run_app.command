#!/bin/bash
cd "$(dirname "$0")/.."

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping backend..."
    kill $BACKEND_PID
}

# Trap exit signals to ensure cleanup
trap cleanup EXIT

echo "Starting Backend..."
uv run uvicorn backend.app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

echo "Starting Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies (first run only)..."
    npm install
fi

npm run dev -- --open
