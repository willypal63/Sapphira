@echo off
SETLOCAL ENABLEEXTENSIONS

REM === Project paths ===
SET ROOT_DIR=%~dp0
SET VENV_DIR=%ROOT_DIR%\.venv
SET MAIN_SCRIPT=%ROOT_DIR%main.py

REM === One‐time setup if venv is missing ===
IF NOT EXIST "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Virtual environment not found – running one‐time setup…

    REM 1) Create .venv
    py -3 -m venv "%VENV_DIR%"

    REM 2) Activate it
    call "%VENV_DIR%\Scripts\activate.bat"

    REM 3) Upgrade pip, setuptools, wheel
    pip install --upgrade pip setuptools wheel

    REM 4) Pin & install numpy
    set "NUMPY_VERSION=1.24.4"
    pip install --no-cache-dir --force-reinstall numpy==%NUMPY_VERSION%

    REM 5) Install the rest of your requirements
    pip install --no-cache-dir --force-reinstall -r "%ROOT_DIR%requirements.txt"

    REM 6) Rebuild key C-extensions from source
    pip install --no-binary=:all: sentence-transformers llama_cpp

    REM 7) Clean caches
    pip cache purge
    for /d /r "%ROOT_DIR%" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

    echo [INFO] One‐time setup complete.
) ELSE (
    REM If it’s already there, just activate
    call "%VENV_DIR%\Scripts\activate.bat"
)

REM === Launch your bot ===
echo [INFO] Launching assistant…
python "%MAIN_SCRIPT%"

ENDLOCAL
pause

