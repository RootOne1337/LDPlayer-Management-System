"""
API роуты для health checks и статуса сервера.
"""

import os
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Any

from ..core.config import get_system_config, SystemConfig
from ..core.uptime import get_uptime_formatted  # 🆕 Uptime tracking
from .dependencies import get_logger_dependency, handle_api_errors
from ..utils.logger import LogCategory
from ..utils.mock_data import get_mock_system_status


router = APIRouter(prefix="/api", tags=["health"])


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


@router.get("/health", response_model=APIResponse)
@handle_api_errors(LogCategory.SYSTEM)
async def health_check():
    """Проверка здоровья сервера.
    
    Returns:
        APIResponse с статусом healthy
    """
    return APIResponse(
        success=True,
        message="Сервер работает нормально",
        data={"status": "healthy"}
    )


@router.get("/status", response_model=ServerStatus)
@handle_api_errors(LogCategory.SYSTEM)
async def get_server_status(config: SystemConfig = Depends(get_system_config)):
    """Получить статус сервера.
    
    Returns:
        ServerStatus с подробной информацией о состоянии системы
    """
    from ..core.models import WorkstationStatus
    from .dependencies import workstation_managers, ldplayer_managers

    # Подсчитать статистику
    connected_workstations = len([
        ws for ws in config.workstations
        if ws.status == "online"
    ])

    total_emulators = 0
    active_operations = 0

    try:
        for ws_id in workstation_managers.keys():
            if ws_id in ldplayer_managers:
                ldplayer_manager = ldplayer_managers[ws_id]
                total_emulators += len(ldplayer_manager.get_emulators())
                active_operations += len(ldplayer_manager.get_active_operations())
    except (KeyError, AttributeError, TypeError) as e:
        logger_api.log_error(f"Failed to count emulators/operations: {e}")
        # Use defaults if counting fails
        total_emulators = 0
        active_operations = 0
    except Exception as e:
        logger_api.log_error(f"Unexpected error in health check stats: {e}", exc_info=True)
        total_emulators = 0
        active_operations = 0

    return ServerStatus(
        status="running",
        version="1.0.0",
        uptime=get_uptime_formatted(),  # ✅ FIXED: Now returns actual uptime!
        connected_workstations=connected_workstations,
        total_emulators=total_emulators,
        active_operations=active_operations,
        timestamp=datetime.now().isoformat()
    )


@router.get("/version")
async def get_version():
    """Получить версию API."""
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "build_date": "2025-10-17"
    }
