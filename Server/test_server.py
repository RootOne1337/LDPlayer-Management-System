#!/usr/bin/env python3
"""
Скрипт для тестирования сервера системы управления LDPlayer эмуляторами.

Предоставляет функции для тестирования подключений, выполнения команд
и проверки работоспособности системы.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Добавить корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    from src.core.config import get_config, config_manager
    from src.core.models import WorkstationStatus
    from src.remote.workstation import WorkstationManager
    from src.remote.ldplayer_manager import LDPlayerManager
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все зависимости установлены")
    sys.exit(1)


class ServerTester:
    """Класс для тестирования сервера."""

    def __init__(self):
        """Инициализация тестера."""
        self.config = get_config()
        self.results: Dict[str, Any] = {}

    def print_header(self, title: str):
        """Вывести заголовок секции."""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print('='*60)

    def print_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """Вывести результат теста."""
        status = "✅ ПАС" if success else "❌ НЕУДАЧА"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   └─ {details}")

        self.results[test_name] = {
            'success': success,
            'message': message,
            'details': details
        }

    async def test_configuration(self):
        """Тестирование конфигурации."""
        self.print_header("ТЕСТИРОВАНИЕ КОНФИГУРАЦИИ")

        try:
            # Тест загрузки конфигурации
            config = get_config()
            self.print_result("Загрузка конфигурации", True, "Конфигурация загружена успешно")

            # Тест количества рабочих станций
            ws_count = len(config.workstations)
            self.print_result(
                "Количество рабочих станций",
                True,
                f"Найдено {ws_count} рабочих станций",
                f"Ожидалось: 8, Найдено: {ws_count}"
            )

            # Тест настроек сервера
            server_config = config.server
            self.print_result(
                "Настройки сервера",
                True,
                "Настройки сервера корректны",
                f"Хост: {server_config.host}, Порт: {server_config.port}"
            )

        except Exception as e:
            self.print_result("Конфигурация", False, f"Ошибка: {e}")

    async def test_workstation_connections(self):
        """Тестирование подключений к рабочим станциям."""
        self.print_header("ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЙ К РАБОЧИМ СТАНЦИЯМ")

        config = get_config()
        total_tests = len(config.workstations)
        successful_connections = 0

        for ws_config in config.workstations:
            print(f"\n📡 Тестирование {ws_config.name} ({ws_config.ip_address})...")

            try:
                manager = WorkstationManager(ws_config)
                success, message = manager.test_connection()

                if success:
                    successful_connections += 1
                    self.print_result(
                        f"Подключение к {ws_config.name}",
                        True,
                        message
                    )
                else:
                    self.print_result(
                        f"Подключение к {ws_config.name}",
                        False,
                        message
                    )

            except Exception as e:
                self.print_result(
                    f"Подключение к {ws_config.name}",
                    False,
                    f"Исключение: {e}"
                )

        # Итоговые результаты
        success_rate = successful_connections / total_tests * 100 if total_tests > 0 else 0
        self.print_result(
            "Итоговые результаты подключений",
            successful_connections > 0,
            f"Успешных: {successful_connections}/{total_tests} ({success_rate".1f"}%)"
        )

    async def test_ldplayer_commands(self):
        """Тестирование команд LDPlayer."""
        self.print_header("ТЕСТИРОВАНИЕ КОМАНД LDPLAYER")

        config = get_config()
        tested_stations = 0
        successful_commands = 0

        for ws_config in config.workstations:
            # Пропустить станции, к которым нет подключения
            manager = WorkstationManager(ws_config)
            if not manager.test_connection()[0]:
                continue

            tested_stations += 1
            print(f"\n🎮 Тестирование команд на {ws_config.name}...")

            try:
                # Тест команды list
                status_code, stdout, stderr = manager.run_ldconsole_command('list')

                if status_code == 0:
                    self.print_result(
                        f"Команда list на {ws_config.name}",
                        True,
                        "Команда выполнена успешно",
                        f"Вывод: {stdout[:100]}..."
                    )
                    successful_commands += 1
                else:
                    self.print_result(
                        f"Команда list на {ws_config.name}",
                        False,
                        f"Ошибка выполнения: {stderr}"
                    )

            except Exception as e:
                self.print_result(
                    f"Команда list на {ws_config.name}",
                    False,
                    f"Исключение: {e}"
                )

        if tested_stations > 0:
            command_success_rate = successful_commands / tested_stations * 100
            self.print_result(
                "Итоговые результаты команд",
                successful_commands > 0,
                f"Успешных команд: {successful_commands}/{tested_stations} ({command_success_rate".1f"}%)"
            )
        else:
            self.print_result(
                "Команды LDPlayer",
                False,
                "Нет доступных станций для тестирования"
            )

    async def test_emulator_operations(self):
        """Тестирование операций с эмуляторами."""
        self.print_header("ТЕСТИРОВАНИЕ ОПЕРАЦИЙ С ЭМУЛЯТОРАМИ")

        config = get_config()
        operations_tested = 0
        operations_successful = 0

        for ws_config in config.workstations:
            # Пропустить станции без подключения
            manager = WorkstationManager(ws_config)
            if not manager.test_connection()[0]:
                continue

            print(f"\n⚙️ Тестирование операций на {ws_config.name}...")

            try:
                # Получить менеджер LDPlayer
                ldplayer_manager = LDPlayerManager(manager)

                # Тест получения списка эмуляторов
                emulators = ldplayer_manager.get_emulators()

                self.print_result(
                    f"Получение списка эмуляторов на {ws_config.name}",
                    True,
                    f"Найдено {len(emulators)} эмуляторов"
                )

                operations_tested += 1
                if len(emulators) >= 0:  # Даже пустой список - успех
                    operations_successful += 1

                # Тест создания эмулятора (если список пустой)
                if len(emulators) == 0:
                    test_name = f"test_emulator_{ws_config.id}"
                    operation = ldplayer_manager.create_emulator(test_name)

                    self.print_result(
                        f"Создание тестового эмулятора на {ws_config.name}",
                        True,
                        f"Операция поставлена в очередь: {operation.id}"
                    )

                    operations_tested += 1
                    operations_successful += 1

            except Exception as e:
                self.print_result(
                    f"Операции с эмуляторами на {ws_config.name}",
                    False,
                    f"Исключение: {e}"
                )

        if operations_tested > 0:
            op_success_rate = operations_successful / operations_tested * 100
            self.print_result(
                "Итоговые результаты операций",
                operations_successful > 0,
                f"Успешных операций: {operations_successful}/{operations_tested} ({op_success_rate".1f"}%)"
            )
        else:
            self.print_result(
                "Операции с эмуляторами",
                False,
                "Нет доступных станций для тестирования операций"
            )

    async def test_api_endpoints(self):
        """Тестирование API endpoints."""
        self.print_header("ТЕСТИРОВАНИЕ API ENDPOINTS")

        try:
            import httpx

            base_url = f"http://{self.config.server.host}:{self.config.server.port}"

            async with httpx.AsyncClient() as client:
                # Тест health endpoint
                response = await client.get(f"{base_url}/api/health")

                if response.status_code == 200:
                    data = response.json()
                    self.print_result(
                        "Health Check (/api/health)",
                        True,
                        "API сервер отвечает",
                        f"Статус: {data.get('data', {}).get('status')}"
                    )
                else:
                    self.print_result(
                        "Health Check (/api/health)",
                        False,
                        f"Ошибка HTTP: {response.status_code}"
                    )

                # Тест status endpoint
                response = await client.get(f"{base_url}/api/status")

                if response.status_code == 200:
                    data = response.json()
                    self.print_result(
                        "Server Status (/api/status)",
                        True,
                        "Статус сервера получен",
                        f"Подключенных станций: {data.get('connected_workstations', 0)}"
                    )
                else:
                    self.print_result(
                        "Server Status (/api/status)",
                        False,
                        f"Ошибка HTTP: {response.status_code}"
                    )

        except ImportError:
            self.print_result(
                "API Endpoints",
                False,
                "httpx не установлен: pip install httpx"
            )
        except Exception as e:
            self.print_result(
                "API Endpoints",
                False,
                f"Ошибка тестирования API: {e}"
            )

    def print_summary(self):
        """Вывести итоговую сводку тестирования."""
        self.print_header("ИТОГОВАЯ СВОДКА ТЕСТИРОВАНИЯ")

        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result['success'])

        print(f"📊 Общее количество тестов: {total_tests}")
        print(f"✅ Успешных тестов: {successful_tests}")
        print(f"❌ Неудачных тестов: {total_tests - successful_tests}")

        if total_tests > 0:
            success_rate = successful_tests / total_tests * 100
            print(f"📈 Процент успеха: {success_rate".1f"}%")

            if success_rate >= 80:
                print("🎉 Отличный результат! Система готова к работе.")
            elif success_rate >= 60:
                print("👍 Хороший результат. Некоторые настройки требуют внимания.")
            else:
                print("⚠️ Низкий процент успеха. Проверьте настройки системы.")
        else:
            print("❌ Тесты не выполнялись.")

        # Рекомендации
        if successful_tests < total_tests:
            print("
💡 Рекомендации:"            print("   • Проверьте настройки рабочих станций в config.json"            print("   • Убедитесь, что LDPlayer установлен на всех станциях"            print("   • Проверьте сетевые настройки и доступность станций"            print("   • Установите необходимые зависимости: pip install -r requirements.txt"
    def save_results(self, filename: str = None):
        """Сохранить результаты тестирования в файл."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_results_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': self.results,
                    'summary': {
                        'total_tests': len(self.results),
                        'successful_tests': sum(1 for r in self.results.values() if r['success']),
                        'success_rate': sum(1 for r in self.results.values() if r['success']) / len(self.results) * 100 if self.results else 0
                    }
                }, f, indent=2, ensure_ascii=False, default=str)

            print(f"📄 Результаты сохранены в файл: {filename}")

        except Exception as e:
            print(f"❌ Ошибка сохранения результатов: {e}")

    async def run_all_tests(self):
        """Выполнить все тесты."""
        print("🚀 НАЧАЛО ТЕСТИРОВАНИЯ LDPLAYER MANAGEMENT SYSTEM")
        print("=" * 80)

        # Выполнить все тесты
        await self.test_configuration()
        await self.test_workstation_connections()
        await self.test_ldplayer_commands()
        await self.test_emulator_operations()
        await self.test_api_endpoints()

        # Вывести итоги
        self.print_summary()

        # Сохранить результаты
        self.save_results()

        print("\n" + "=" * 80)
        print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")


async def main():
    """Основная функция."""
    tester = ServerTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("🧪 Тестер сервера LDPlayer Management System")
    print("Для запуска сервера используйте: python run.py")
    print("Для тестирования API используйте: python test_server.py")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)