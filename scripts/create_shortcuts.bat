@echo off
echo Creating Windows shortcuts in the project root...
cd /d "%~dp0\.."

set SCRIPT_DIR=%~dp0

:: Create shortcuts using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%CD%\start_backend.lnk'); $Shortcut.TargetPath = '%SCRIPT_DIR%start_backend.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Start Backend Server'; $Shortcut.Save()"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%CD%\start_frontend.lnk'); $Shortcut.TargetPath = '%SCRIPT_DIR%start_frontend.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Start Frontend Server'; $Shortcut.Save()"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%CD%\run_app.lnk'); $Shortcut.TargetPath = '%SCRIPT_DIR%run_app.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Start Both Servers'; $Shortcut.Save()"

echo.
echo Shortcuts created successfully:
echo   - start_backend.lnk
echo   - start_frontend.lnk
echo   - run_app.lnk
echo.
echo You can now double-click these shortcuts in the project root to start the servers.
pause

