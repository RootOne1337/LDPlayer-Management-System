"""
Основной сервер системы управления LDPlayer эмуляторами.

Модульная версия с разделенными API роутами.
"""

import asyncio
import json
from datetime import datetime
from typing import List
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import get_config
from .models import WorkstationStatus
from ..api import (
    health_router,
    workstations_router,
    emulators_router,
    operations_router
)
from ..api.dependencies import workstation_managers, ldplayer_managers
from ..remote.workstation import WorkstationMonitor
from ..remote.protocols import connection_pool
from ..utils.logger import get_logger, LogCategory
from ..utils.secrets_manager import ConfigEncryption


# Logger
logger = get_logger(LogCategory.SYSTEM)

# FastAPI приложение
app = FastAPI(
    title="LDPlayer Management System API",
    description="API для управления LDPlayer эмуляторами на удаленных рабочих станциях",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware для поддержки веб-клиентов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключить роутеры
app.include_router(health_router)
app.include_router(workstations_router)
app.include_router(emulators_router)
app.include_router(operations_router)

# Глобальные переменные
monitor: WorkstationMonitor = None
websocket_connections: List[WebSocket] = []


# WebSocket менеджер
class WebSocketManager:
    """Менеджер WebSocket соединений."""

    def __init__(self):
        """Инициализация менеджера WebSocket."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Подключить WebSocket клиент."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Отключить WebSocket клиент."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Отправить сообщение всем подключенным клиентам."""
        if not self.active_connections:
            return

        message_json = json.dumps(message, default=str, ensure_ascii=False)

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.append(connection)

        # Удалить отключенные соединения
        for connection in disconnected:
            self.disconnect(connection)


# Глобальный WebSocket менеджер
websocket_manager = WebSocketManager()


async def broadcast_websocket_event(event_type: str, data: dict):
    """Отправить событие через WebSocket.

    Args:
        event_type: Тип события
        data: Данные события
    """
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

    await websocket_manager.broadcast(event)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time обновлений."""
    await websocket_manager.connect(websocket)

    try:
        while True:
            # Ожидать сообщения от клиента
            data = await websocket.receive_text()

            # Обработать сообщение если нужно
            try:
                message = json.loads(data)
                # Здесь можно добавить обработку команд от клиента
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


# Фоновые задачи
async def start_monitoring():
    """Запустить мониторинг рабочих станций."""
    global monitor

    config = get_config()
    managers = []

    # Создать менеджеры для всех рабочих станций
    for ws_config in config.workstations:
        from ..remote.workstation import WorkstationManager
        if ws_config.id not in workstation_managers:
            workstation_managers[ws_config.id] = WorkstationManager(ws_config)
        managers.append(workstation_managers[ws_config.id])

    if managers:
        monitor = WorkstationMonitor(managers)
        await monitor.start_monitoring()
        logger.log_system_event("Мониторинг рабочих станций запущен", {"count": len(managers)})


async def stop_monitoring():
    """Остановить мониторинг рабочих станций."""
    global monitor

    if monitor:
        await monitor.stop_monitoring()
        monitor = None
        logger.log_system_event("Мониторинг рабочих станций остановлен", {})


async def start_operation_processors():
    """Запустить обработчики операций для всех менеджеров."""
    for ws_id, ldplayer_manager in ldplayer_managers.items():
        asyncio.create_task(ldplayer_manager.start_operation_processor())
        logger.log_system_event(
            f"Запущен обработчик операций для станции {ws_id}",
            {"workstation_id": ws_id}
        )


# Lifecycle события
@app.on_event("startup")
async def startup_event():
    """Действия при запуске сервера."""
    import os
    
    logger.log_system_event("🚀 Запуск LDPlayer Management System Server", {})

    try:
        # ===== Шифрование конфигурации =====
        config_path = Path("config.json")
        encrypted_config_path = Path("config.encrypted.json")
        
        # Проверить, нужно ли шифровать конфиг
        if config_path.exists():
            logger.log_system_event("🔐 Инициализация шифрования конфигурации...", {})
            try:
                config_encryptor = ConfigEncryption(str(config_path))
                
                # Зашифровать конфиг
                config_encryptor.encrypt_config(str(encrypted_config_path))
                logger.log_system_event(
                    "✅ Конфигурация зашифрована успешно",
                    {"encrypted_config": str(encrypted_config_path)}
                )
                
                # Установить переменную окружения для использования зашифрованного конфига
                os.environ["ENCRYPTED_CONFIG"] = str(encrypted_config_path)
                
            except Exception as e:
                logger.log_system_event(
                    f"⚠️  Ошибка шифрования конфигурации: {e}",
                    {"error": str(e)}
                )
        
        # Загрузить конфигурацию
        config = get_config()
        logger.log_system_event(
            f"Конфигурация загружена: {len(config.workstations)} рабочих станций",
            {"workstations_count": len(config.workstations)}
        )

        # Проверить, включен ли режим разработки (БЕЗ удаленного мониторинга)
        dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        
        if not dev_mode:
            # Запустить мониторинг (только в продакшен режиме)
            await start_monitoring()

            # Запустить обработчики операций
            await start_operation_processors()
            
            logger.log_system_event("✅ Сервер успешно запущен с мониторингом", {})
        else:
            logger.log_system_event("✅ Сервер успешно запущен в DEV режиме (БЕЗ мониторинга)", {})

    except Exception as e:
        logger.log_system_event(f"❌ Ошибка запуска сервера: {e}", {"error": str(e)})
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке сервера."""
    logger.log_system_event("🛑 Остановка LDPlayer Management System Server", {})

    try:
        # Остановить мониторинг
        await stop_monitoring()

        # Закрыть все подключения
        connection_pool.cleanup()

        # Отключить все WebSocket соединения
        for ws in websocket_manager.active_connections:
            await ws.close()

        logger.log_system_event("✅ Сервер успешно остановлен", {})

    except Exception as e:
        logger.log_system_event(f"❌ Ошибка остановки сервера: {e}", {"error": str(e)})


# Основная функция запуска
def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False, ssl_certfile: str = None, ssl_keyfile: str = None):
    """Запустить сервер.

    Args:
        host: Хост для запуска сервера
        port: Порт для запуска сервера
        reload: Перезапуск при изменении файлов
        ssl_certfile: Путь до SSL сертификата
        ssl_keyfile: Путь до SSL приватного ключа
    """
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile
    )


if __name__ == "__main__":
    config = get_config()
    run_server(
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload
    )
