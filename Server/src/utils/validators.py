"""
Input validators - валидация всех входящих данных

Используется для:
- Валидации названий рабочих станций
- Валидации конфигурации эмуляторов
- Валидации параметров операций
- Валидации пользовательского ввода
"""

from typing import Optional, Dict, Any, List
import re
import logging
from src.utils.constants import ValidationRules, ErrorMessage

logger = logging.getLogger(__name__)


# ============================================================================
# WORKSTATION VALIDATORS
# ============================================================================

def validate_workstation_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Валидирует название рабочей станции.
    
    Args:
        name: Название для проверки
        
    Returns:
        (is_valid, error_message)
    """
    # Проверка пусто ли
    if not name or not str(name).strip():
        return False, "Workstation name cannot be empty"
    
    # Проверка длины
    if len(name) < ValidationRules.MIN_NAME_LENGTH:
        return False, f"Name must be at least {ValidationRules.MIN_NAME_LENGTH} characters"
    
    if len(name) > ValidationRules.MAX_NAME_LENGTH:
        return False, f"Name cannot exceed {ValidationRules.MAX_NAME_LENGTH} characters"
    
    # Проверка паттерна (только буквы, цифры, подчеркивание, дефис)
    if not re.match(ValidationRules.NAME_PATTERN, name):
        return False, "Name can only contain letters, numbers, underscores, and hyphens"
    
    return True, None


def validate_workstation_id(ws_id: str) -> tuple[bool, Optional[str]]:
    """Валидирует ID рабочей станции"""
    return validate_workstation_name(ws_id)


# ============================================================================
# EMULATOR VALIDATORS
# ============================================================================

def validate_emulator_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Валидирует название эмулятора.
    
    Args:
        name: Название для проверки
        
    Returns:
        (is_valid, error_message)
    """
    # Проверка пусто ли
    if not name or not str(name).strip():
        return False, "Emulator name cannot be empty"
    
    # Проверка длины
    if len(name) < ValidationRules.MIN_NAME_LENGTH:
        return False, f"Name must be at least {ValidationRules.MIN_NAME_LENGTH} characters"
    
    if len(name) > ValidationRules.MAX_NAME_LENGTH:
        return False, f"Name cannot exceed {ValidationRules.MAX_NAME_LENGTH} characters"
    
    # Проверка паттерна
    if not re.match(ValidationRules.NAME_PATTERN, name):
        return False, "Name can only contain letters, numbers, underscores, and hyphens"
    
    return True, None


def validate_emulator_config(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Валидирует конфигурацию эмулятора.
    
    Args:
        config: Конфигурация для проверки
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(config, dict):
        return False, "Configuration must be a dictionary"
    
    # Обязательные поля
    required_fields = ['width', 'height', 'dpi']
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    # Проверка типов
    try:
        width = int(config['width'])
        height = int(config['height'])
        dpi = int(config['dpi'])
        
        if width <= 0 or height <= 0 or dpi <= 0:
            return False, "Width, height, and DPI must be positive numbers"
        
        if width < 320 or height < 240:
            return False, "Minimum resolution is 320x240"
        
        if width > 2560 or height > 1600:
            return False, "Maximum resolution is 2560x1600"
        
        if dpi < 72 or dpi > 600:
            return False, "DPI must be between 72 and 600"
            
    except (ValueError, TypeError) as e:
        return False, f"Invalid configuration values: {e}"
    
    return True, None


# ============================================================================
# OPERATION VALIDATORS
# ============================================================================

def validate_operation_type(op_type: str, allowed_types: List[str] = None) -> tuple[bool, Optional[str]]:
    """
    Валидирует тип операции.
    
    Args:
        op_type: Тип операции для проверки
        allowed_types: Список разрешённых типов (если None, то все разрешены)
        
    Returns:
        (is_valid, error_message)
    """
    if not op_type or not isinstance(op_type, str):
        return False, "Operation type must be a non-empty string"
    
    op_type = op_type.strip().lower()
    
    if allowed_types and op_type not in allowed_types:
        return False, f"Invalid operation type. Allowed: {', '.join(allowed_types)}"
    
    return True, None


def validate_operation_status(status: str) -> tuple[bool, Optional[str]]:
    """Валидирует статус операции"""
    valid_statuses = ["PENDING", "RUNNING", "SUCCESS", "FAILED", "CANCELLED", "TIMEOUT"]
    
    if not status or status.upper() not in valid_statuses:
        return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
    
    return True, None


def validate_operation_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Валидирует параметры операции.
    
    Args:
        params: Параметры для проверки
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(params, dict):
        return False, "Parameters must be a dictionary"
    
    # Проверка на пустоту
    if not params:
        return False, "Parameters cannot be empty"
    
    # Проверка размера (не более 10KB)
    import json
    try:
        json_str = json.dumps(params)
        if len(json_str) > 10240:  # 10KB
            return False, "Parameters are too large (max 10KB)"
    except Exception as e:
        return False, f"Invalid parameters format: {e}"
    
    return True, None


# ============================================================================
# PAGINATION VALIDATORS
# ============================================================================

def validate_pagination_params(skip: Optional[int], limit: Optional[int]) -> tuple[int, int]:
    """
    Валидирует и нормализует параметры пагинации.
    
    Args:
        skip: Сколько пропустить
        limit: Лимит результатов
        
    Returns:
        (validated_skip, validated_limit)
    """
    # Установить значения по умолчанию если None
    skip = skip or 0
    limit = limit or 100
    
    # Защита от negative values
    skip = max(0, skip)
    limit = max(1, min(limit, 1000))  # Минимум 1, максимум 1000
    
    return skip, limit


# ============================================================================
# GENERAL VALIDATORS
# ============================================================================

def validate_not_empty(value: str, field_name: str = "field") -> tuple[bool, Optional[str]]:
    """
    Проверяет что значение не пусто.
    
    Args:
        value: Значение для проверки
        field_name: Название поля для сообщения об ошибке
        
    Returns:
        (is_valid, error_message)
    """
    if not value or not str(value).strip():
        return False, f"{field_name} cannot be empty"
    
    return True, None


def validate_string_length(value: str, min_len: int = 1, max_len: int = 255, 
                          field_name: str = "field") -> tuple[bool, Optional[str]]:
    """
    Проверяет длину строки.
    
    Args:
        value: Строка для проверки
        min_len: Минимальная длина
        max_len: Максимальная длина
        field_name: Название поля для сообщения об ошибке
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"
    
    if len(value) < min_len:
        return False, f"{field_name} must be at least {min_len} characters"
    
    if len(value) > max_len:
        return False, f"{field_name} cannot exceed {max_len} characters"
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Проверяет валидность email адреса.
    
    Args:
        email: Email для проверки
        
    Returns:
        (is_valid, error_message)
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if not email or not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_ip_address(ip: str) -> tuple[bool, Optional[str]]:
    """
    Проверяет валидность IP адреса.
    
    Args:
        ip: IP адрес для проверки
        
    Returns:
        (is_valid, error_message)
    """
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    
    if not ip or not re.match(ip_pattern, ip):
        return False, "Invalid IP address format"
    
    # Проверка диапазонов
    parts = ip.split('.')
    for part in parts:
        try:
            num = int(part)
            if num > 255:
                return False, "Invalid IP address: octets must be 0-255"
        except ValueError:
            return False, "Invalid IP address: octets must be numbers"
    
    return True, None


def validate_port(port: int) -> tuple[bool, Optional[str]]:
    """
    Проверяет валидность порта.
    
    Args:
        port: Порт для проверки
        
    Returns:
        (is_valid, error_message)
    """
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return False, "Port must be between 1 and 65535"
    except (ValueError, TypeError):
        return False, "Port must be a valid number"
    
    return True, None


# ============================================================================
# BATCH VALIDATION
# ============================================================================

def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, Optional[str]]:
    """
    Валидирует что все обязательные поля присутствуют.
    
    Args:
        data: Данные для проверки
        required_fields: Список обязательных полей
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if data[field] is None:
            return False, f"Required field '{field}' cannot be null"
    
    return True, None
