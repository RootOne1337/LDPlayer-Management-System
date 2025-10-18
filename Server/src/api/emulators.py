"""
API роуты для управления эмуляторами.
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..core.models import EmulatorConfig, Emulator, OperationType
from ..core.config import get_system_config, SystemConfig
from .dependencies import get_emulator_service, verify_token  # 🆕 Updated import location
from ..utils.logger import get_logger, LogCategory
from ..utils.mock_data import get_mock_emulators, get_mock_emulator
from ..services.emulator_service import EmulatorService  # 🆕 New service
from ..utils.validators import validate_pagination_params, validate_emulator_name, validate_emulator_config  # ✅ NEW
from ..utils.constants import ErrorMessage, OperationStatus  # ✅ NEW


router = APIRouter(prefix="/api/emulators", tags=["emulators"])
logger = get_logger(LogCategory.EMULATOR)


class EmulatorCreateRequest(BaseModel):
    """Модель запроса на создание эмулятора."""
    workstation_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None


class EmulatorActionRequest(BaseModel):
    """Модель запроса на действие с эмулятором."""
    workstation_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class EmulatorRenameRequest(BaseModel):
    """Модель запроса на переименование эмулятора."""
    workstation_id: str = Field(..., min_length=1)
    old_name: str = Field(..., min_length=1)
    new_name: str = Field(..., min_length=1)


class APIResponse(BaseModel):
    """Стандартный ответ API."""
    success: bool
    message: str
    data: Any = None
    error: str = None


@router.get("")
async def get_all_emulators(
    skip: int = 0,
    limit: int = 100,
    service: EmulatorService = Depends(get_emulator_service)
) -> Dict[str, Any]:
    """Получить список эмуляторов с пагинацией.
    
    Args:
        skip: Сколько пропустить (по умолчанию 0)
        limit: Максимум элементов (по умолчанию 100, максимум 1000)
        
    Returns:
        Словарь с списком эмуляторов и информацией о пагинации
    """
    try:
        # Валидация пагинации
        skip, limit = validate_pagination_params(skip, limit)
        
        # Получить все эмуляторы через сервис
        emulators, _ = await service.get_all(limit=limit + skip, offset=0)
        
        # Применить пагинацию
        total_count = len(emulators)
        paginated = emulators[skip : skip + limit]
        
        return {
            "data": [emu.to_dict() for emu in paginated],
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "returned": len(paginated),
                "has_more": (skip + limit) < total_count
            }
        }
    except Exception as e:
        logger.log_error(f"Ошибка получения эмуляторов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения эмуляторов: {str(e)}"
        )


@router.post("", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_emulator(
    request: EmulatorCreateRequest,
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Создать новый эмулятор.
    
    Args:
        request: Данные для создания эмулятора
        current_user: Аутентифицированный пользователь
        
    Returns:
        APIResponse с информацией об операции
        
    Raises:
        HTTPException: 404 если станция не найдена, 400 если некорректные данные, 500 при ошибке
    """
    try:
        # Создать эмулятор через сервис
        new_emu = await service.create({
            "workstation_id": request.workstation_id,
            "name": request.name,
            "config": request.config or {}
        })

        logger.log_system_event(
            f"Создан эмулятор '{request.name}'",
            {
                "workstation_id": request.workstation_id,
                "emulator_name": request.name,
                "emulator_id": new_emu.id
            }
        )

        return APIResponse(
            success=True,
            message=f"Эмулятор '{request.name}' создан",
            data=new_emu.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(f"Ошибка создания эмулятора '{request.name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания эмулятора: {str(e)}"
        )


@router.get("/{emulator_id}")
async def get_emulator(
    emulator_id: str,
    service: EmulatorService = Depends(get_emulator_service)
) -> Dict[str, Any]:
    """Получить информацию об эмуляторе."""
    try:
        emu = await service.get_by_id(emulator_id)
        
        if not emu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Эмулятор {emulator_id} не найден"
            )
        
        return emu.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(f"Ошибка получения эмулятора {emulator_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения эмулятора: {str(e)}"
        )


@router.post("/{emulator_id}/start", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_emulator(
    emulator_id: str,
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Запустить эмулятор."""
    try:
        logger.log_system_event(
            f"Запуск эмулятора '{emulator_id}'",
            {"emulator_id": emulator_id}
        )
        
        # Call real service method to queue operation
        result = await service.start(emulator_id)
        
        return APIResponse(
            success=True,
            message=f"Операция запуска эмулятора '{emulator_id}' поставлена в очередь",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(f"Ошибка запуска эмулятора: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{emulator_id}/stop", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def stop_emulator(
    emulator_id: str,
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Остановить эмулятор."""
    try:
        logger.log_system_event(
            f"Остановка эмулятора '{emulator_id}'",
            {"emulator_id": emulator_id}
        )
        
        # Call real service method to queue operation
        result = await service.stop(emulator_id)
        
        return APIResponse(
            success=True,
            message=f"Операция остановки эмулятора '{emulator_id}' поставлена в очередь",
            data=result
        )

    except Exception as e:
        logger.log_error(f"Ошибка остановки эмулятора: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{emulator_id}", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def delete_emulator(
    emulator_id: str,
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Удалить эмулятор."""
    try:
        logger.log_system_event(
            f"Удаление эмулятора '{emulator_id}'",
            {"emulator_id": emulator_id}
        )
        
        # Call real service method to queue operation
        result = await service.delete(emulator_id)
        
        return APIResponse(
            success=True,
            message=f"Операция удаления эмулятора '{emulator_id}' поставлена в очередь",
            data=result
        )

    except Exception as e:
        logger.log_error(f"Ошибка удаления эмулятора: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/rename", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def rename_emulator(
    request: EmulatorRenameRequest,
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Переименовать эмулятор."""
    try:
        logger.log_system_event(
            f"Переименование эмулятора '{request.old_name}' -> '{request.new_name}'",
            {"workstation_id": request.workstation_id}
        )
        
        # Call real service method to queue operation
        result = await service.rename(request.old_name, request.new_name)
        
        return APIResponse(
            success=True,
            message=f"Операция переименования эмулятора с '{request.old_name}' на '{request.new_name}' поставлена в очередь",
            data=result
        )

    except Exception as e:
        logger.log_error(f"Ошибка переименования эмулятора: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/batch-start", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def batch_start_emulators(
    workstation_id: str,
    emulator_names: List[str],
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Запустить несколько эмуляторов одновременно."""
    try:
        logger.log_system_event(
            f"Batch запуск {len(emulator_names)} эмуляторов",
            {"workstation_id": workstation_id, "count": len(emulator_names)}
        )
        
        # Call real service method to queue batch operation
        result = await service.batch_start(emulator_names)
        
        return APIResponse(
            success=True,
            message=f"Запущено {len(emulator_names)} операций запуска",
            data=result
        )

    except Exception as e:
        logger.log_error(f"Ошибка batch запуска: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/batch-stop", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def batch_stop_emulators(
    workstation_id: str,
    emulator_names: List[str],
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Остановить несколько эмуляторов одновременно."""
    try:
        logger.log_system_event(
            f"Batch остановка {len(emulator_names)} эмуляторов",
            {"workstation_id": workstation_id, "count": len(emulator_names)}
        )
        
        # Call real service method to queue batch operation
        result = await service.batch_stop(emulator_names)
        
        return APIResponse(
            success=True,
            message=f"Запущено {len(emulator_names)} операций остановки",
            data=result
        )

    except Exception as e:
        logger.log_error(f"Ошибка batch остановки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
