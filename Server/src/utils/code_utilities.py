"""
Code utilities - общие функции для избежания дублирования кода

Используется для:
- Извлечения имён эмуляторов
- Проверки статусов
- Работы с операциями
- Преобразований данных
"""

from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# UTILITIES FOR EMULATOR NAME EXTRACTION
# ============================================================================

def extract_emulator_name(full_name: str) -> str:
    """
    Извлекает имя эмулятора из полного имени формата 'workstation__emulator_name'.
    
    Args:
        full_name: Полное имя в формате 'workstation_id__emulator_name'
        
    Returns:
        Только название эмулятора без префикса workstation
        
    Examples:
        >>> extract_emulator_name("ws1__emulator_1")
        'emulator_1'
    """
    try:
        parts = full_name.split("__")
        if len(parts) >= 2:
            return parts[-1]  # Берем последнюю часть
        return full_name
    except Exception as e:
        logger.warning(f"Failed to extract emulator name from {full_name}: {e}")
        return full_name


def get_workstation_id_from_emulator(full_name: str) -> Optional[str]:
    """
    Извлекает ID workstation из полного имени эмулятора.
    
    Args:
        full_name: Полное имя в формате 'workstation_id__emulator_name'
        
    Returns:
        ID workstation или None если не удается извлечь
    """
    try:
        parts = full_name.split("__")
        if len(parts) >= 2:
            return parts[0]
        return None
    except Exception as e:
        logger.warning(f"Failed to extract workstation ID from {full_name}: {e}")
        return None


# ============================================================================
# UTILITIES FOR SEARCH AND FILTERING
# ============================================================================

def find_emulator_by_name(emulators: List[Any], name: str, full_name: bool = False) -> Optional[Any]:
    """
    Находит эмулятор по названию (или полному имени).
    
    Args:
        emulators: Список объектов Emulator
        name: Название для поиска
        full_name: Если True, ищет по полному имени. Если False, по short name
        
    Returns:
        Объект Emulator или None если не найден
    """
    try:
        for emulator in emulators:
            if full_name:
                if emulator.name == name:
                    return emulator
            else:
                emulator_short = extract_emulator_name(emulator.name)
                if emulator_short == name:
                    return emulator
        return None
    except Exception as e:
        logger.error(f"Error searching for emulator {name}: {e}")
        return None


def find_workstation_by_id(workstations: List[Any], ws_id: str) -> Optional[Any]:
    """
    Находит рабочую станцию по ID.
    
    Args:
        workstations: Список объектов Workstation
        ws_id: ID для поиска
        
    Returns:
        Объект Workstation или None если не найден
    """
    try:
        for ws in workstations:
            if ws.id == ws_id:
                return ws
        return None
    except Exception as e:
        logger.error(f"Error searching for workstation {ws_id}: {e}")
        return None


# ============================================================================
# UTILITIES FOR STATUS CHECKING
# ============================================================================

def is_emulator_running(status: str) -> bool:
    """Проверяет запущен ли эмулятор"""
    return status.upper() in ["RUNNING", "ACTIVE", "ONLINE"]


def is_emulator_stopped(status: str) -> bool:
    """Проверяет остановлен ли эмулятор"""
    return status.upper() in ["STOPPED", "OFFLINE", "INACTIVE"]


def is_operation_in_progress(status: str) -> bool:
    """Проверяет выполняется ли операция"""
    return status.upper() in ["PENDING", "RUNNING", "PROCESSING"]


def is_operation_completed(status: str) -> bool:
    """Проверяет завершена ли операция"""
    return status.upper() in ["SUCCESS", "COMPLETED", "DONE"]


def is_operation_failed(status: str) -> bool:
    """Проверяет была ли ошибка операции"""
    return status.upper() in ["FAILED", "ERROR"]


# ============================================================================
# UTILITIES FOR PAGINATION
# ============================================================================

def apply_pagination(items: List[Any], skip: int = 0, limit: int = 100) -> List[Any]:
    """
    Применяет пагинацию к списку.
    
    Args:
        items: Список для пагинации
        skip: Сколько элементов пропустить (по умолчанию 0)
        limit: Максимум элементов в ответе (по умолчанию 100)
        
    Returns:
        Подмножество списка с применённой пагинацией
    """
    # Защита от negative values
    skip = max(0, skip)
    limit = max(1, min(limit, 1000))  # Максимум 1000 за раз
    
    return items[skip : skip + limit]


def get_pagination_info(total_count: int, skip: int, limit: int) -> Dict[str, int]:
    """
    Возвращает информацию о пагинации.
    
    Args:
        total_count: Общее количество элементов
        skip: Сколько элементов пропущено
        limit: Лимит элементов
        
    Returns:
        Словарь с информацией о пагинации
    """
    skip = max(0, skip)
    limit = max(1, min(limit, 1000))
    
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "returned": min(limit, max(0, total_count - skip)),
        "has_more": (skip + limit) < total_count,
    }


# ============================================================================
# UTILITIES FOR DATA TRANSFORMATION
# ============================================================================

def safe_get_dict_value(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Безопасно получает значение из словаря.
    
    Args:
        d: Словарь
        key: Ключ
        default: Значение по умолчанию если ключ не найден
        
    Returns:
        Значение или default
    """
    try:
        return d.get(key, default)
    except (TypeError, AttributeError):
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Объединяет несколько словарей"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


# ============================================================================
# UTILITIES FOR LOGGING
# ============================================================================

def log_operation_start(op_name: str, operation_id: str, params: Dict[str, Any] = None):
    """Логирует начало операции"""
    logger.info(f"Starting operation {op_name} [{operation_id}]")
    if params:
        logger.debug(f"  Parameters: {params}")


def log_operation_complete(op_name: str, operation_id: str, result: Any = None):
    """Логирует завершение операции"""
    logger.info(f"Completed operation {op_name} [{operation_id}]")
    if result:
        logger.debug(f"  Result: {result}")


def log_operation_error(op_name: str, operation_id: str, error: Exception):
    """Логирует ошибку операции"""
    logger.error(f"Error in operation {op_name} [{operation_id}]: {error}")


# ============================================================================
# UTILITIES FOR VALIDATION
# ============================================================================

def validate_not_empty(value: str, field_name: str = "field") -> bool:
    """Проверяет что значение не пусто"""
    if not value or not str(value).strip():
        logger.warning(f"Validation failed: {field_name} is empty")
        return False
    return True


def validate_length(value: str, min_len: int = 1, max_len: int = 255, field_name: str = "field") -> bool:
    """Проверяет длину строки"""
    if not isinstance(value, str):
        return False
    if len(value) < min_len or len(value) > max_len:
        logger.warning(f"Validation failed: {field_name} length {len(value)} not in range [{min_len}, {max_len}]")
        return False
    return True


def validate_alphanumeric(value: str, field_name: str = "field", allow_underscore: bool = True) -> bool:
    """Проверяет что строка только буквы, цифры и опционально подчеркивание"""
    if not isinstance(value, str):
        return False
    
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    if allow_underscore:
        allowed_chars.add("_")
        allowed_chars.add("-")
    
    if not all(c in allowed_chars for c in value):
        logger.warning(f"Validation failed: {field_name} contains invalid characters")
        return False
    return True
