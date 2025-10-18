#!/usr/bin/env python3
"""
Скрипт установки и настройки сервера LDPlayer Management System.

Автоматически устанавливает зависимости, создает конфигурацию
и подготавливает систему к запуску.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple


class ServerSetup:
    """Класс для установки и настройки сервера."""

    def __init__(self):
        """Инициализация установщика."""
        self.root_dir = Path(__file__).parent
        self.requirements_file = self.root_dir / "requirements.txt"
        self.config_file = self.root_dir / "config.json"

    def print_step(self, step: str, status: str = "🔄"):
        """Вывести шаг установки."""
        print(f"{status} {step}")

    def run_command(self, command: List[str], shell: bool = False) -> Tuple[int, str, str]:
        """Выполнить системную команду."""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def check_python_version(self) -> bool:
        """Проверить версию Python."""
        self.print_step("Проверка версии Python")

        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.print_step(f"Версия Python: {version.major}.{version.minor}.{version.micro}", "✅")
            return True
        else:
            self.print_step(f"Требуется Python 3.8+, установлена версия: {version.major}.{version.minor}", "❌")
            return False

    def install_dependencies(self) -> bool:
        """Установить Python зависимости."""
        self.print_step("Установка Python зависимостей")

        if not self.requirements_file.exists():
            self.print_step("Файл requirements.txt не найден", "❌")
            return False

        # Проверка наличия pip
        code, _, _ = self.run_command([sys.executable, "-m", "pip", "--version"])
        if code != 0:
            self.print_step("pip не найден", "❌")
            return False

        # Установка зависимостей
        code, stdout, stderr = self.run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])

        if code == 0:
            self.print_step("Зависимости установлены успешно", "✅")
            return True
        else:
            self.print_step(f"Ошибка установки зависимостей: {stderr}", "❌")
            return False

    def create_directories(self) -> bool:
        """Создать необходимые директории."""
        self.print_step("Создание директорий проекта")

        directories = [
            "configs",
            "logs",
            "backups",
            "src/core",
            "src/remote",
            "src/api",
            "src/utils"
        ]

        try:
            for dir_name in directories:
                dir_path = self.root_dir / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)

            self.print_step("Директории созданы успешно", "✅")
            return True

        except Exception as e:
            self.print_step(f"Ошибка создания директорий: {e}", "❌")
            return False

    def create_config_file(self) -> bool:
        """Создать файл конфигурации."""
        self.print_step("Создание файла конфигурации")

        if self.config_file.exists():
            self.print_step("Файл конфигурации уже существует", "✅")
            return True

        # Пример конфигурации
        config_data = {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True,
                "reload": True,
                "websocket_port": 8001,
                "log_level": "INFO",
                "log_file": "logs/server.log",
                "database_url": "sqlite:///./ldplayer_manager.db",
                "secret_key": "your-secret-key-change-in-production",
                "access_token_expire_minutes": 30
            },
            "workstations": [
                {
                    "id": f"ws_{i+1"03d"}",
                    "name": f"Рабочая станция {i+1}",
                    "ip_address": f"192.168.1.{101+i}",
                    "username": "administrator",
                    "password": "your_password_here",
                    "domain": "",
                    "ldplayer_path": "C:\\LDPlayer\\LDPlayer9.0",
                    "ldconsole_path": "C:\\LDPlayer\\LDPlayer9.0\\ldconsole.exe",
                    "configs_path": "C:\\LDPlayer\\LDPlayer9.0\\customizeConfigs",
                    "smb_enabled": True,
                    "powershell_remoting_enabled": True,
                    "winrm_port": 5985,
                    "monitoring_enabled": True,
                    "monitoring_interval": 30,
                    "status": "unknown",
                    "last_seen": None
                }
                for i in range(8)
            ],
            "system": {
                "base_dir": str(self.root_dir),
                "configs_dir": str(self.root_dir / "configs"),
                "logs_dir": str(self.root_dir / "logs"),
                "backups_dir": str(self.root_dir / "backups"),
                "backup_enabled": True,
                "backup_interval": 3600,
                "max_backups": 10,
                "global_monitoring": True,
                "alert_thresholds": {
                    "cpu_usage": 80.0,
                    "memory_usage": 85.0,
                    "disk_usage": 90.0
                }
            }
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.print_step("Файл конфигурации создан успешно", "✅")
            self.print_step("Не забудьте изменить пароли в config.json!", "⚠️")
            return True

        except Exception as e:
            self.print_step(f"Ошибка создания конфигурации: {e}", "❌")
            return False

    def create_init_files(self) -> bool:
        """Создать __init__.py файлы."""
        self.print_step("Создание __init__.py файлов")

        init_files = [
            "src/__init__.py",
            "src/core/__init__.py",
            "src/remote/__init__.py",
            "src/api/__init__.py",
            "src/utils/__init__.py"
        ]

        try:
            for init_file in init_files:
                init_path = self.root_dir / init_file
                if not init_path.exists():
                    init_path.parent.mkdir(parents=True, exist_ok=True)
                    init_path.write_text('"""\nLDPlayer Management System - Server\n"""\n')

            self.print_step("__init__.py файлы созданы успешно", "✅")
            return True

        except Exception as e:
            self.print_step(f"Ошибка создания __init__.py файлов: {e}", "❌")
            return False

    def test_installation(self) -> bool:
        """Протестировать установку."""
        self.print_step("Тестирование установки")

        try:
            # Тест импорта основных модулей
            from src.core.config import get_config
            from src.core.models import Emulator, Workstation

            # Тест загрузки конфигурации
            config = get_config()

            self.print_step("Тестирование прошло успешно", "✅")
            self.print_step(f"Найдено рабочих станций: {len(config.workstations)}", "ℹ️")
            return True

        except ImportError as e:
            self.print_step(f"Ошибка импорта модулей: {e}", "❌")
            return False
        except Exception as e:
            self.print_step(f"Ошибка тестирования: {e}", "❌")
            return False

    def show_next_steps(self):
        """Показать следующие шаги после установки."""
        print(f"\n{'='*60}")
        print("🎉 УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        print('='*60)

        print("\n📋 Следующие шаги:")
        print("1. 📝 Измените пароли в файле config.json")
        print("2. 🔧 Настройте IP адреса рабочих станций")
        print("3. 🚀 Запустите сервер: python run.py")
        print("4. 🌐 Откройте браузер: http://localhost:8000/docs")
        print("5. 🧪 Протестируйте систему: python test_server.py")

        print("\n🔗 Важные файлы:")
        print(f"   Конфигурация: {self.config_file}")
        print(f"   Документация API: http://localhost:{self.config.server.port}/docs")
        print("   Логи сервера: logs/server.log"

        print("\n💡 Команды для управления:")
        print("   Запуск сервера: python run.py")
        print("   Тестирование: python test_server.py")
        print("   Создание конфигурации: python run.py --create-config")
        print("   Проверка станций: python run.py --list-workstations")

        print(f"\n{'='*60}")

    def run_setup(self) -> bool:
        """Выполнить полную установку."""
        print("🚀 НАЧАЛО УСТАНОВКИ LDPLAYER MANAGEMENT SYSTEM")
        print("=" * 60)

        steps = [
            ("Проверка версии Python", self.check_python_version),
            ("Создание директорий", self.create_directories),
            ("Создание __init__.py файлов", self.create_init_files),
            ("Создание файла конфигурации", self.create_config_file),
            ("Установка зависимостей", self.install_dependencies),
            ("Тестирование установки", self.test_installation),
        ]

        success_count = 0

        for step_name, step_func in steps:
            try:
                if step_func():
                    success_count += 1
                else:
                    self.print_step(f"{step_name} - НЕУДАЧА", "❌")
            except Exception as e:
                self.print_step(f"{step_name} - ИСКЛЮЧЕНИЕ: {e}", "❌")

        # Показать результаты
        total_steps = len(steps)
        print(f"\n📊 РЕЗУЛЬТАТЫ УСТАНОВКИ:")
        print(f"✅ Успешных шагов: {success_count}/{total_steps}")

        if success_count == total_steps:
            self.show_next_steps()
            return True
        else:
            print("
❌ УСТАНОВКА ЗАВЕРШЕНА С ОШИБКАМИ"            print("Проверьте ошибки выше и повторите установку"            return False


def main():
    """Основная функция."""
    setup = ServerSetup()

    print("🔧 LDPlayer Management System - Мастер установки")
    print("Этот скрипт поможет установить и настроить сервер управления LDPlayer")

    try:
        success = setup.run_setup()
        if success:
            print("\n✅ Система готова к использованию!")
            return 0
        else:
            print("\n❌ Установка завершена с ошибками")
            return 1

    except KeyboardInterrupt:
        print("\n\n🛑 Установка прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Критическая ошибка установки: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())