@echo off
chcp 65001 >nul
color 0B
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         🧪 LDPLAYER AUTO TEST - ALL FEATURES               ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Запускаю автоматический тест всех функций...
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

python test_all_features.py

echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
