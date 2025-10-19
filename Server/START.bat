@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: 🚀 ПРОФЕССИОНАЛЬНЫЙ ЗАПУСК LDPLAYER MANAGEMENT SYSTEM
:: С полной диагностикой и супер-логированием

cls
echo.
echo ================================================================================
echo                    🚀 LDPLAYER MANAGEMENT SYSTEM 🚀
echo ================================================================================
echo.
echo [%time%] Подготовка к запуску...
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ОШИБКА: Python не найден!
    echo Установите Python 3.8+ и добавьте его в PATH
    pause
    exit /b 1
)

echo ✅ Python обнаружен
python --version

:: Переход в директорию сервера
cd /d "%~dp0"
echo ✅ Рабочая директория: %cd%

:: Установка кодировки UTF-8
set PYTHONIOENCODING=utf-8

:: Проверка зависимостей
echo.
echo [%time%] Проверка зависимостей...
python -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Некоторые зависимости отсутствуют
    echo 📦 Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей!
        pause
        exit /b 1
    )
) else (
    echo ✅ Все зависимости установлены
)

:: Очистка старых процессов
echo.
echo [%time%] Очистка старых процессов Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: Создание директорий
if not exist "logs" mkdir logs
if not exist "configs" mkdir configs
if not exist "backups" mkdir backups
echo ✅ Директории подготовлены

:: Запуск сервера с диагностикой
echo.
echo ================================================================================
echo                       🎯 ЗАПУСК СЕРВЕРА С ДИАГНОСТИКОЙ
echo ================================================================================
echo.
echo 📡 API будет доступен по адресу: http://localhost:8001/api
echo 📚 Документация: http://localhost:8001/docs
echo 🎨 Web интерфейс: http://localhost:8001/static/index.html
echo.
echo ⚠️  Для остановки нажмите Ctrl+C
echo.
echo ================================================================================
echo.

:: Запуск с полной диагностикой
python start_server.py

:: Обработка завершения
echo.
echo.
echo ================================================================================
echo                          📊 СЕРВЕР ОСТАНОВЛЕН
echo ================================================================================
echo.
echo [%time%] Сервер корректно завершил работу
echo.
pause
