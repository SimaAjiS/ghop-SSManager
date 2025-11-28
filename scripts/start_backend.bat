@echo off
cd /d "%~dp0\.."
uv run uvicorn backend.app.main:app --reload --port 8000
pause


