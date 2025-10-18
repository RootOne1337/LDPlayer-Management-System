"""
СВЕРХ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ для удалённой диагностики.

Добавляет автоматическое логирование всех функций с:
- Входными параметрами (без паролей!)
- Результатами выполнения
- Временем выполнения
- Полными stack trace при ошибках
"""

import functools
import traceback
import inspect
from datetime import datetime
from typing import Callable, Any
from .logger import get_logger, LogCategory


def log_function_call(category: LogCategory = LogCategory.SYSTEM):
    """
    Декоратор для автоматического логирования вызовов функций.
    
    Логирует:
    - Входные параметры (без паролей!)
    - Результат выполнения
    - Время выполнения
    - Ошибки со stack trace
    
    Пример:
        @log_function_call(LogCategory.API)
        async def create_emulator(name: str, config: dict):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(category)
            func_name = func.__name__
            module_name = func.__module__
            
            # Безопасное логирование параметров (скрываем пароли)
            safe_kwargs = _sanitize_sensitive_data(kwargs.copy())
            safe_args = _sanitize_sensitive_data(list(args))
            
            # Логируем ВХОД в функцию
            logger.logger.info(
                f"🚀 CALL {module_name}.{func_name}() | args={safe_args} | kwargs={safe_kwargs}"
            )
            
            start_time = datetime.now()
            
            try:
                result = await func(*args, **kwargs)
                
                # Логируем УСПЕШНЫЙ результат
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                safe_result = _sanitize_sensitive_data(result) if result else None
                
                logger.logger.info(
                    f"✅ SUCCESS {module_name}.{func_name}() | duration={duration_ms:.2f}ms | result={_truncate_data(safe_result)}"
                )
                
                return result
                
            except Exception as e:
                # Логируем ОШИБКУ с полным stack trace
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                error_trace = traceback.format_exc()
                
                logger.logger.error(
                    f"❌ ERROR {module_name}.{func_name}() | duration={duration_ms:.2f}ms | "
                    f"error={type(e).__name__}: {str(e)}\n"
                    f"Stack trace:\n{error_trace}"
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(category)
            func_name = func.__name__
            module_name = func.__module__
            
            safe_kwargs = _sanitize_sensitive_data(kwargs.copy())
            safe_args = _sanitize_sensitive_data(list(args))
            
            logger.logger.info(
                f"🚀 CALL {module_name}.{func_name}() | args={safe_args} | kwargs={safe_kwargs}"
            )
            
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                safe_result = _sanitize_sensitive_data(result) if result else None
                
                logger.logger.info(
                    f"✅ SUCCESS {module_name}.{func_name}() | duration={duration_ms:.2f}ms | result={_truncate_data(safe_result)}"
                )
                
                return result
                
            except Exception as e:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                error_trace = traceback.format_exc()
                
                logger.logger.error(
                    f"❌ ERROR {module_name}.{func_name}() | duration={duration_ms:.2f}ms | "
                    f"error={type(e).__name__}: {str(e)}\n"
                    f"Stack trace:\n{error_trace}"
                )
                
                raise
        
        # Вернуть правильную обёртку (async или sync)
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _sanitize_sensitive_data(data: Any) -> Any:
    """
    Удаляет чувствительные данные из логов (пароли, токены).
    """
    if isinstance(data, dict):
        return {
            key: "***HIDDEN***" if any(
                sensitive in key.lower() 
                for sensitive in ["password", "token", "secret", "key", "auth", "hashed_password"]
            ) else _sanitize_sensitive_data(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [_sanitize_sensitive_data(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(_sanitize_sensitive_data(item) for item in data)
    else:
        return data


def _truncate_data(data: Any, max_length: int = 500) -> str:
    """
    Обрезает большие данные для логов.
    """
    data_str = str(data)
    if len(data_str) > max_length:
        return data_str[:max_length] + f"... (truncated, total {len(data_str)} chars)"
    return data_str


def log_http_request(request_info: dict):
    """
    Логирует HTTP запрос с полными деталями.
    
    Args:
        request_info: {
            "method": "POST",
            "url": "/api/emulators",
            "headers": {...},
            "body": {...},
            "client_ip": "192.168.1.100",
            "user": "admin"
        }
    """
    logger = get_logger(LogCategory.API)
    
    safe_info = _sanitize_sensitive_data(request_info.copy())
    
    logger.logger.info(
        f"🌐 HTTP {safe_info.get('method')} {safe_info.get('url')} | "
        f"client={safe_info.get('client_ip')} | user={safe_info.get('user')} | "
        f"headers={_truncate_data(safe_info.get('headers', {}), 200)} | "
        f"body={_truncate_data(safe_info.get('body', {}), 300)}"
    )


def log_http_response(response_info: dict):
    """
    Логирует HTTP ответ с деталями.
    
    Args:
        response_info: {
            "status_code": 200,
            "duration_ms": 123.45,
            "body": {...}
        }
    """
    logger = get_logger(LogCategory.API)
    
    status = response_info.get("status_code")
    duration = response_info.get("duration_ms", 0)
    
    emoji = "✅" if 200 <= status < 300 else "⚠️" if 300 <= status < 400 else "❌"
    
    logger.logger.info(
        f"{emoji} HTTP RESPONSE {status} | duration={duration:.2f}ms | "
        f"body={_truncate_data(response_info.get('body', {}), 300)}"
    )


def log_database_query(query_info: dict):
    """
    Логирует запрос к базе данных.
    
    Args:
        query_info: {
            "operation": "SELECT",
            "table": "users",
            "filters": {...},
            "duration_ms": 12.34
        }
    """
    logger = get_logger(LogCategory.SYSTEM)
    
    logger.logger.debug(
        f"💾 DB {query_info.get('operation')} {query_info.get('table')} | "
        f"filters={query_info.get('filters')} | "
        f"duration={query_info.get('duration_ms', 0):.2f}ms"
    )


def log_external_api_call(api_info: dict):
    """
    Логирует вызов внешнего API (LDPlayer, WinRM).
    
    Args:
        api_info: {
            "api": "LDPlayer",
            "command": "dnconsole.exe list2",
            "target": "ws_001",
            "duration_ms": 456.78,
            "result": {...}
        }
    """
    logger = get_logger(LogCategory.WORKSTATION)
    
    logger.logger.info(
        f"🔌 EXTERNAL API {api_info.get('api')} | "
        f"command={api_info.get('command')} | "
        f"target={api_info.get('target')} | "
        f"duration={api_info.get('duration_ms', 0):.2f}ms | "
        f"result={_truncate_data(api_info.get('result', {}), 200)}"
    )


def log_authentication_attempt(auth_info: dict):
    """
    Логирует попытку аутентификации.
    
    Args:
        auth_info: {
            "username": "admin",
            "success": True,
            "ip": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "reason": "Invalid password" (if failed)
        }
    """
    logger = get_logger(LogCategory.SECURITY)
    
    emoji = "🔓" if auth_info.get("success") else "🔒"
    status = "SUCCESS" if auth_info.get("success") else "FAILED"
    
    logger.logger.warning(
        f"{emoji} AUTH {status} | user={auth_info.get('username')} | "
        f"ip={auth_info.get('ip')} | "
        f"user_agent={_truncate_data(auth_info.get('user_agent', ''), 100)} | "
        f"reason={auth_info.get('reason', 'N/A')}"
    )


def log_permission_check(perm_info: dict):
    """
    Логирует проверку прав доступа.
    
    Args:
        perm_info: {
            "user": "operator",
            "role": "OPERATOR",
            "required_role": "ADMIN",
            "resource": "/api/users",
            "allowed": False
        }
    """
    logger = get_logger(LogCategory.SECURITY)
    
    emoji = "✅" if perm_info.get("allowed") else "❌"
    status = "ALLOWED" if perm_info.get("allowed") else "DENIED"
    
    logger.logger.warning(
        f"{emoji} PERMISSION {status} | user={perm_info.get('user')} | "
        f"role={perm_info.get('role')} | required={perm_info.get('required_role')} | "
        f"resource={perm_info.get('resource')}"
    )


def log_workstation_connection(conn_info: dict):
    """
    Логирует подключение/отключение от workstation.
    
    Args:
        conn_info: {
            "workstation_id": "ws_001",
            "ip": "192.168.1.101",
            "action": "connect" | "disconnect",
            "success": True,
            "error": "Connection timeout" (if failed)
        }
    """
    logger = get_logger(LogCategory.WORKSTATION)
    
    action = conn_info.get("action", "").upper()
    emoji = "🔌" if action == "CONNECT" else "🔌"
    status = "SUCCESS" if conn_info.get("success") else "FAILED"
    
    logger.logger.info(
        f"{emoji} {action} {status} | ws={conn_info.get('workstation_id')} | "
        f"ip={conn_info.get('ip')} | "
        f"error={conn_info.get('error', 'N/A')}"
    )


def log_emulator_operation(emu_info: dict):
    """
    Логирует операции с эмулятором.
    
    Args:
        emu_info: {
            "operation": "start" | "stop" | "create" | "delete",
            "emulator_id": "emu_123",
            "emulator_name": "Test Emulator",
            "workstation_id": "ws_001",
            "duration_ms": 1234.56,
            "success": True,
            "error": "Emulator not found" (if failed)
        }
    """
    logger = get_logger(LogCategory.EMULATOR)
    
    operation = emu_info.get("operation", "").upper()
    emoji_map = {
        "START": "▶️",
        "STOP": "⏸️",
        "CREATE": "➕",
        "DELETE": "🗑️",
        "MODIFY": "✏️"
    }
    emoji = emoji_map.get(operation, "🎮")
    status = "SUCCESS" if emu_info.get("success") else "FAILED"
    
    logger.logger.info(
        f"{emoji} EMULATOR {operation} {status} | "
        f"name={emu_info.get('emulator_name')} | "
        f"id={emu_info.get('emulator_id')} | "
        f"ws={emu_info.get('workstation_id')} | "
        f"duration={emu_info.get('duration_ms', 0):.2f}ms | "
        f"error={emu_info.get('error', 'N/A')}"
    )
