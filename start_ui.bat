@echo off
title Email Monitoring & Spam Protection Agent
echo ======================================================================
echo    EMAIL MONITORING & SPAM DETECTION AGENT - STARTING UI
echo ======================================================================
echo.
cd /d "%~dp0"

echo [*] Opening UI in browser: http://localhost:8501
start http://localhost:8501

echo [*] Starting Streamlit Server...
python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Could not start via run.py, trying direct streamlit...
    streamlit run src/scamgraph/app.py --server.port=8501 --server.address=localhost
)
pause
