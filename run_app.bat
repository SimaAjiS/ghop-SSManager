@echo off
cd /d "%~dp0"

REM Start the backend server
uv run uvicorn app:app --reload --port 8000
pause
