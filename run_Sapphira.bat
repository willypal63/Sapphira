@echo off
REM ───────────────────────────────────────────────────────────────────────
REM  run_Sapphira.bat — Launches Sapphira from the project directory
REM ───────────────────────────────────────────────────────────────────────


REM Ensure we’re in the script’s directory
cd /d "%~dp0"

REM Enable cuBLAS support for llama-cpp-python (GPU offload)
set LLAMA_CUBLAS=1

REM Launch Sapphira with any passed arguments (e.g. --model auto)
python sapphira.py %*

pause