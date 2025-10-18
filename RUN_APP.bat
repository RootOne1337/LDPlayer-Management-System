@echo off
REM LDPlayer Management System - Desktop App Launcher

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════╗
echo ║  LDPlayer Management System - Desktop  ║
echo ║  Запуск приложения...                  ║
echo ╚════════════════════════════════════════╝
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python app_desktop.py

pause
