"""
API роуты для управления рабочими станциями.
Требуют JWT аутентификацию.
"""

import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..core.config import get_system_config, SystemConfig, config_manager, WorkstationConfig
from ..core.models import WorkstationStatus
from ..core.exceptions import (
    WorkstationException, WorkstationNotFoundError, WorkstationConnectionError,
    WorkstationCommandError, ValidationException, InvalidWorkstationConfig
)
from .dependencies import get_workstation_service, get_emulator_service, verify_token
from ..utils.logger import get_logger, LogCategory
from ..utils.mock_data import get_mock_workstations, get_mock_emulators
from ..services.workstation_service import WorkstationService
from ..services.emulator_service import EmulatorService
from ..utils.validators import validate_pagination_params, validate_workstation_name, validate_ip_address
from ..utils.constants import ErrorMessage, OperationStatus


router = APIRouter(prefix="/api/workstations", tags=["workstations"])
logger = get_logger(LogCategory.API)


class WorkstationCreate(BaseModel):
    """Модель для создания рабочей станции."""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: str = Field(..., pattern=r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    username: str = "administrator"
    password: str = Field(..., min_length=1)
    ldplayer_path: str = r"C:\LDPlayer\LDPlayer9.0"


class APIResponse(BaseModel):
    """Стандартный ответ API."""
    success: bool
    message: str
    data: Any = None
    error: str = None


@router.get("")
async def get_workstations(
    skip: int = 0,
    limit: int = 100,
    service: WorkstationService = Depends(get_workstation_service),
    config: SystemConfig = Depends(get_system_config)
) -> Dict[str, Any]:
    """Получить список рабочих станций с пагинацией.
    
    Args:
        skip: Сколько пропустить (по умолчанию 0)
        limit: Максимум элементов (по умолчанию 100, максимум 1000)
        
    Returns:
        Словарь со списком рабочих станций и информацией о пагинации
    """
    try:
        # Валидация пагинации
        from src.utils.validators import validate_pagination_params
        skip, limit = validate_pagination_params(skip, limit)
        
        workstations_data = []
    
        # Получить все рабочие станции через сервис
        workstations, _ = await service.get_all(limit=1000, offset=0)
        
        total_count = len(workstations)
        paginated = workstations[skip : skip + limit]
        
        for ws in paginated:
            workstations_data.append(ws.to_dict())

        return {
            "data": workstations_data,
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "returned": len(paginated),
                "has_more": (skip + limit) < total_count
            }
        }
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        logger.log_error(f"Failed to get workstations - data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workstation data"
        )
    except WorkstationException as e:
        logger.log_error(f"Workstation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workstation error: {e.message}"
        )
    except Exception as e:
        logger.log_error(f"Unexpected error getting workstations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workstations"
        )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def add_workstation(
    workstation_data: WorkstationCreate,
    service: WorkstationService = Depends(get_workstation_service),
    current_user: str = Depends(verify_token)
):
    """Добавить новую рабочую станцию.
    
    **Требуется JWT аутентификация**
    """
    try:
        # Создать новую рабочую станцию через сервис
        new_ws = await service.create({
            "id": workstation_data.id,
            "name": workstation_data.name,
            "ip_address": workstation_data.ip_address,
            "username": workstation_data.username,
            "password": workstation_data.password,
            "ldplayer_path": workstation_data.ldplayer_path,
        })

        logger.log_system_event(
            f"Добавлена рабочая станция: {workstation_data.name}",
            {"workstation_id": workstation_data.id}
        )

        return APIResponse(
            success=True,
            message=f"Рабочая станция '{workstation_data.name}' добавлена",
            data={"workstation_id": new_ws.id}
        )

    except Exception as e:
        logger.log_error(f"Ошибка при добавлении рабочей станции: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{workstation_id}")
async def get_workstation(
    workstation_id: str,
    service: WorkstationService = Depends(get_workstation_service)
) -> Dict[str, Any]:
    """Получить информацию о рабочей станции.
    
    Args:
        workstation_id: ID рабочей станции
        
    Returns:
        Dict с информацией о рабочей станции
        
    Raises:
        HTTPException: 404 если станция не найдена, 500 если ошибка получения данных
    """
    try:
        # Получить рабочую станцию через сервис
        ws = await service.get_by_id(workstation_id)
        
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рабочая станция '{workstation_id}' не найдена"
            )
        
        return ws.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(f"Ошибка получения информации о станции {workstation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения информации о рабочей станции: {str(e)}"
        )


@router.delete("/{workstation_id}", response_model=APIResponse)
async def remove_workstation(
    workstation_id: str,
    service: WorkstationService = Depends(get_workstation_service),
    current_user: str = Depends(verify_token)
):
    """Удалить рабочую станцию."""
    try:
        # Получить станцию перед удалением для логирования
        ws = await service.get_by_id(workstation_id)
        
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рабочая станция {workstation_id} не найдена"
            )

        # Удалить через сервис
        success = await service.delete(workstation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Не удалось удалить рабочую станцию {workstation_id}"
            )

        logger.log_system_event(
            f"Удалена рабочая станция: {ws.name}",
            {"workstation_id": workstation_id}
        )

        return APIResponse(
            success=True,
            message=f"Рабочая станция '{ws.name}' удалена"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(f"Ошибка удаления рабочей станции: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{workstation_id}/test-connection", response_model=APIResponse)
async def test_workstation_connection(
    workstation_id: str,
    service: WorkstationService = Depends(get_workstation_service),
    current_user: str = Depends(verify_token)
):
    """Протестировать подключение к рабочей станции."""
    try:
        ws = await service.get_or_fail(workstation_id)
        
        # ✅ FIXED: Call test_connection method to diagnose connection
        result = await service.test_connection(workstation_id)
        
        logger.log_system_event(
            f"Connection test for {ws.name}: {result['status']}",
            {"workstation_id": workstation_id, "result": result}
        )
        
        return APIResponse(
            success=result["connected"],
            message=f"Connection test completed: {result['status']}",
            data=result
        )
        
    except WorkstationNotFoundError as e:
        logger.log_error(f"Workstation not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workstation not found: {workstation_id}"
        )
    except Exception as e:
        logger.log_error(f"Connection test error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )
        logger.log_error(f"Тест подключения к {workstation_id} неудачен: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get("/{workstation_id}/emulators")
async def get_workstation_emulators(
    workstation_id: str,
    emulator_service: EmulatorService = Depends(get_emulator_service)
) -> List[Dict[str, Any]]:
    """Получить список эмуляторов на рабочей станции."""
    try:
        # Получить эмуляторы для конкретной рабочей станции через сервис
        emulators = await emulator_service.get_by_workstation(workstation_id)
        return [emu.to_dict() for emu in emulators]
    except Exception as e:
        logger.log_error(f"Ошибка получения эмуляторов станции {workstation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения эмуляторов: {str(e)}"
        )


@router.get("/{workstation_id}/system-info")
async def get_workstation_system_info(
    workstation_id: str,
    service: WorkstationService = Depends(get_workstation_service)
) -> Dict[str, Any]:
    """Получить системную информацию о рабочей станции."""
    try:
        ws = await service.get_or_fail(workstation_id)
        # TODO: Добавить метод get_system_info в WorkstationService
        return ws.to_dict()
    except Exception as e:
        logger.log_error(f"Ошибка получения системной информации станции {workstation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения информации: {str(e)}"
        )
