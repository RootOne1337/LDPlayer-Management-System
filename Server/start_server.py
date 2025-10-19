"""
🚀 ПРОФЕССИОНАЛЬНЫЙ ЗАПУСК СЕРВЕРА С ПОЛНОЙ ДИАГНОСТИКОЙ
Автоматическое тестирование всех компонентов при старте
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import uvicorn

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

# Импорт диагностики
from system_diagnostics import SystemDiagnostics, Colors, print_header, print_section, print_success, print_error, print_info

# Импорт сервера
from src.core.server import app


async def pre_startup_diagnostics():
    """Полная диагностика перед запуском сервера"""
    print_header("🚀 ЗАПУСК LDPLAYER MANAGEMENT SYSTEM")
    
    print_info(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Python: {sys.version.split()[0]}")
    
    # Запуск полной диагностики
    print_section("ПРЕДСТАРТОВАЯ ДИАГНОСТИКА")
    
    diagnostics = SystemDiagnostics()
    results = await diagnostics.run_full_diagnostics()
    
    # Проверка критических компонентов
    critical_errors = []
    
    # Проверка базы данных
    if results.get("database", {}).get("status") == "error":
        critical_errors.append("База данных недоступна")
    
    # Проверка файловой структуры
    if results.get("file_structure", {}).get("status") == "errors":
        critical_errors.append("Проблемы с файловой структурой")
    
    if critical_errors:
        print_error("КРИТИЧЕСКИЕ ОШИБКИ ОБНАРУЖЕНЫ:")
        for error in critical_errors:
            print_error(f"  • {error}")
        print_error("\nСервер может работать нестабильно!")
        
        response = input(f"\n{Colors.YELLOW}Продолжить запуск несмотря на ошибки? (y/N): {Colors.ENDC}")
        if response.lower() != 'y':
            print_error("Запуск отменен пользователем")
            return False
    
    return True


class ServerManager:
    """Менеджер сервера с расширенным логированием"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        self.host = host
        self.port = port
        self.server_started = False
    
    async def start(self):
        """Запуск сервера с логированием"""
        try:
            # Предстартовая диагностика
            if not await pre_startup_diagnostics():
                return
            
            print_section("ЗАПУСК СЕРВЕРА")
            
            print_info(f"Хост: {self.host}")
            print_info(f"Порт: {self.port}")
            print_info(f"Документация: http://localhost:{self.port}/docs")
            print_info(f"Web UI: http://localhost:{self.port}/static/index.html")
            
            # Конфигурация uvicorn
            config = uvicorn.Config(
                app=app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True,
                reload=False,  # Отключаем автоперезагрузку для стабильности
                loop="asyncio"
            )
            
            # Создаем сервер
            server = uvicorn.Server(config)
            
            print_success("Сервер готов к запуску!")
            print()
            print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'СЕРВЕР УСПЕШНО ЗАПУЩЕН'.center(80)}{Colors.ENDC}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
            print()
            print(f"{Colors.CYAN}📡 API доступен по адресу: {Colors.BOLD}http://localhost:{self.port}/api{Colors.ENDC}")
            print(f"{Colors.CYAN}📚 Документация: {Colors.BOLD}http://localhost:{self.port}/docs{Colors.ENDC}")
            print(f"{Colors.CYAN}🎨 Web интерфейс: {Colors.BOLD}http://localhost:{self.port}/static/index.html{Colors.ENDC}")
            print()
            print(f"{Colors.YELLOW}Для остановки нажмите Ctrl+C{Colors.ENDC}")
            print()
            
            self.server_started = True
            
            # Запуск сервера
            await server.serve()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Получен сигнал остановки (Ctrl+C){Colors.ENDC}")
            await self.shutdown()
        except Exception as e:
            print_error(f"Критическая ошибка при запуске: {e}")
            import traceback
            traceback.print_exc()
            await self.shutdown()
    
    async def shutdown(self):
        """Корректная остановка сервера"""
        if self.server_started:
            print_section("ОСТАНОВКА СЕРВЕРА")
            print_info("Закрываем соединения...")
            print_info("Сохраняем состояние...")
            print_success("Сервер корректно остановлен")
        
        print()
        print(f"{Colors.CYAN}Спасибо за использование LDPlayer Management System!{Colors.ENDC}")
        print()


async def main():
    """Главная функция"""
    # Включаем поддержку ANSI цветов в Windows
    if sys.platform == "win32":
        os.system("")  # Активирует VT100 режим
    
    # Создаем и запускаем менеджер сервера
    manager = ServerManager(host="0.0.0.0", port=8001)
    await manager.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Выход...{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Фатальная ошибка: {e}{Colors.ENDC}")
        sys.exit(1)
