"""
Обработчик ошибок и исключений системы управления LDPlayer эмуляторами.

Предоставляет централизованную обработку ошибок, восстановление после сбоев
и механизмы graceful degradation при проблемах с подключением.
"""

import asyncio
import functools
import time
import traceback
from typing import Dict, List, Optional, Any, Callable, TypeVar, Union
from datetime import datetime, timedelta
from enum import Enum

from .logger import get_logger, LogCategory, LogLevel, OperationType


T = TypeVar('T')


class ErrorSeverity(str, Enum):
    """Уровень серьезности ошибки."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Категория ошибки."""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    VALIDATION = "validation"
    SYSTEM = "system"
    WORKSTATION = "workstation"
    EMULATOR = "emulator"
    CONFIGURATION = "configuration"
    EXTERNAL = "external"


class SystemError(Exception):
    """Базовое исключение системы."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        workstation_id: str = None,
        emulator_id: str = None,
        recoverable: bool = True,
        **kwargs
    ):
        """Инициализация системной ошибки.

        Args:
            message: Сообщение об ошибке
            category: Категория ошибки
            severity: Уровень серьезности
            workstation_id: ID рабочей станции
            emulator_id: ID эмулятора
            recoverable: Можно ли восстановиться после ошибки
            **kwargs: Дополнительные данные
        """
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.workstation_id = workstation_id
        self.emulator_id = emulator_id
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        self.additional_data = kwargs


class NetworkError(SystemError):
    """Ошибка сети."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.NETWORK, ErrorSeverity.HIGH, **kwargs)


class WorkstationConnectionError(SystemError):
    """Ошибка подключения к рабочей станции."""

    def __init__(self, workstation_id: str, message: str = None, **kwargs):
        message = message or f"Не удалось подключиться к рабочей станции {workstation_id}"
        super().__init__(
            message,
            ErrorCategory.WORKSTATION,
            ErrorSeverity.HIGH,
            workstation_id=workstation_id,
            **kwargs
        )


class EmulatorOperationError(SystemError):
    """Ошибка операции с эмулятором."""

    def __init__(self, emulator_id: str, operation: str, message: str = None, **kwargs):
        message = message or f"Ошибка операции '{operation}' с эмулятором {emulator_id}"
        super().__init__(
            message,
            ErrorCategory.EMULATOR,
            ErrorSeverity.MEDIUM,
            emulator_id=emulator_id,
            **kwargs
        )


class ConfigurationError(SystemError):
    """Ошибка конфигурации."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.CONFIGURATION, ErrorSeverity.HIGH, **kwargs)


class ErrorHandler:
    """Централизованный обработчик ошибок."""

    def __init__(self):
        """Инициализация обработчика ошибок."""
        self.logger = get_logger(LogCategory.SYSTEM)
        self.error_counts: Dict[str, int] = {}
        self.error_timestamps: Dict[str, datetime] = {}
        self.circuit_breakers: Dict[str, bool] = {}

        # Настройки восстановления
        self.max_errors_per_minute = 10
        self.circuit_breaker_timeout = 60  # секунды

    def handle_error(
        self,
        error: Exception,
        context: str = "",
        workstation_id: str = None,
        emulator_id: str = None,
        reraise: bool = False
    ) -> SystemError:
        """Обработать ошибку и преобразовать в SystemError.

        Args:
            error: Исходная ошибка
            context: Контекст возникновения ошибки
            workstation_id: ID рабочей станции
            emulator_id: ID эмулятора
            reraise: Перевыбросить исключение после обработки

        Returns:
            SystemError: Обработанная ошибка
        """
        # Определить категорию и серьезность
        category, severity = self._categorize_error(error)

        # Создать SystemError
        if isinstance(error, SystemError):
            system_error = error
        else:
            system_error = SystemError(
                str(error),
                category,
                severity,
                workstation_id=workstation_id,
                emulator_id=emulator_id,
                recoverable=self._is_recoverable(error)
            )

        # Добавить контекст
        if context:
            system_error.additional_data['context'] = context

        # Логировать ошибку
        self._log_error(system_error, error)

        # Обновить статистику ошибок
        self._update_error_stats(system_error)

        # Проверить circuit breaker
        if self._should_trigger_circuit_breaker(system_error):
            self._trigger_circuit_breaker(system_error)

        if reraise:
            raise system_error

        return system_error

    def _categorize_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Определить категорию и серьезность ошибки.

        Args:
            error: Исключение для категоризации

        Returns:
            tuple[ErrorCategory, ErrorSeverity]: Категория и серьезность
        """
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Определение категории
        if any(term in error_message for term in ['connection', 'network', 'timeout', 'unreachable']):
            category = ErrorCategory.NETWORK
            severity = ErrorSeverity.HIGH
        elif any(term in error_message for term in ['permission', 'access denied', 'unauthorized']):
            category = ErrorCategory.PERMISSION
            severity = ErrorSeverity.HIGH
        elif any(term in error_message for term in ['authentication', 'credentials', 'login']):
            category = ErrorCategory.AUTHENTICATION
            severity = ErrorSeverity.HIGH
        elif any(term in error_message for term in ['validation', 'invalid', 'format']):
            category = ErrorCategory.VALIDATION
            severity = ErrorSeverity.MEDIUM
        elif any(term in error_message for term in ['workstation', 'ldplayer', 'emulator']):
            category = ErrorCategory.WORKSTATION
            severity = ErrorSeverity.MEDIUM
        elif any(term in error_message for term in ['config', 'configuration', 'setting']):
            category = ErrorCategory.CONFIGURATION
            severity = ErrorSeverity.HIGH
        else:
            category = ErrorCategory.SYSTEM
            severity = ErrorSeverity.MEDIUM

        # Корректировка серьезности на основе типа ошибки
        if error_type in ['ConnectionError', 'TimeoutError', 'NetworkError']:
            severity = ErrorSeverity.HIGH
        elif error_type in ['PermissionError', 'AuthenticationError']:
            severity = ErrorSeverity.CRITICAL
        elif error_type in ['ValidationError', 'ValueError']:
            severity = ErrorSeverity.LOW

        return category, severity

    def _is_recoverable(self, error: Exception) -> bool:
        """Определить, можно ли восстановиться после ошибки.

        Args:
            error: Исключение для анализа

        Returns:
            bool: True если ошибка восстанавливаемая
        """
        error_type = type(error).__name__

        # Невосстанавливаемые ошибки
        non_recoverable = [
            'PermissionError',
            'AuthenticationError',
            'ConfigurationError',
            'ImportError',
            'ModuleNotFoundError'
        ]

        return error_type not in non_recoverable

    def _log_error(self, system_error: SystemError, original_error: Exception) -> None:
        """Записать ошибку в лог.

        Args:
            system_error: Обработанная ошибка
            original_error: Исходная ошибка
        """
        # Подготовить данные для логирования
        log_data = {
            "error_type": type(original_error).__name__,
            "error_message": str(original_error),
            "category": system_error.category.value,
            "severity": system_error.severity.value,
            "recoverable": system_error.recoverable,
            "workstation_id": system_error.workstation_id,
            "emulator_id": system_error.emulator_id,
            "traceback": traceback.format_exc()
        }

        # Выбрать уровень логирования
        if system_error.severity == ErrorSeverity.CRITICAL:
            level = LogLevel.CRITICAL
        elif system_error.severity == ErrorSeverity.HIGH:
            level = LogLevel.ERROR
        elif system_error.severity == ErrorSeverity.MEDIUM:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO

        # Записать в лог
        self.logger.log_operation(
            OperationType.MODIFY,
            LogCategory.SYSTEM,
            f"Ошибка: {system_error}",
            workstation_id=system_error.workstation_id,
            emulator_id=system_error.emulator_id,
            additional_data=log_data,
            level=level
        )

    def _update_error_stats(self, error: SystemError) -> None:
        """Обновить статистику ошибок.

        Args:
            error: Обработанная ошибка
        """
        # Ключ для статистики
        error_key = f"{error.category.value}:{error.workstation_id or 'global'}"

        # Обновить счетчик ошибок
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.error_timestamps[error_key] = datetime.now()

    def _should_trigger_circuit_breaker(self, error: SystemError) -> bool:
        """Проверить, нужно ли активировать circuit breaker.

        Args:
            error: Обработанная ошибка

        Returns:
            bool: True если нужно активировать circuit breaker
        """
        if error.severity not in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            return False

        # Ключ для circuit breaker
        cb_key = f"{error.category.value}:{error.workstation_id or 'global'}"

        # Проверить количество ошибок за последнюю минуту
        if cb_key in self.error_timestamps:
            minute_ago = datetime.now() - timedelta(minutes=1)
            if self.error_timestamps[cb_key] < minute_ago:
                # Сбросить счетчик если прошло больше минуты
                self.error_counts[cb_key] = 0

        error_count = self.error_counts.get(cb_key, 0)
        return error_count >= self.max_errors_per_minute

    def _trigger_circuit_breaker(self, error: SystemError) -> None:
        """Активировать circuit breaker.

        Args:
            error: Ошибка, вызвавшая активацию
        """
        cb_key = f"{error.category.value}:{error.workstation_id or 'global'}"

        self.circuit_breakers[cb_key] = True

        self.logger.log_operation(
            OperationType.MODIFY,
            LogCategory.SYSTEM,
            f"Circuit breaker активирован: {cb_key}",
            workstation_id=error.workstation_id,
            additional_data={
                "circuit_breaker_key": cb_key,
                "timeout_seconds": self.circuit_breaker_timeout
            },
            level=LogLevel.WARNING
        )

        # Запланировать восстановление circuit breaker
        asyncio.create_task(self._reset_circuit_breaker(cb_key))

    async def _reset_circuit_breaker(self, cb_key: str):
        """Сбросить circuit breaker после таймаута.

        Args:
            cb_key: Ключ circuit breaker
        """
        await asyncio.sleep(self.circuit_breaker_timeout)

        if cb_key in self.circuit_breakers:
            self.circuit_breakers[cb_key] = False

            self.logger.log_operation(
                OperationType.MODIFY,
                LogCategory.SYSTEM,
                f"Circuit breaker сброшен: {cb_key}",
                additional_data={"circuit_breaker_key": cb_key},
                level=LogLevel.INFO
            )

    def is_circuit_breaker_active(self, category: ErrorCategory, workstation_id: str = None) -> bool:
        """Проверить, активен ли circuit breaker.

        Args:
            category: Категория ошибки
            workstation_id: ID рабочей станции

        Returns:
            bool: True если circuit breaker активен
        """
        cb_key = f"{category.value}:{workstation_id or 'global'}"
        return self.circuit_breakers.get(cb_key, False)

    def get_error_stats(self) -> Dict[str, Any]:
        """Получить статистику ошибок.

        Returns:
            Dict[str, Any]: Статистика ошибок
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        # Очистить старые записи
        keys_to_remove = []
        for key, timestamp in self.error_timestamps.items():
            if timestamp < hour_ago:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            self.error_counts.pop(key, None)
            self.error_timestamps.pop(key, None)

        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts_by_category": self._group_errors_by_category(),
            "circuit_breakers_active": len([k for k, v in self.circuit_breakers.items() if v]),
            "errors_last_minute": sum(
                count for key, count in self.error_counts.items()
                if key in self.error_timestamps and self.error_timestamps[key] >= minute_ago
            ),
            "errors_last_hour": sum(self.error_counts.values())
        }

    def _group_errors_by_category(self) -> Dict[str, int]:
        """Группировать ошибки по категориям."""
        categories = {}

        for key in self.error_counts:
            category = key.split(':')[0]
            categories[category] = categories.get(category, 0) + self.error_counts[key]

        return categories


class RetryMechanism:
    """Механизм повторных попыток."""

    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """Инициализация механизма повторных попыток.

        Args:
            max_attempts: Максимальное количество попыток
            base_delay: Базовая задержка в секундах
            max_delay: Максимальная задержка в секундах
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

    def calculate_delay(self, attempt: int) -> float:
        """Рассчитать задержку перед следующей попыткой.

        Args:
            attempt: Номер попытки (начиная с 1)

        Returns:
            float: Задержка в секундах
        """
        # Экспоненциальное увеличение задержки
        delay = self.base_delay * (2 ** (attempt - 1))

        # Ограничить максимальной задержкой
        return min(delay, self.max_delay)

    async def execute_with_retry(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """Выполнить функцию с повторными попытками.

        Args:
            func: Функция для выполнения
            *args: Аргументы функции
            **kwargs: Ключевые аргументы функции

        Returns:
            T: Результат выполнения функции

        Raises:
            Exception: Последняя ошибка если все попытки неудачны
        """
        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_error = e

                # Не повторять для невосстанавливаемых ошибок
                if isinstance(e, SystemError) and not e.recoverable:
                    raise e

                # Если это последняя попытка, выбросить ошибку
                if attempt == self.max_attempts:
                    break

                # Рассчитать задержку и ждать
                delay = self.calculate_delay(attempt)
                await asyncio.sleep(delay)

        # Все попытки неудачны
        raise last_error


# Декораторы для обработки ошибок

def handle_errors(
    context: str = "",
    workstation_id: str = None,
    emulator_id: str = None,
    reraise: bool = False
):
    """Декоратор для обработки ошибок в функциях.

    Args:
        context: Контекст выполнения функции
        workstation_id: ID рабочей станции
        emulator_id: ID эмулятора
        reraise: Перевыбросить исключение после обработки
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_handler = ErrorHandler()

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(
                    e,
                    context,
                    workstation_id,
                    emulator_id,
                    reraise
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_handler = ErrorHandler()

            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(
                    e,
                    context,
                    workstation_id,
                    emulator_id,
                    reraise
                )

        # Вернуть соответствующий wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    context: str = ""
):
    """Декоратор для выполнения с повторными попытками.

    Args:
        max_attempts: Максимальное количество попыток
        base_delay: Базовая задержка
        context: Контекст для логирования
    """
    def decorator(func):
        retry_mechanism = RetryMechanism(max_attempts, base_delay)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await retry_mechanism.execute_with_retry(func, *args, **kwargs)
            except Exception as e:
                logger = get_logger(LogCategory.SYSTEM)
                logger.log_operation(
                    OperationType.MODIFY,
                    LogCategory.SYSTEM,
                    f"Все попытки неудачны: {context}",
                    additional_data={"error": str(e)},
                    level=LogLevel.ERROR
                )
                raise

        return async_wrapper

    return decorator


# Глобальный обработчик ошибок
_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Получить глобальный обработчик ошибок.

    Returns:
        ErrorHandler: Обработчик ошибок
    """
    return _error_handler


def handle_system_error(
    error: Exception,
    context: str = "",
    workstation_id: str = None,
    emulator_id: str = None
) -> SystemError:
    """Обработать системную ошибку.

    Args:
        error: Исходная ошибка
        context: Контекст ошибки
        workstation_id: ID рабочей станции
        emulator_id: ID эмулятора

    Returns:
        SystemError: Обработанная системная ошибка
    """
    error_handler = get_error_handler()
    return error_handler.handle_error(error, context=context, workstation_id=workstation_id, emulator_id=emulator_id)


def with_circuit_breaker(
    category: ErrorCategory,
    operation_name: str = None
):
    """Декоратор для защиты операций circuit breaker.

    Args:
        category: Категория ошибки для circuit breaker
        operation_name: Имя операции для логирования

    Returns:
        Decorated function with circuit breaker protection
    
    Raises:
        RuntimeError: Если circuit breaker активен
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            
            # Получить workstation_id если есть
            workstation_id = kwargs.get('workstation_id') or (
                getattr(args[0].config, 'workstation_id', None) or 
                getattr(args[0].config, 'id', None) if (args and hasattr(args[0], 'config')) else None
            )
            
            # Проверить circuit breaker
            if error_handler.is_circuit_breaker_active(category, workstation_id):
                op_name = operation_name or func.__name__
                logger = get_logger(LogCategory.SYSTEM)
                logger.logger.warning(
                    f"⚠️ Circuit breaker активен для {op_name}"
                )
                raise RuntimeError(
                    f"Circuit breaker активен для операции '{op_name}'. "
                    f"Пожалуйста, повторите попытку позже."
                )
            
            # Выполнить функцию
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(
                    e,
                    category=category,
                    context={'operation': operation_name or func.__name__}
                )
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            
            # Получить workstation_id если есть
            workstation_id = kwargs.get('workstation_id') or (
                getattr(args[0].config, 'workstation_id', None) or 
                getattr(args[0].config, 'id', None) if (args and hasattr(args[0], 'config')) else None
            )
            
            # Проверить circuit breaker
            if error_handler.is_circuit_breaker_active(category, workstation_id):
                op_name = operation_name or func.__name__
                logger = get_logger(LogCategory.SYSTEM)
                logger.logger.warning(
                    f"⚠️ Circuit breaker активен для {op_name}"
                )
                raise RuntimeError(
                    f"Circuit breaker активен для операции '{op_name}'. "
                    f"Пожалуйста, повторите попытку позже."
                )
            
            # Выполнить функцию
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(
                    e,
                    category=category,
                    context={'operation': operation_name or func.__name__}
                )
                raise
        
        # Вернуть правильный wrapper в зависимости от типа функции
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def is_operation_safe(
    error_handler: ErrorHandler,
    category: ErrorCategory,
    workstation_id: str = None
) -> bool:
    """Проверить, безопасно ли выполнять операцию.

    Args:
        error_handler: Обработчик ошибок
        category: Категория операции
        workstation_id: ID рабочей станции

    Returns:
        bool: True если операция безопасна
    """
    return not error_handler.is_circuit_breaker_active(category, workstation_id)

    return not error_handler.is_circuit_breaker_active(category, workstation_id)