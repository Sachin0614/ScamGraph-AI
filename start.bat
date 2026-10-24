@echo off
title ScamGraph AI - Threat Investigation Platform
echo ======================================================================
echo   Starting ScamGraph AI Platform (Backend + Interactive 3D Frontend)
echo ======================================================================

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [*] Launching ScamGraph AI on http://localhost:8000
start http://localhost:8000
"%PYTHON_EXE%" run.py
pause
