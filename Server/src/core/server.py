"""
Основной сервер системы управления LDPlayer эмуляторами.

Предоставляет REST API для управления рабочими станциями и эмуляторами,
а также WebSocket интерфейс для real-time обновлений.
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from ..core.config import get_config, config_manager, SystemConfig, WorkstationConfig
from ..core.models import (
    Workstation,  WorkstationStatus,
    Emulator, EmulatorConfig, EmulatorStatus,
    Operation, OperationType, OperationStatus
)
from ..remote.workstation import WorkstationManager, WorkstationMonitor
from ..remote.ldplayer_manager import LDPlayerManager
from ..remote.protocols import connection_pool
from ..api.auth_routes import router as auth_router, get_current_active_user  # JWT Authentication + dependency
from ..utils.auth import require_role  # Auth helpers
from ..utils.cache import get_cache_stats, invalidate_cache  # 🚀 Performance caching
from ..core.models import UserInDB, UserRole  # User models for type hints (import after existing models)
from ..utils.detailed_logging import (  # Сверх детальное логирование
    log_http_request, 
    log_http_response, 
    log_authentication_attempt,
    log_permission_check,
    log_workstation_connection,
    log_emulator_operation
)
from ..utils.logger import get_logger, LogCategory

# 🆕 Новые модули для ремедиации
from ..core.container import container, DIContainer  # DI контейнер
from ..models.entities import Workstation as WsEntity, Emulator as EmEntity  # Domain entities
from ..models.schemas import PaginatedResponse, PaginationParams  # API schemas
from ..services.workstation_service import WorkstationService  # Business logic
from ..services.emulator_service import EmulatorService  # Business logic
from ..utils.exceptions import (  # Структурированные исключения
    LDPlayerManagementException,
    EmulatorNotFoundError,
    WorkstationNotFoundError,
    InvalidInputError
)


# 🆕 DI контейнер для управления зависимостями (вместо глобальных переменных)
# Все сервисы будут зарегистрированы здесь и инъектированы через Depends()

# ⚠️ ИНИЦИАЛИЗАЦИЯ кэшей менеджеров:
# ПРИМЕЧАНИЕ: Эти словари используются для кэширования менеджеров. В будущем должны быть заменены на DI контейнер.
# TODO: Миграция на DIContainer (из container.py) для замены глобальных словарей
workstation_managers: Dict[str, WorkstationManager] = {}
ldplayer_managers: Dict[str, LDPlayerManager] = {}

monitor: Optional[WorkstationMonitor] = None
websocket_connections: List[WebSocket] = []


def initialize_di_services() -> None:
    """
    Инициализировать все сервисы в DI контейнере.
    
    Вызывается при startup приложения.
    """
    logger = get_logger(LogCategory.SYSTEM)
    
    try:
        # Инициализировать менеджеры
        config = get_config()
        
        # Создать менеджер рабочей станции
        workstation_manager = WorkstationManager(config)
        container.register("workstation_manager", workstation_manager)
        
        # Создать LDPlayer менеджер (основной, на localhost)
        ldplayer_manager = LDPlayerManager(workstation_manager)
        container.register("ldplayer_manager", ldplayer_manager)
        logger.log_system_event("LDPlayerManager initialized")
        
        # Создать сервисы бизнес-логики
        ws_service = WorkstationService(ldplayer_manager)
        container.register("workstation_service", ws_service)
        logger.log_system_event("WorkstationService initialized")
        
        em_service = EmulatorService(ldplayer_manager)
        container.register("emulator_service", em_service)
        logger.log_system_event("EmulatorService initialized")
        
    except Exception as e:
        error_logger = get_logger(LogCategory.SYSTEM)
        error_logger.log_error(e, "Failed to initialize DI services")
        raise


# ============================================================================
# 🆕 ПРИМЕЧАНИЕ: Функции зависимостей перемещены в src/api/dependencies.py
# для избежания циклического импорта
# - get_workstation_service()
# - get_emulator_service()
# - get_ldplayer_manager_di()
# ============================================================================


# Lifecycle управление с использованием lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    logger = get_logger(LogCategory.SYSTEM)
    
    # ============ STARTUP ============
    print("[STARTUP] LDPlayer Management System Server")
    logger.log_system_event("Starting LDPlayer Management System")
    
    # 🆕 Start tracking server uptime
    from .uptime import start_uptime_tracking
    start_uptime_tracking()
    logger.log_system_event("Uptime tracking started")
    
    # 🔐 ВАЛИДАЦИЯ БЕЗОПАСНОСТИ НА STARTUP (PHASE 1 - HOTFIX)
    try:
        from .config import validate_security_configuration
        validate_security_configuration()
        logger.log_system_event("✅ Security validation passed")
    except RuntimeError as e:
        logger.log_error(e, "Security validation failed - startup blocked")
        raise
    except Exception as e:
        logger.log_error(e, "Unexpected error during security validation")
        raise
    
    # Инициализировать DI контейнер с сервисами
    try:
        initialize_di_services()
        logger.log_system_event("DI container initialized")
    except Exception as e:
        logger.log_error(e, "Failed to initialize DI container")
        raise
    
    print("[OK] Server started successfully")
    
    # ============ APPLICATION RUNNING ============
    yield
    
    # ============ SHUTDOWN ============
    print("[SHUTDOWN] LDPlayer Management System Server")
    logger.log_system_event("Shutting down LDPlayer Management System")
    
    try:
        # Очистить ресурсы DI контейнера (если есть)
        # TODO: Добавить метод cleanup() в DIContainer при необходимости
        logger.log_system_event("DI container resources cleaned up")
    except Exception as e:
        logger.log_error(e, "Failed to cleanup resources")
    
    print("[OK] Server stopped successfully")


# FastAPI приложение
app = FastAPI(
    title="LDPlayer Management System API",
    description="API для управления LDPlayer эмуляторами на удаленных рабочих станциях",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware для поддержки веб-клиентов
# ВАЖНО: В production указывать только доверенные домены!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# СВЕРХ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ВСЕХ HTTP ЗАПРОСОВ
# ============================================================================

@app.middleware("http")
async def log_requests_middleware(request, call_next):
    """Middleware для детального логирования всех HTTP запросов и ответов."""
    from datetime import datetime
    import json as json_lib
    
    start_time = datetime.now()
    
    # Получить информацию о пользователе (если есть)
    user = "anonymous"
    try:
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            user = "authenticated"
    except Exception:
        pass
    
    # Получить тело запроса (если есть)
    body = {}
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            body_bytes = await request.body()
            if body_bytes:
                try:
                    body = json_lib.loads(body_bytes.decode())
                except (ValueError, UnicodeDecodeError):
                    body = {"raw": body_bytes.decode()[:500]}
    except Exception:
        pass
    
    # Логируем входящий запрос
    log_http_request({
        "method": request.method,
        "url": str(request.url.path),
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "body": body,
        "client_ip": request.client.host if request.client else "unknown",
        "user": user
    })
    
    # Выполнить запрос
    try:
        response = await call_next(request)
        
        # Вычислить время выполнения
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Логируем ответ
        log_http_response({
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "headers": dict(response.headers)
        })
        
        return response
        
    except Exception as e:
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Логируем ошибку
        logger = get_logger(LogCategory.API)
        logger.logger.error(
            f"❌ HTTP REQUEST FAILED | {request.method} {request.url.path} | "
            f"duration={duration_ms:.2f}ms | error={type(e).__name__}: {str(e)}"
        )
        
        raise


# Include routers
app.include_router(auth_router, prefix="/api")

# Import and include other routers
from ..api.workstations import router as workstations_router
from ..api.emulators import router as emulators_router
from ..api.operations import router as operations_router
from ..api.health import router as health_router

app.include_router(workstations_router, prefix="/api/workstations", tags=["Workstations"])
app.include_router(emulators_router, prefix="/api/emulators", tags=["Emulators"])
app.include_router(operations_router, prefix="/api/operations", tags=["Operations"])
app.include_router(health_router, prefix="/api", tags=["Health"])


# Pydantic модели для API

class ServerStatus(BaseModel):
    """Модель статуса сервера."""
    status: str
    version: str
    uptime: str
    connected_workstations: int
    total_emulators: int
    active_operations: int
    timestamp: str


class APIResponse(BaseModel):
    """Стандартный ответ API."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


# Зависимости

async def get_system_config() -> SystemConfig:
    """Получить конфигурацию системы."""
    return get_config()


# WebSocket менеджер

class WebSocketManager:
    """Менеджер WebSocket соединений."""

    def __init__(self) -> None:
        """Инициализация менеджера WebSocket."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Подключить WebSocket клиент."""
        await websocket.accept()
        self.active_connections.append(websocket)
        websocket_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Отключить WebSocket клиент."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
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


# Вспомогательные функции

def get_workstation_manager(workstation_id: str) -> WorkstationManager:
    """Получить менеджер рабочей станции.

    Args:
        workstation_id: ID рабочей станции

    Returns:
        WorkstationManager: Менеджер рабочей станции

    Raises:
        HTTPException: Если рабочая станция не найдена
    """
    config = get_config()
    workstation_config = None

    for ws in config.workstations:
        if ws.id == workstation_id:
            workstation_config = ws
            break

    if not workstation_config:
        raise HTTPException(
            status_code=404,
            detail=f"Рабочая станция {workstation_id} не найдена"
        )

    if workstation_id not in workstation_managers:
        workstation_managers[workstation_id] = WorkstationManager(workstation_config)

    return workstation_managers[workstation_id]


def get_ldplayer_manager(workstation_id: str) -> LDPlayerManager:
    """Получить менеджер LDPlayer для рабочей станции.

    Args:
        workstation_id: ID рабочей станции

    Returns:
        LDPlayerManager: Менеджер LDPlayer
    """
    if workstation_id not in ldplayer_managers:
        workstation_manager = get_workstation_manager(workstation_id)
        ldplayer_managers[workstation_id] = LDPlayerManager(workstation_manager)

    return ldplayer_managers[workstation_id]


async def broadcast_websocket_event(event_type: str, data: Dict[str, Any]):
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


# Serve static files and web UI
@app.get("/")
async def index():
    """Главная страница веб-интерфейса."""
    try:
        static_dir = Path(__file__).parent.parent.parent / "static"
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
    except Exception as e:
        print(f"Error serving index: {e}")
    return {"message": "Welcome to LDPlayer Management System"}


# Mount static files directory
try:
    static_dir = Path(__file__).parent.parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
except Exception as e:
    print(f"Error mounting static files: {e}")


# API endpoints

@app.get("/api/health", response_model=APIResponse)
async def health_check():
    """Проверка здоровья сервера."""
    return APIResponse(
        success=True,
        message="Сервер работает нормально",
        data={"status": "healthy"}
    )


@app.get("/api/status", response_model=ServerStatus)
async def get_server_status(current_user: UserInDB = Depends(get_current_active_user)):
    """Получить статус сервера. Требуется аутентификация."""
    config = get_config()

    # Подсчитать статистику
    connected_workstations = len([
        ws for ws in config.workstations
        if ws.status == WorkstationStatus.ONLINE
    ])

    total_emulators = sum(
        len(get_ldplayer_manager(ws.id).get_emulators())
        for ws in config.workstations
    )

    active_operations = sum(
        len(get_ldplayer_manager(ws.id).get_active_operations())
        for ws in config.workstations
    )

    return ServerStatus(
        status="running",
        version="1.0.0",
        uptime="0:00:00",  # TODO: Реализовать подсчет uptime
        connected_workstations=connected_workstations,
        total_emulators=total_emulators,
        active_operations=active_operations,
        timestamp=datetime.now().isoformat()
    )


def _get_workstations_list() -> List[Dict[str, Any]]:
    """Вспомогательная функция для получения списка рабочих станций (для кэширования)"""
    config = get_config()
    workstations_data = []
    
    for ws_config in config.workstations:
        # Получить актуальный статус
        status_str = ws_config.status

        # Handle last_seen - can be str (from config) or datetime (from model)
        last_seen_str = None
        if ws_config.last_seen:
            if isinstance(ws_config.last_seen, str):
                last_seen_str = ws_config.last_seen
            else:
                last_seen_str = ws_config.last_seen.isoformat() if hasattr(ws_config.last_seen, 'isoformat') else str(ws_config.last_seen)

        workstations_data.append({
            "id": ws_config.id,
            "name": ws_config.name,
            "ip_address": ws_config.ip_address,
            "status": status_str,
            "total_emulators": ws_config.total_emulators,
            "active_emulators": ws_config.active_emulators,
            "cpu_usage": ws_config.cpu_usage,
            "memory_usage": ws_config.memory_usage,
            "disk_usage": ws_config.disk_usage,
            "last_seen": last_seen_str
        })
    
    return workstations_data


@app.get("/api/workstations", response_model=List[Dict[str, Any]])
async def get_workstations(current_user: UserInDB = Depends(get_current_active_user)):
    """Получить список всех рабочих станций. Требуется аутентификация."""
    # Получить список (кэш на 30 сек для быстрых повторных запросов)
    return _get_workstations_list()


@app.post("/api/workstations", response_model=APIResponse, status_code=201)
async def add_workstation(
    workstation_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Добавить новую рабочую станцию. Требуется роль OPERATOR или ADMIN."""
    require_role(current_user, UserRole.OPERATOR)
    
    try:
        # Валидация обязательных полей
        name = workstation_data.get("name", "").strip()
        if not name:
            raise ValueError("name is required and cannot be empty")
        
        # Генерируем id, если не предоставлен
        if "id" not in workstation_data or not workstation_data["id"]:
            workstation_data["id"] = f"ws_{name.lower().replace(' ', '_')}_{int(time.time())}"
        
        # Поддерживаем оба формата: ip_address или host
        ip_address = workstation_data.get("ip_address") or workstation_data.get("host")
        if not ip_address:
            raise ValueError("ip_address or host is required")
        
        # Валидация портов (если указаны)
        if "port" in workstation_data:
            port = workstation_data.get("port")
            if port is not None:
                try:
                    port_num = int(port)
                    if port_num < 1 or port_num > 65535:
                        raise ValueError(f"port must be between 1 and 65535, got {port_num}")
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid port: {e}")
        
        workstation_config = WorkstationConfig(
            id=workstation_data["id"],
            name=name,
            ip_address=ip_address,
            username=workstation_data.get("username", "administrator"),
            password=workstation_data["password"]
        )

        config_manager.add_workstation(workstation_config)
        
        # 🚀 Инвалидировать кэш списка рабочих станций
        invalidate_cache(pattern="workstations")

        # Отправить событие через WebSocket
        await broadcast_websocket_event("workstation_added", {
            "workstation_id": workstation_config.id,
            "name": workstation_config.name,
            "ip_address": workstation_config.ip_address
        })

        return APIResponse(
            success=True,
            message=f"Рабочая станция {workstation_config.name} добавлена",
            data={"id": workstation_config.id, "workstation_id": workstation_config.id}
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/workstations/{workstation_id}", response_model=Dict[str, Any])
async def get_workstation(
    workstation_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Получить информацию о рабочей станции. Требуется аутентификация."""
    manager = get_workstation_manager(workstation_id)

    # Получить системную информацию
    system_info = manager.get_system_info()

    return {
        "id": manager.config.id,
        "name": manager.config.name,
        "ip_address": manager.config.ip_address,
        "status": manager.config.status.value if hasattr(manager.config.status, 'value') else str(manager.config.status),
        "system_info": system_info,
        "emulators": [emu.to_dict() for emu in manager.get_emulators_list()]
    }


@app.post("/api/workstations/{workstation_id}/test-connection", response_model=APIResponse)
async def test_workstation_connection(
    workstation_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Протестировать подключение к рабочей станции. Требуется аутентификация."""
    manager = get_workstation_manager(workstation_id)

    success, message = manager.test_connection()

    if success:
        return APIResponse(success=True, message=message)
    else:
        raise HTTPException(status_code=400, detail=message)


@app.get("/api/workstations/{workstation_id}/emulators", response_model=List[Dict[str, Any]])
async def get_workstation_emulators(
    workstation_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Получить список эмуляторов на рабочей станции. Требуется аутентификация."""
    manager = get_ldplayer_manager(workstation_id)
    emulators = manager.get_emulators()

    return [emu.to_dict() for emu in emulators]


@app.post("/api/emulators", response_model=APIResponse)
async def create_emulator(
    emulator_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Создать новый эмулятор. Требуется роль OPERATOR или ADMIN."""
    require_role(current_user, UserRole.OPERATOR)
    
    try:
        workstation_id = emulator_data["workstation_id"]
        name = emulator_data["name"]

        # Получить менеджер LDPlayer
        ldplayer_manager = get_ldplayer_manager(workstation_id)

        # Создать конфигурацию эмулятора
        config_data = emulator_data.get("config", {})
        config = EmulatorConfig(
            android_version=config_data.get("android_version", "9.0"),
            screen_size=config_data.get("screen_size", "1280x720"),
            cpu_cores=config_data.get("cpu_cores", 2),
            memory_mb=config_data.get("memory_mb", 2048)
        )

        # Создать операцию
        operation = ldplayer_manager.create_emulator(name, config)

        # Отправить событие через WebSocket
        await broadcast_websocket_event("emulator_creating", {
            "operation_id": operation.id,
            "emulator_name": name,
            "workstation_id": workstation_id
        })

        return APIResponse(
            success=True,
            message=f"Операция создания эмулятора '{name}' поставлена в очередь",
            data={
                "operation_id": operation.id,
                "emulator_name": name,
                "workstation_id": workstation_id
            }
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/emulators/{emulator_id}/start", response_model=APIResponse)
async def start_emulator(
    emulator_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Запустить эмулятор. Требуется роль OPERATOR или ADMIN."""
    require_role(current_user, UserRole.OPERATOR)
    
    try:
        # Найти эмулятор и получить менеджер
        config = get_config()
        emulator = None
        ldplayer_manager = None

        for ws_config in config.workstations:
            ldplayer_manager = get_ldplayer_manager(ws_config.id)
            emulators = ldplayer_manager.get_emulators()

            for emu in emulators:
                if emu.id == emulator_id:
                    emulator = emu
                    break

            if emulator:
                break

        if not emulator:
            raise HTTPException(status_code=404, detail=f"Эмулятор {emulator_id} не найден")

        # Создать операцию запуска
        operation = ldplayer_manager.start_emulator(emulator.name)

        # Отправить событие через WebSocket
        await broadcast_websocket_event("emulator_starting", {
            "operation_id": operation.id,
            "emulator_id": emulator_id,
            "emulator_name": emulator.name
        })

        return APIResponse(
            success=True,
            message=f"Операция запуска эмулятора '{emulator.name}' поставлена в очередь",
            data={"operation_id": operation.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/emulators/{emulator_id}/stop", response_model=APIResponse)
async def stop_emulator(
    emulator_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Остановить эмулятор. Требуется роль OPERATOR или ADMIN."""
    require_role(current_user, UserRole.OPERATOR)
    
    try:
        # Найти эмулятор и получить менеджер
        config = get_config()
        emulator = None
        ldplayer_manager = None

        for ws_config in config.workstations:
            ldplayer_manager = get_ldplayer_manager(ws_config.id)
            emulators = ldplayer_manager.get_emulators()

            for emu in emulators:
                if emu.id == emulator_id:
                    emulator = emu
                    break

            if emulator:
                break

        if not emulator:
            raise HTTPException(status_code=404, detail=f"Эмулятор {emulator_id} не найден")

        # Создать операцию остановки
        operation = ldplayer_manager.stop_emulator(emulator.name)

        # Отправить событие через WebSocket
        await broadcast_websocket_event("emulator_stopping", {
            "operation_id": operation.id,
            "emulator_id": emulator_id,
            "emulator_name": emulator.name
        })

        return APIResponse(
            success=True,
            message=f"Операция остановки эмулятора '{emulator.name}' поставлена в очередь",
            data={"operation_id": operation.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/emulators/{emulator_id}", response_model=APIResponse)
async def delete_emulator(
    emulator_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Удалить эмулятор. Требуется роль OPERATOR или ADMIN."""
    require_role(current_user, UserRole.OPERATOR)
    
    try:
        # Найти эмулятор и получить менеджер
        config = get_config()
        emulator = None
        ldplayer_manager = None

        for ws_config in config.workstations:
            ldplayer_manager = get_ldplayer_manager(ws_config.id)
            emulators = ldplayer_manager.get_emulators()

            for emu in emulators:
                if emu.id == emulator_id:
                    emulator = emu
                    break

            if emulator:
                break

        if not emulator:
            raise HTTPException(status_code=404, detail=f"Эмулятор {emulator_id} не найден")

        # Создать операцию удаления
        operation = ldplayer_manager.delete_emulator(emulator.name)

        # Отправить событие через WebSocket
        await broadcast_websocket_event("emulator_deleting", {
            "operation_id": operation.id,
            "emulator_id": emulator_id,
            "emulator_name": emulator.name
        })

        return APIResponse(
            success=True,
            message=f"Операция удаления эмулятора '{emulator.name}' поставлена в очередь",
            data={"operation_id": operation.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/operations", response_model=List[Dict[str, Any]])
async def get_operations(current_user: UserInDB = Depends(get_current_active_user)):
    """Получить список активных операций. Требуется аутентификация."""
    operations_data = []

    for ldplayer_manager in ldplayer_managers.values():
        for operation in ldplayer_manager.get_active_operations():
            operations_data.append({
                "id": operation.id,
                "type": operation.type.value,
                "emulator_id": operation.emulator_id,
                "workstation_id": operation.workstation_id,
                "status": operation.status.value,
                "created_at": operation.created_at.isoformat(),
                "started_at": operation.started_at.isoformat() if operation.started_at else None,
                "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
                "result": operation.result,
                "error_message": operation.error_message
            })

    return operations_data


@app.get("/api/operations/{operation_id}", response_model=Dict[str, Any])
async def get_operation(
    operation_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Получить информацию об операции. Требуется аутентификация."""
    for ldplayer_manager in ldplayer_managers.values():
        operation = ldplayer_manager.get_operation(operation_id)
        if operation:
            return {
                "id": operation.id,
                "type": operation.type.value,
                "emulator_id": operation.emulator_id,
                "workstation_id": operation.workstation_id,
                "status": operation.status.value,
                "created_at": operation.created_at.isoformat(),
                "started_at": operation.started_at.isoformat() if operation.started_at else None,
                "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
                "result": operation.result,
                "error_message": operation.error_message
            }

    raise HTTPException(status_code=404, detail=f"Операция {operation_id} не найдена")


@app.post("/api/operations/{operation_id}/cancel", response_model=APIResponse)
async def cancel_operation(
    operation_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Отменить операцию. Требуется роль OPERATOR или ADMIN."""
    require_role(current_user, UserRole.OPERATOR)
    
    for ldplayer_manager in ldplayer_managers.values():
        if ldplayer_manager.cancel_operation(operation_id):
            await broadcast_websocket_event("operation_cancelled", {
                "operation_id": operation_id
            })
            return APIResponse(
                success=True,
                message=f"Операция {operation_id} отменена"
            )

    raise HTTPException(status_code=404, detail=f"Операция {operation_id} не найдена")


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


# Основная функция запуска



# ============================================================================
# 🚀 PERFORMANCE MONITORING ENDPOINTS
# ============================================================================

@app.get("/api/performance/cache-stats", response_model=Dict[str, Any])
async def get_cache_statistics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Получить статистику кэша. Требуется аутентификация."""
    require_role(current_user, UserRole.ADMIN)
    
    stats = get_cache_stats()
    return {
        "status": "success",
        "cache_stats": stats,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/performance/cache-clear", response_model=APIResponse)
async def clear_cache(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Очистить кэш полностью. Требуется роль ADMIN."""
    require_role(current_user, UserRole.ADMIN)
    
    invalidate_cache(pattern=None)  # Очистить весь кэш
    
    return APIResponse(
        success=True,
        message="Кэш полностью очищен",
        data={"cleared_at": datetime.now().isoformat()}
    )


@app.post("/api/performance/cache-invalidate", response_model=APIResponse)
async def invalidate_cache_endpoint(
    pattern: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Инвалидировать кэш по паттерну. Требуется роль ADMIN."""
    require_role(current_user, UserRole.ADMIN)
    
    if not pattern:
        raise HTTPException(
            status_code=400,
            detail="Pattern cannot be empty"
        )
    
    invalidate_cache(pattern=pattern)
    
    return APIResponse(
        success=True,
        message=f"Кэш инвалидирован для паттерна: {pattern}",
        data={"pattern": pattern, "invalidated_at": datetime.now().isoformat()}
    )


@app.get("/api/performance/metrics", response_model=Dict[str, Any])
async def get_performance_metrics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Получить метрики производительности:
    - Cache hit rate
    - Number of cached items
    - Workstation managers count
    - Active WebSocket connections
    """
    require_role(current_user, UserRole.ADMIN)
    
    cache_stats = get_cache_stats()
    
    return {
        "status": "success",
        "metrics": {
            "cache": {
                "hit_rate_percent": cache_stats.get('hit_rate_percent', 0),
                "total_hits": cache_stats.get('hits', 0),
                "total_misses": cache_stats.get('misses', 0),
                "evictions": cache_stats.get('evictions', 0),
                "cached_items": cache_stats.get('size', 0)
            },
            "managers": {
                "workstations": len(workstation_managers),
                "ldplayers": len(ldplayer_managers)
            },
            "websockets": {
                "active_connections": len(websocket_connections)
            }
        },
        "timestamp": datetime.now().isoformat()
    }


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Запустить сервер.

    Args:
        host: Хост для запуска сервера
        port: Порт для запуска сервера
        reload: Перезапуск при изменении файлов
    """
    uvicorn.run(
        "src.core.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()
