@echo off
echo [INFO] Starting Sapphira in OFFLINE mode...

SET ROOT_DIR=%~dp0
SET VENV_DIR=%ROOT_DIR%\.venv
SET MAIN_SCRIPT=%ROOT_DIR%main.py

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate environment.
    pause
    exit /b
)

echo [INFO] Launching bot...
python "%MAIN_SCRIPT%"

echo.
echo [INFO] Bot exited. Press any key to close...
pause

