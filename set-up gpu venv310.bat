@echo off
:: Change working dir to script location to avoid missing files
cd /d "%~dp0"

:: setup_gpu_venv310.bat
:: Auto-creates Python 3.10 GPU-ready venv for llama-cpp-python

SETLOCAL

:: === [1] Correct Python 3.10 path === ::
SET PY310="C:\Users\willi\AppData\Local\Programs\Python\python-3.10.5\python.exe"

:: === [2] Delete existing broken venv === ::
IF EXIST .venv310 rmdir /s /q .venv310

:: === [3] Create fresh venv === ::
%PY310% -m venv .venv310

:: === [4] Activate it === ::
CALL .venv310\Scripts\activate.bat

:: === [5] Ensure pip works === ::
python -m ensurepip --upgrade

:: === [6] Install all dependencies === ::
pip install -r requirements.txt
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu129

:: === [7] Run verify script === ::
python verify_gpu.py

pause