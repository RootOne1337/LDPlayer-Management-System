@echo off
REM LDPlayer Management System - Pro Edition Launcher

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════╗
echo ║  LDPlayer Management PRO               ║
echo ║  Professional Desktop Application      ║
echo ╚════════════════════════════════════════╝
echo.
echo Loading...
echo.

call venv\Scripts\activate.bat
python app_desktop_pro.py

pause
