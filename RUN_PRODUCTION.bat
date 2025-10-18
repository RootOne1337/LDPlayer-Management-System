@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🚀 LDPLAYER MANAGEMENT - PRODUCTION
echo ========================================
echo.
echo Starting production version with full remote management...
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python app_production.py

pause
