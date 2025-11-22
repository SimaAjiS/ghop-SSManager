@echo off
cd /d "%~dp0"

echo Starting Backend...
start "Backend Server" cmd /k "uv run uvicorn app:app --reload --port 8000"

echo Starting Frontend...
cd frontend

if not exist node_modules (
    echo Installing dependencies (first run only)...
    call npm install
)

call npm run dev -- --open
