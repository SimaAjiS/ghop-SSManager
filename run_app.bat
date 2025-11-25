@echo off
cd /d "%~dp0"

echo ========================================
echo Starting Backend Server...
echo ========================================
start "Backend Server" cmd /k "%~dp0start_backend.bat"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting Frontend Server...
echo ========================================
start "Frontend Server" cmd /k "%~dp0start_frontend.bat"

timeout /t 2 /nobreak >nul
echo.
echo ========================================
echo Both servers are starting:
echo   - Backend: http://127.0.0.1:8000
echo   - Frontend: http://localhost:5173
echo ========================================
echo.
echo Check the "Backend Server" and "Frontend Server" windows for status.
echo This window will close in 5 seconds...
timeout /t 5 /nobreak >nul
