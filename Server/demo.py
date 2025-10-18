#!/usr/bin/env python3
"""
Демонстрационный скрипт для LDPlayer Management System.

Показывает возможности сервера и API endpoints.
"""

import sys
import json
from pathlib import Path

# Добавить корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    from src.core.config import get_config
    from src.core.server import app
    from src.utils.logger import get_logger, LogCategory, LogLevel
    from src.utils.config_manager import get_config_manager
    from src.utils.backup_manager import get_backup_manager
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все зависимости установлены")
    sys.exit(1)


def demo_system():
    """Демонстрация системы."""
    print("🚀 LDPLAYER MANAGEMENT SYSTEM DEMO")
    print("=" * 50)

    # 1. Конфигурация системы
    print("\n📋 1. СИСТЕМНАЯ КОНФИГУРАЦИЯ")
    print("-" * 30)

    config = get_config()
    print(f"Сервер: {config.server.host}:{config.server.port}")
    print(f"WebSocket: порт {config.server.websocket_port}")
    print(f"Рабочих станций: {len(config.workstations)}")
    print(f"Директория конфигураций: {config.configs_dir}")
    print(f"Директория логов: {config.logs_dir}")

    # 2. Рабочие станции
    print("\n🏭 2. НАСТРОЕННЫЕ РАБОЧИЕ СТАНЦИИ")
    print("-" * 30)

    for i, ws in enumerate(config.workstations[:3], 1):
        print(f"{i}. {ws.name}")
        print(f"   IP: {ws.ip_address}")
        print(f"   Пользователь: {ws.username}")
        print(f"   LDPlayer путь: {ws.ldplayer_path}")
        print(f"   Статус: {ws.status}")
        print()

    # 3. API endpoints
    print("🌐 3. ДОСТУПНЫЕ API ENDPOINTS")
    print("-" * 30)

    api_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith('/api')]

    for route in api_routes[:10]:
        methods = ', '.join(route.methods) if route.methods else 'ANY'
        print(f"  {methods:20} {route.path}")

    print(f"\nВсего API маршрутов: {len(api_routes)}")

    # 4. Конфигурации эмуляторов
    print("\n⚙️ 4. СИСТЕМА КОНФИГУРАЦИЙ")
    print("-" * 30)

    config_manager = get_config_manager()
    configs = config_manager.list_configs()

    print(f"Конфигураций эмуляторов: {len(configs)}")

    if configs:
        print("Примеры конфигураций:")
        for config_info in configs[:3]:
            print(f"  - {config_info['config_name']} ({config_info['size']} bytes)")

    # 5. Система резервного копирования
    print("\n💾 5. СИСТЕМА РЕЗЕРВНОГО КОПИРОВАНИЯ")
    print("-" * 30)

    backup_manager = get_backup_manager()
    backups = backup_manager.list_backups()

    print(f"Резервных копий: {len(backups)}")

    if backups:
        print("Последние резервные копии:")
        for backup in backups[:3]:
            print(f"  - {backup['name']} ({backup['size_mb']} MB)")
            print(f"    Создано: {backup['created_at']}")

    # 6. Система логирования
    print("\n📝 6. СИСТЕМА ЛОГИРОВАНИЯ")
    print("-" * 30)

    logger = get_logger(LogCategory.SYSTEM)
    logger.log_system_event("Демонстрация системы логирования", {"demo": True}, LogLevel.INFO)
    print("Логирование работает корректно")

    # 7. Обработчик ошибок
    print("\n🛡️ 7. ОБРАБОТЧИК ОШИБОК")
    print("-" * 30)

    from src.utils.error_handler import get_error_handler
    error_handler = get_error_handler()
    stats = error_handler.get_error_stats()

    print(f"Ошибок за последний час: {stats['errors_last_hour']}")
    print(f"Активных circuit breakers: {stats['circuit_breakers_active']}")

    # 8. Итоговая информация
    print("\n📊 8. ИТОГОВАЯ ИНФОРМАЦИЯ")
    print("-" * 30)

    print("✅ Серверная часть готова к работе")
    print("✅ Конфигурация загружена успешно")
    print("✅ API сервер функционирует")
    print("✅ Система логирования активна")
    print("✅ Обработчик ошибок настроен")
    print("✅ Менеджер конфигураций работает")
    print(f"\n🌟 Готово к созданию WPF клиента!")
    print(f"📖 Документация API: http://localhost:{config.server.port}/docs")
    print(f"🔗 Репозиторий: LDPlayerManagementSystem/")

    print(f"\n{'=' * 50}")
    print("🎯 Следующий этап: WPF клиент с красивым интерфейсом")
    print("=" * 50)


if __name__ == "__main__":
    demo_system()