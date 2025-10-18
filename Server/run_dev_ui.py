"""
Упрощенный сервер для разработки Web UI.
БЕЗ удаленного мониторинга workstations.
"""

import os
import uvicorn
import sys
from pathlib import Path

# Установить DEV_MODE перед импортом приложения
os.environ["DEV_MODE"] = "true"

# Добавить src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.core.server_modular import app

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 ЗАПУСК СЕРВЕРА ДЛЯ РАЗРАБОТКИ WEB UI")
    print("=" * 80)
    print("\n⚠️  DEV MODE: БЕЗ удаленного мониторинга workstations")
    print("Используется для быстрого тестирования Web UI\n")
    print("Backend: http://localhost:8000 (HTTP для разработки)")
    print("Frontend: http://localhost:3000")
    print("Swagger: http://localhost:8000/docs")
    print("\nЛогин: admin")
    print("Пароль: admin123")
    print("=" * 80)
    print()
    
    # Запуск сервера с DEV_MODE (БЕЗ SSL для упрощения)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        # Без SSL в dev режиме для упрощения
        log_level="warning",  # Меньше логов
        access_log=False  # Отключить access logs
    )
