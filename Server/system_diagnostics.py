"""
🚀 СИСТЕМА МОЩНОЙ ДИАГНОСТИКИ
Полная проверка всех протоколов, подключений и компонентов системы
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import socket
import platform
import subprocess
import json
from typing import Dict, List, Tuple, Any

# Добавляем путь к src модулю
sys.path.insert(0, str(Path(__file__).parent))

# Цвета для консоли (Windows PowerShell поддерживает ANSI)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Красивый заголовок"""
    width = 80
    print(f"\n{Colors.CYAN}{'=' * width}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(width)}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'=' * width}{Colors.ENDC}\n")

def print_section(text: str):
    """Секция"""
    print(f"\n{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}📋 {text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'─' * 80}{Colors.ENDC}")

def print_success(text: str):
    """Успешный результат"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Ошибка"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Предупреждение"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    """Информация"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

def print_stat(label: str, value: str, status: str = "info"):
    """Статистика"""
    color = Colors.GREEN if status == "success" else Colors.YELLOW if status == "warning" else Colors.CYAN
    print(f"  {color}▪{Colors.ENDC} {label}: {Colors.BOLD}{value}{Colors.ENDC}")


class SystemDiagnostics:
    """Система полной диагностики"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "system": {},
            "protocols": {},
            "database": {},
            "network": {},
            "services": {}
        }
    
    async def run_full_diagnostics(self):
        """Запуск полной диагностики"""
        print_header("🚀 СИСТЕМА МОЩНОЙ ДИАГНОСТИКИ LDPlayer Management")
        
        print_info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"Python версия: {sys.version.split()[0]}")
        print_info(f"Платформа: {platform.platform()}")
        
        # 1. Системная информация
        await self.check_system_info()
        
        # 2. Проверка файловой структуры
        await self.check_file_structure()
        
        # 3. Проверка базы данных
        await self.check_database()
        
        # 4. Проверка сетевых протоколов
        await self.check_network_protocols()
        
        # 5. Проверка инструментов удаленного управления
        await self.check_remote_tools()
        
        # 6. Проверка ADB протокола
        await self.check_adb_protocol()
        
        # 7. Проверка LDPlayer
        await self.check_ldplayer()
        
        # 8. Финальная сводка
        self.print_final_summary()
        
        return self.results
    
    async def check_system_info(self):
        """Системная информация"""
        print_section("СИСТЕМНАЯ ИНФОРМАЦИЯ")
        
        try:
            # Операционная система
            os_info = {
                "platform": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": socket.gethostname()
            }
            
            self.results["system"] = os_info
            
            print_stat("ОС", f"{os_info['platform']} {os_info['release']}", "success")
            print_stat("Архитектура", os_info['architecture'], "success")
            print_stat("Процессор", os_info['processor'][:50], "info")
            print_stat("Имя хоста", os_info['hostname'], "success")
            
            # IP адреса
            hostname = socket.gethostname()
            try:
                ip_address = socket.gethostbyname(hostname)
                print_stat("IP адрес", ip_address, "success")
                self.results["system"]["ip_address"] = ip_address
            except:
                print_warning("Не удалось получить IP адрес")
            
            print_success("Системная информация получена")
            
        except Exception as e:
            print_error(f"Ошибка получения системной информации: {e}")
            self.results["system"]["error"] = str(e)
    
    async def check_file_structure(self):
        """Проверка файловой структуры"""
        print_section("ФАЙЛОВАЯ СТРУКТУРА")
        
        base_path = Path(__file__).parent
        required_paths = {
            "Конфигурация": base_path / "config.json",
            "База данных": base_path / "configs" / "workstations.db",
            "Логи": base_path / "logs",
            "Статика": base_path / "static",
            "Исходники": base_path / "src",
            "Ядро": base_path / "src" / "core",
            "API": base_path / "src" / "api",
            "Утилиты": base_path / "src" / "utils",
            "Удаленное управление": base_path / "src" / "remote"
        }
        
        structure_ok = True
        for name, path in required_paths.items():
            if path.exists():
                print_success(f"{name}: {path.name}")
            else:
                print_error(f"{name}: НЕ НАЙДЕНО - {path}")
                structure_ok = False
        
        self.results["file_structure"] = {
            "status": "ok" if structure_ok else "errors",
            "paths_checked": len(required_paths),
            "base_path": str(base_path)
        }
        
        if structure_ok:
            print_success("Файловая структура в порядке")
        else:
            print_warning("Обнаружены проблемы в файловой структуре")
    
    async def check_database(self):
        """Проверка базы данных"""
        print_section("БАЗА ДАННЫХ")
        
        try:
            from src.utils.config_manager import ConfigManager
            
            config_manager = ConfigManager()
            db_path = config_manager.db_path
            
            print_info(f"Путь к БД: {db_path}")
            
            if not db_path.exists():
                print_error("База данных не найдена!")
                self.results["database"]["status"] = "missing"
                return
            
            # Размер БД
            db_size = db_path.stat().st_size
            print_stat("Размер БД", f"{db_size:,} байт ({db_size / 1024:.2f} KB)", "success")
            
            # Подключение к БД
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Таблицы
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print_stat("Таблиц в БД", str(len(tables)), "success")
            
            # Статистика по каждой таблице
            stats = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count
                    print_stat(f"  └─ {table}", f"{count} записей", "info")
                except Exception as e:
                    print_warning(f"  └─ {table}: ошибка подсчета - {e}")
            
            conn.close()
            
            self.results["database"] = {
                "status": "ok",
                "path": str(db_path),
                "size_bytes": db_size,
                "tables": tables,
                "statistics": stats
            }
            
            print_success(f"База данных проверена: {sum(stats.values())} записей")
            
        except Exception as e:
            print_error(f"Ошибка проверки БД: {e}")
            self.results["database"] = {"status": "error", "error": str(e)}
    
    async def check_network_protocols(self):
        """Проверка сетевых протоколов"""
        print_section("СЕТЕВЫЕ ПРОТОКОЛЫ И ПОРТЫ")
        
        protocols = {
            "HTTP API": 8001,
            "ADB Start": 5555,
            "ADB End": 5585,
            "WinRM HTTP": 5985,
            "WinRM HTTPS": 5986,
            "SSH": 22,
            "SMB": 445
        }
        
        for name, port in protocols.items():
            try:
                # Проверка доступности порта
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', port))
                    
                    if result == 0:
                        print_success(f"{name} (порт {port}): ДОСТУПЕН")
                        self.results["network"][name] = {"port": port, "status": "available"}
                    else:
                        print_info(f"{name} (порт {port}): не используется")
                        self.results["network"][name] = {"port": port, "status": "unused"}
            except Exception as e:
                print_warning(f"{name} (порт {port}): ошибка проверки - {e}")
                self.results["network"][name] = {"port": port, "status": "error", "error": str(e)}
    
    async def check_remote_tools(self):
        """Проверка инструментов удаленного управления"""
        print_section("ИНСТРУМЕНТЫ УДАЛЕННОГО УПРАВЛЕНИЯ")
        
        tools = {
            "paramiko": "SSH подключения",
            "pywinrm": "Windows Remote Management",
            "smbprotocol": "SMB файловые операции"
        }
        
        for module, description in tools.items():
            try:
                __import__(module)
                print_success(f"{module}: установлен ({description})")
                self.results["protocols"][module] = {"status": "installed", "description": description}
            except ImportError:
                print_warning(f"{module}: НЕ УСТАНОВЛЕН ({description})")
                self.results["protocols"][module] = {"status": "missing", "description": description}
    
    async def check_adb_protocol(self):
        """Проверка ADB протокола"""
        print_section("ADB (ANDROID DEBUG BRIDGE)")
        
        try:
            # Проверка наличия adb.exe
            adb_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk" / "platform-tools" / "adb.exe",
                Path("C:/") / "Program Files (x86)" / "Android" / "android-sdk" / "platform-tools" / "adb.exe",
                Path("adb.exe")  # В PATH
            ]
            
            adb_found = False
            adb_path = None
            
            for path in adb_paths:
                if path.exists():
                    adb_found = True
                    adb_path = path
                    break
            
            if adb_found:
                print_success(f"ADB найден: {adb_path}")
                
                # Версия ADB
                try:
                    result = subprocess.run([str(adb_path), "version"], 
                                          capture_output=True, text=True, timeout=5)
                    version = result.stdout.split('\n')[0] if result.stdout else "неизвестно"
                    print_stat("Версия ADB", version, "success")
                    
                    # Список устройств
                    result = subprocess.run([str(adb_path), "devices"], 
                                          capture_output=True, text=True, timeout=5)
                    devices = [line for line in result.stdout.split('\n') if '\t' in line]
                    print_stat("Подключенных устройств", str(len(devices)), "info")
                    
                    self.results["protocols"]["adb"] = {
                        "status": "available",
                        "path": str(adb_path),
                        "version": version,
                        "devices": len(devices)
                    }
                    
                except Exception as e:
                    print_warning(f"ADB найден, но ошибка выполнения: {e}")
                    self.results["protocols"]["adb"] = {
                        "status": "found_but_error",
                        "path": str(adb_path),
                        "error": str(e)
                    }
            else:
                print_warning("ADB не найден в системе")
                print_info("ADB можно установить через Android SDK Platform Tools")
                self.results["protocols"]["adb"] = {"status": "not_found"}
                
        except Exception as e:
            print_error(f"Ошибка проверки ADB: {e}")
            self.results["protocols"]["adb"] = {"status": "error", "error": str(e)}
    
    async def check_ldplayer(self):
        """Проверка LDPlayer"""
        print_section("LDPLAYER ЭМУЛЯТОР")
        
        try:
            # Типичные пути установки LDPlayer
            ldplayer_paths = [
                Path("C:/") / "LDPlayer" / "LDPlayer4.0",
                Path("C:/") / "LDPlayer" / "LDPlayer9",
                Path("D:/") / "LDPlayer" / "LDPlayer4.0",
                Path("D:/") / "LDPlayer" / "LDPlayer9",
            ]
            
            ldconsole_found = False
            ldconsole_path = None
            
            for base_path in ldplayer_paths:
                ldconsole = base_path / "ldconsole.exe"
                if ldconsole.exists():
                    ldconsole_found = True
                    ldconsole_path = ldconsole
                    break
            
            if ldconsole_found:
                print_success(f"LDConsole найден: {ldconsole_path}")
                
                try:
                    # Список эмуляторов
                    result = subprocess.run([str(ldconsole_path), "list2"], 
                                          capture_output=True, text=True, timeout=10, 
                                          encoding='utf-8', errors='ignore')
                    
                    emulators = []
                    for line in result.stdout.split('\n'):
                        if ',' in line:
                            parts = line.split(',')
                            if len(parts) >= 2:
                                emulators.append({
                                    "index": parts[0],
                                    "name": parts[1]
                                })
                    
                    print_stat("Локальных эмуляторов", str(len(emulators)), "success")
                    
                    for emu in emulators[:5]:  # Показываем первые 5
                        print_info(f"  └─ {emu['name']} (index: {emu['index']})")
                    
                    if len(emulators) > 5:
                        print_info(f"  └─ ... и еще {len(emulators) - 5}")
                    
                    self.results["services"]["ldplayer"] = {
                        "status": "available",
                        "path": str(ldconsole_path),
                        "emulators_count": len(emulators),
                        "emulators": emulators[:10]  # Первые 10 в результаты
                    }
                    
                except Exception as e:
                    print_warning(f"LDConsole найден, но ошибка выполнения: {e}")
                    self.results["services"]["ldplayer"] = {
                        "status": "found_but_error",
                        "path": str(ldconsole_path),
                        "error": str(e)
                    }
            else:
                print_warning("LDPlayer не найден на локальной машине")
                print_info("Можно управлять удаленными эмуляторами через рабочие станции")
                self.results["services"]["ldplayer"] = {"status": "not_found_locally"}
                
        except Exception as e:
            print_error(f"Ошибка проверки LDPlayer: {e}")
            self.results["services"]["ldplayer"] = {"status": "error", "error": str(e)}
    
    def print_final_summary(self):
        """Финальная сводка"""
        print_section("ФИНАЛЬНАЯ СВОДКА")
        
        # Подсчет статусов
        total_checks = 0
        passed_checks = 0
        warnings = 0
        errors = 0
        
        # Анализ результатов
        for category, data in self.results.items():
            if category == "timestamp":
                continue
            
            if isinstance(data, dict):
                for key, value in data.items():
                    total_checks += 1
                    if isinstance(value, dict):
                        status = value.get("status", "unknown")
                        if status in ["ok", "available", "installed", "success"]:
                            passed_checks += 1
                        elif status in ["warning", "unused", "not_found", "missing"]:
                            warnings += 1
                        elif status in ["error", "errors"]:
                            errors += 1
        
        # Статистика
        print(f"\n{Colors.BOLD}Статистика проверок:{Colors.ENDC}")
        print_stat("Всего проверок", str(total_checks), "info")
        print_stat("Успешно", str(passed_checks), "success")
        print_stat("Предупреждений", str(warnings), "warning")
        print_stat("Ошибок", str(errors), "warning" if errors == 0 else "error")
        
        # Общий статус
        if errors == 0 and warnings < 3:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ СИСТЕМА ГОТОВА К РАБОТЕ{Colors.ENDC}")
        elif errors == 0:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  СИСТЕМА РАБОТАЕТ С ПРЕДУПРЕЖДЕНИЯМИ{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ПРОБЛЕМЫ{Colors.ENDC}")
        
        # Рекомендации
        print(f"\n{Colors.CYAN}{Colors.BOLD}Рекомендации:{Colors.ENDC}")
        
        if self.results.get("protocols", {}).get("adb", {}).get("status") == "not_found":
            print_info("• Установите Android SDK Platform Tools для ADB поддержки")
        
        if self.results.get("services", {}).get("ldplayer", {}).get("status") == "not_found_locally":
            print_info("• LDPlayer не найден локально, используйте удаленное управление")
        
        if self.results.get("protocols", {}).get("paramiko", {}).get("status") == "missing":
            print_info("• Установите paramiko: pip install paramiko")
        
        if self.results.get("protocols", {}).get("pywinrm", {}).get("status") == "missing":
            print_info("• Установите pywinrm: pip install pywinrm")
        
        print()
        print_header("ДИАГНОСТИКА ЗАВЕРШЕНА")


async def main():
    """Главная функция"""
    try:
        # Включаем поддержку ANSI цветов в Windows
        if platform.system() == "Windows":
            os.system("")  # Активирует VT100 режим в Windows 10+
        
        diagnostics = SystemDiagnostics()
        results = await diagnostics.run_full_diagnostics()
        
        # Сохранение результатов
        report_path = Path(__file__).parent / "logs" / f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print_info(f"\nОтчет сохранен: {report_path}")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Диагностика прервана пользователем{Colors.ENDC}")
        return 1
    except Exception as e:
        print_error(f"\nКритическая ошибка диагностики: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
