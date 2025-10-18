@echo off
REM Quick launcher for Monitoring Dashboard
REM LDPlayer Management System

echo.
echo ========================================
echo   MONITORING DASHBOARD
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run dashboard
python dashboard_monitoring.py

pause
