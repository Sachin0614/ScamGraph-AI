@echo off
title ScamGraph AI - Threat Investigation Platform
echo ======================================================================
echo   Starting ScamGraph AI Platform (Real-Time Monitoring + Threat Graph)
echo ======================================================================
echo.
cd /d "%~dp0"

echo [*] Launching ScamGraph AI on http://localhost:8501
start http://localhost:8501
python run.py
pause
