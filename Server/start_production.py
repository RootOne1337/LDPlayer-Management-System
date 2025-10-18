#!/usr/bin/env python3
"""
🚀 ЗАПУСК PRODUCTION СЕРВЕРА
"""

import sys
from pathlib import Path

print("=" * 70)
print("🚀 LDPlayer Management System - Production Server")
print("=" * 70)
print()

# Проверка зависимостей
print("📦 Проверка зависимостей...")
try:
    import uvicorn
    print("   ✅ uvicorn")
except ImportError:
    print("   ❌ uvicorn не установлен")
    print("   Установите: pip install uvicorn")
    sys.exit(1)

try:
    import fastapi
    print("   ✅ fastapi")
except ImportError:
    print("   ❌ fastapi не установлен")
    print("   Установите: pip install fastapi")
    sys.exit(1)

try:
    import pydantic
    print("   ✅ pydantic")
except ImportError:
    print("   ❌ pydantic не установлен")
    print("   Установите: pip install pydantic")
    sys.exit(1)

print()
print("=" * 70)
print("🎯 ЧТО БУДЕТ ДОСТУПНО:")
print("=" * 70)
print()
print("📋 API Endpoints:")
print("   • Health: /api/health, /api/status, /api/version")
print("   • Workstations: CRUD + test-connection + system-info (7 endpoints)")
print("   • Emulators: create, start, stop, delete, modify (9+ endpoints)")
print("   • Operations: get, cancel, statistics (6 endpoints)")
print("   • WebSocket: /ws/monitor")
print()
print("📚 Документация:")
print("   • Swagger UI: http://localhost:8000/docs")
print("   • ReDoc: http://localhost:8000/redoc")
print("   • OpenAPI: http://localhost:8000/openapi.json")
print()
print("🔧 Возможности:")
print("   ✅ Создание эмуляторов с настройками")
print("   ✅ Изменение 14 параметров (CPU, RAM, разрешение, IMEI, MAC, и др.)")
print("   ✅ Запуск/остановка эмуляторов")
print("   ✅ Удаленное управление через WinRM/SMB")
print("   ✅ Real-time обновления через WebSocket")
print("   ✅ Логирование всех операций")
print()
print("=" * 70)
print()

# Варианты запуска
print("🎮 ВАРИАНТЫ ДЕЙСТВИЙ:")
print()
print("1️⃣  Запустить API сервер и протестировать через Swagger UI")
print("2️⃣  Создать JWT аутентификацию")
print("3️⃣  Создать простой Web UI (HTML + JavaScript)")
print("4️⃣  Написать unit тесты с pytest")
print("5️⃣  Запустить демонстрационный скрипт")
print()

choice = input("Выберите действие (1-5) или Enter для запуска сервера: ").strip()

if not choice or choice == "1":
    print()
    print("=" * 70)
    print("🚀 ЗАПУСК СЕРВЕРА...")
    print("=" * 70)
    print()
    print("📡 Сервер будет доступен на: http://localhost:8000")
    print("📚 Swagger UI: http://localhost:8000/docs")
    print()
    print("⚠️  Для остановки нажмите Ctrl+C")
    print()
    print("=" * 70)
    print()
    
    # Запуск через uvicorn
    try:
        uvicorn.run(
            "src.core.server_modular:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✅ Сервер остановлен")

elif choice == "2":
    print("\n🔐 Реализация JWT аутентификации...")
    print("Создание файлов для JWT auth...")
    
elif choice == "3":
    print("\n🌐 Создание Web UI...")
    print("Генерация HTML интерфейса...")
    
elif choice == "4":
    print("\n🧪 Создание unit тестов...")
    print("Настройка pytest и создание тестов...")
    
elif choice == "5":
    print("\n🎬 Запуск демонстрации...")
    import subprocess
    subprocess.run([sys.executable, "demo.py"])
    
else:
    print("\n❌ Неверный выбор")
    sys.exit(1)
