"""
Зависимости для FastAPI endpoints с JWT аутентификацией.

Предоставляет общие зависимости для инъекции в роуты.
"""

from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import get_config, SystemConfig
from ..remote.workstation import WorkstationManager
from ..remote.ldplayer_manager import LDPlayerManager
from ..utils.logger import get_logger, LogCategory
from ..utils.jwt_auth import JWTManager, User, Token, get_current_user, get_current_admin


# Менеджеры (глобальные)
workstation_managers: Dict[str, WorkstationManager] = {}
ldplayer_managers: Dict[str, LDPlayerManager] = {}

# JWT Manager
jwt_manager = JWTManager()

# Security
security = HTTPBearer(auto_error=False)


async def get_system_config() -> SystemConfig:
    """Получить конфигурацию системы.
    
    Returns:
        SystemConfig: Конфигурация системы
    """
    return get_config()


def get_workstation_manager(workstation_id: str, 
                            config: SystemConfig = Depends(get_system_config)) -> WorkstationManager:
    """Получить менеджер рабочей станции.

    Args:
        workstation_id: ID рабочей станции
        config: Конфигурация системы

    Returns:
        WorkstationManager: Менеджер рабочей станции

    Raises:
        HTTPException: Если рабочая станция не найдена
    """
    workstation_config = None

    for ws in config.workstations:
        if ws.id == workstation_id:
            workstation_config = ws
            break

    if not workstation_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
        # ИСПРАВЛЕНО: Убрана циклическая зависимость
        # Создаём WorkstationManager напрямую без вызова get_workstation_manager
        workstation_config = None
        for ws in config.workstations:
            if ws.id == workstation_id:
                workstation_config = ws
                break
        
        if not workstation_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рабочая станция {workstation_id} не найдена"
            )
        
        workstation_manager = WorkstationManager(workstation_config)
        ldplayer_managers[workstation_id] = LDPlayerManager(workstation_manager)

    return ldplayer_managers[workstation_id]


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Проверить JWT токен.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        str: Username если токен валиден

    Raises:
        HTTPException: Если токен невалиден или отсутствует
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Проверить JWT токен
        payload = jwt_manager.verify_token(credentials.credentials)
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        return username
        
    except HTTPException:
        raise
    except (ValueError, TypeError, KeyError) as e:
        logger_api.log_error(f"Token validation error - invalid data: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token data: {str(e)}",
        )
    except Exception as e:
        logger_api.log_error(f"Token validation error - unexpected: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
        )


def get_logger_dependency(category: LogCategory = LogCategory.API):
    """Получить логгер для endpoint'а.

    Args:
        category: Категория логирования

    Returns:
        Logger: Логгер
    """
    return get_logger(category)


# ============================================================================
# UTILITY DECORATORS - Reduce Code Duplication
# ============================================================================

from functools import wraps
from typing import Callable, Any


def handle_api_errors(logger_category: LogCategory = LogCategory.API):
    """Декоратор для унифицированной обработки ошибок в API endpoints.
    
    Автоматически логирует ошибки и преобразует их в HTTPException с правильными кодами.
    
    Args:
        logger_category: Категория логирования
        
    Example:
        @router.get("/example")
        @handle_api_errors(LogCategory.EMULATOR)
        async def example_endpoint():
            # Your code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(logger_category)
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPExceptions as-is (already have correct status codes)
                raise
            except ValueError as e:
                # Validation errors → 400 Bad Request
                logger.log_error(f"Validation error in {func.__name__}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input: {str(e)}"
                )
            except PermissionError as e:
                # Permission errors → 403 Forbidden
                logger.log_error(f"Permission denied in {func.__name__}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {str(e)}"
                )
            except ConnectionError as e:
                # Network errors → 503 Service Unavailable
                logger.log_error(f"Connection error in {func.__name__}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service temporarily unavailable: {str(e)}"
                )
            except TimeoutError as e:
                # Timeout errors → 504 Gateway Timeout
                logger.log_error(f"Timeout in {func.__name__}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"Operation timeout: {str(e)}"
                )
            except Exception as e:
                # All other errors → 500 Internal Server Error
                logger.log_error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal server error: {str(e)}"
                )
        return wrapper
    return decorator


def validate_workstation_exists(config: SystemConfig, workstation_id: str) -> None:
    """Валидация существования рабочей станции.
    
    Args:
        config: Системная конфигурация
        workstation_id: ID рабочей станции
        
    Raises:
        HTTPException: 404 если станция не найдена
    """
    ws_exists = any(ws.id == workstation_id for ws in config.workstations)
    if not ws_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workstation '{workstation_id}' not found"
        )


def validate_emulator_name(name: str) -> None:
    """Валидация имени эмулятора.
    
    Args:
        name: Имя эмулятора
        
    Raises:
        ValueError: Если имя некорректное
    """
    if not name or len(name.strip()) == 0:
        raise ValueError("Emulator name cannot be empty")
    
    if len(name) > 100:
        raise ValueError("Emulator name too long (max 100 characters)")
    
    # Проверка на недопустимые символы
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in name for char in invalid_chars):
        raise ValueError(f"Emulator name contains invalid characters: {', '.join(invalid_chars)}")


# ============================================================================
# 🆕 DI КОНТЕЙНЕР ЗАВИСИМОСТИ (для избежания циклического импорта)
# ============================================================================

async def get_workstation_service() -> "WorkstationService":
    """Получить WorkstationService из DI контейнера.
    
    🆕 Используется для FastAPI dependency injection в маршрутах.
    Это позволяет избежать циклического импорта.
    """
    from ..core.container import container
    from ..services.workstation_service import WorkstationService
    
    service = container.get("workstation_service")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WorkstationService не инициализирован"
        )
    return service


async def get_emulator_service() -> "EmulatorService":
    """Получить EmulatorService из DI контейнера.
    
    🆕 Используется для FastAPI dependency injection в маршрутах.
    Это позволяет избежать циклического импорта.
    """
    from ..core.container import container
    from ..services.emulator_service import EmulatorService
    
    service = container.get("emulator_service")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="EmulatorService не инициализирован"
        )
    return service


async def get_ldplayer_manager_di() -> "LDPlayerManager":
    """Получить LDPlayerManager из DI контейнера.
    
    🆕 Используется для FastAPI dependency injection в маршрутах.
    """
    from ..core.container import container
    
    manager = container.get("ldplayer_manager")
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LDPlayerManager не инициализирован"
        )
    return manager
