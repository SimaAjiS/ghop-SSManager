@echo off
cd /d "%~dp0\.."
uv run .\backend\app\scripts\import_data.py
pause

