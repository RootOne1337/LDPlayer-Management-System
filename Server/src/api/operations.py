"""
API роуты для управления операциями.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.config import get_system_config, SystemConfig
from .dependencies import (
    get_ldplayer_manager, 
    ldplayer_managers, 
    verify_token,
    handle_api_errors,
    validate_workstation_exists
)
from ..utils.logger import get_logger, LogCategory
from ..utils.validators import validate_pagination_params, validate_operation_type  # ✅ NEW
from ..utils.constants import ErrorMessage, OperationStatus, OperationType  # ✅ NEW


router = APIRouter(prefix="/api/operations", tags=["operations"])
logger = get_logger(LogCategory.OPERATION)


class APIResponse(BaseModel):
    """Стандартный ответ API."""
    success: bool
    message: str
    data: Any = None
    error: str = None


@router.get("")
@handle_api_errors(LogCategory.OPERATION)
async def get_operations(config: SystemConfig = Depends(get_system_config)) -> List[Dict[str, Any]]:
    """Получить список всех активных операций.
    
    Returns:
        List[Dict]: Список операций со всех workstations
    """
    operations_data = []

    for ws_config in config.workstations:
        if ws_config.id in ldplayer_managers:
            ldplayer_manager = ldplayer_managers[ws_config.id]
            operations = ldplayer_manager.get_active_operations()

            for operation in operations:
                operations_data.append({
                    "id": operation.id,
                    "type": operation.type.value,
                    "emulator_id": operation.emulator_id,
                    "workstation_id": operation.workstation_id,
                    "workstation_name": ws_config.name,
                    "status": operation.status.value,
                    "created_at": operation.created_at.isoformat(),
                    "started_at": operation.started_at.isoformat() if operation.started_at else None,
                    "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
                    "result": operation.result,
                    "error_message": operation.error_message,
                    "parameters": operation.parameters
                })

    return operations_data


@router.get("/{operation_id}")
@handle_api_errors(LogCategory.OPERATION)
async def get_operation(operation_id: str, config: SystemConfig = Depends(get_system_config)) -> Dict[str, Any]:
    """Получить информацию об операции.
    
    Args:
        operation_id: ID операции
        
    Returns:
        Dict с информацией об операции
        
    Raises:
        HTTPException: 404 если операция не найдена
    """
    # Найти операцию на всех рабочих станциях
    for ws_config in config.workstations:
        if ws_config.id not in ldplayer_managers:
            continue

        ldplayer_manager = ldplayer_managers[ws_config.id]
        operation = ldplayer_manager.get_operation(operation_id)

        if operation:
            return {
                "id": operation.id,
                "type": operation.type.value,
                "emulator_id": operation.emulator_id,
                "workstation_id": operation.workstation_id,
                "workstation_name": ws_config.name,
                "status": operation.status.value,
                "created_at": operation.created_at.isoformat(),
                "started_at": operation.started_at.isoformat() if operation.started_at else None,
                "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
                "result": operation.result,
                "error_message": operation.error_message,
                "parameters": operation.parameters
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Операция '{operation_id}' не найдена"
    )


@router.post("/{operation_id}/cancel", response_model=APIResponse)
async def cancel_operation(operation_id: str, config: SystemConfig = Depends(get_system_config), current_user: str = Depends(verify_token)):
    """Отменить операцию."""
    # Найти и отменить операцию на всех рабочих станциях
    for ws_config in config.workstations:
        try:
            if ws_config.id not in ldplayer_managers:
                continue

            ldplayer_manager = ldplayer_managers[ws_config.id]

            if ldplayer_manager.cancel_operation(operation_id):
                logger.log_system_event(
                    f"Операция {operation_id} отменена",
                    {"operation_id": operation_id, "workstation_id": ws_config.id}
                )

                return APIResponse(
                    success=True,
                    message=f"Операция {operation_id} отменена"
                )

        except Exception:
            continue

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Операция {operation_id} не найдена"
    )


@router.get("/workstation/{workstation_id}")
async def get_workstation_operations(workstation_id: str) -> List[Dict[str, Any]]:
    """Получить список операций для конкретной рабочей станции."""
    if workstation_id not in ldplayer_managers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Менеджер для рабочей станции {workstation_id} не найден"
        )

    try:
        ldplayer_manager = ldplayer_managers[workstation_id]
        operations = ldplayer_manager.get_active_operations()

        operations_data = []
        for operation in operations:
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
                "error_message": operation.error_message,
                "parameters": operation.parameters
            })

        return operations_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/summary")
async def get_operations_stats(config: SystemConfig = Depends(get_system_config)) -> Dict[str, Any]:
    """Получить статистику по операциям."""
    stats = {
        "total_operations": 0,
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
        "by_workstation": {}
    }

    for ws_config in config.workstations:
        try:
            if ws_config.id not in ldplayer_managers:
                continue

            ldplayer_manager = ldplayer_managers[ws_config.id]
            operations = ldplayer_manager.get_active_operations()

            ws_stats = {
                "total": len(operations),
                "pending": 0,
                "running": 0,
                "completed": 0,
                "failed": 0,
                "cancelled": 0
            }

            for operation in operations:
                stats["total_operations"] += 1

                status_key = operation.status.value
                if status_key in ws_stats:
                    ws_stats[status_key] += 1
                    stats[status_key] += 1

            stats["by_workstation"][ws_config.id] = {
                "name": ws_config.name,
                "stats": ws_stats
            }

        except Exception:
            continue

    return stats


@router.delete("/cleanup", response_model=APIResponse)
async def cleanup_completed_operations(config: SystemConfig = Depends(get_system_config), current_user: str = Depends(verify_token)):
    """Очистить завершенные операции из памяти."""
    from .dependencies import ldplayer_managers
    
    total_cleaned = 0
    
    # ✅ FIXED: Iterate through all managers and cleanup completed operations
    for ws_id, manager in ldplayer_managers.items():
        if manager:
            # Clean operations completed more than 1 hour ago
            cleaned_count = manager.cleanup_completed_operations(keep_hours=1)
            total_cleaned += cleaned_count
            
            if cleaned_count > 0:
                logger.log_system_event(
                    f"Cleaned {cleaned_count} operations from {ws_id}",
                    {"workstation_id": ws_id, "cleaned_count": cleaned_count}
                )

    return APIResponse(
        success=True,
        message=f"Cleaned {total_cleaned} completed operations from all managers",
        data={"cleaned_count": total_cleaned}
    )
