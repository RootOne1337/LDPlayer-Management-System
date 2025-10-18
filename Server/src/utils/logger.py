"""
Система логирования операций системы управления LDPlayer эмуляторами.

Предоставляет структурированное логирование всех операций,
событий и ошибок в системе с поддержкой различных уровней логирования
и форматов вывода.
"""

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import sys
import os


class LogLevel(str, Enum):
    """Уровни логирования."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Категории логов."""
    SYSTEM = "system"
    WORKSTATION = "workstation"
    EMULATOR = "emulator"
    OPERATION = "operation"
    API = "api"
    WEBSOCKET = "websocket"
    SECURITY = "security"
    BACKUP = "backup"
    MONITORING = "monitoring"


class OperationType(str, Enum):
    """Типы операций для логирования."""
    CREATE = "create"
    DELETE = "delete"
    START = "start"
    STOP = "stop"
    RENAME = "rename"
    CLONE = "clone"
    MODIFY = "modify"
    BACKUP = "backup"
    RESTORE = "restore"
    CONNECTION = "connection"
    DISCONNECTION = "disconnection"


class StructuredLogger:
    """Структурированный логгер для системы."""

    def __init__(self, name: str, log_file: str = None, level: str = "INFO"):
        """Инициализация структурированного логгера.

        Args:
            name: Имя логгера
            log_file: Путь к файлу логов
            level: Уровень логирования
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Создать форматтер
        self.formatter = self._create_formatter()

        # Добавить обработчики если их нет
        if not self.logger.handlers:
            self._add_handlers(log_file)

    def _create_formatter(self) -> logging.Formatter:
        """Создать СВЕРХ ДЕТАЛЬНЫЙ форматтер для удалённой диагностики."""
        # Формат: [ВРЕМЯ.мс] УРОВЕНЬ | КАТЕГОРИЯ | файл.py:строка:функция() | СООБЩЕНИЕ
        return logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-15s | %(filename)s:%(lineno)d:%(funcName)s() | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _add_handlers(self, log_file: str = None) -> None:
        """Добавить обработчики логирования."""
        # Консольный обработчик с UTF-8 encoding
        import io
        console_handler = logging.StreamHandler(
            io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        )
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

        # Файловый обработчик
        if log_file:
            try:
                # Создать директорию для логов если не существует
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)

                # Ротация логов по размеру (10 MB) с UTF-8 encoding
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setFormatter(self.formatter)
                self.logger.addHandler(file_handler)

            except Exception as e:
                print(f"Ошибка создания файлового логгера: {e}")

    def log_operation(
        self,
        operation_type: OperationType,
        category: LogCategory,
        message: str,
        workstation_id: str = None,
        emulator_id: str = None,
        user_id: str = None,
        additional_data: Dict[str, Any] = None,
        level: LogLevel = LogLevel.INFO
    ):
        """Записать операцию в лог.

        Args:
            operation_type: Тип операции
            category: Категория лога
            message: Сообщение
            workstation_id: ID рабочей станции
            emulator_id: ID эмулятора
            user_id: ID пользователя
            additional_data: Дополнительные данные
            level: Уровень логирования
        """
        # Создать структурированное сообщение
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type.value,
            "category": category.value,
            "message": message,
            "workstation_id": workstation_id,
            "emulator_id": emulator_id,
            "user_id": user_id,
            "additional_data": additional_data or {}
        }

        # Записать в лог
        log_message = json.dumps(log_data, default=str, ensure_ascii=False)

        if level == LogLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == LogLevel.INFO:
            self.logger.info(log_message)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_message)
        elif level == LogLevel.ERROR:
            self.logger.error(log_message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_message)

    def log_system_event(
        self,
        event: str,
        details: Dict[str, Any] = None,
        level: LogLevel = LogLevel.INFO
    ):
        """Записать системное событие.

        Args:
            event: Название события
            details: Детали события
            level: Уровень логирования
        """
        self.log_operation(
            OperationType.MODIFY,
            LogCategory.SYSTEM,
            f"Системное событие: {event}",
            additional_data=details or {},
            level=level
        )

    def log_workstation_event(
        self,
        workstation_id: str,
        event: str,
        details: Dict[str, Any] = None,
        level: LogLevel = LogLevel.INFO
    ):
        """Записать событие рабочей станции.

        Args:
            workstation_id: ID рабочей станции
            event: Название события
            details: Детали события
            level: Уровень логирования
        """
        self.log_operation(
            OperationType.MODIFY,
            LogCategory.WORKSTATION,
            f"Событие станции {workstation_id}: {event}",
            workstation_id=workstation_id,
            additional_data=details or {},
            level=level
        )

    def log_emulator_event(
        self,
        emulator_id: str,
        workstation_id: str,
        event: str,
        details: Dict[str, Any] = None,
        level: LogLevel = LogLevel.INFO
    ):
        """Записать событие эмулятора.

        Args:
            emulator_id: ID эмулятора
            workstation_id: ID рабочей станции
            event: Название события
            details: Детали события
            level: Уровень логирования
        """
        self.log_operation(
            OperationType.MODIFY,
            LogCategory.EMULATOR,
            f"Событие эмулятора {emulator_id}: {event}",
            workstation_id=workstation_id,
            emulator_id=emulator_id,
            additional_data=details or {},
            level=level
        )

    def log_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        user_id: str = None,
        details: Dict[str, Any] = None
    ):
        """Записать API запрос.

        Args:
            method: HTTP метод
            endpoint: Endpoint API
            status_code: Код ответа
            user_id: ID пользователя
            details: Дополнительные детали
        """
        level = LogLevel.INFO if status_code < 400 else LogLevel.WARNING

        self.log_operation(
            OperationType.MODIFY,
            LogCategory.API,
            f"API запрос: {method} {endpoint} -> {status_code}",
            user_id=user_id,
            additional_data={
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                **(details or {})
            },
            level=level
        )

    def log_error(
        self,
        error: Exception,
        context: str = "",
        workstation_id: str = None,
        emulator_id: str = None,
        additional_data: Dict[str, Any] = None
    ):
        """Записать ошибку в лог.

        Args:
            error: Исключение
            context: Контекст ошибки
            workstation_id: ID рабочей станции
            emulator_id: ID эмулятора
            additional_data: Дополнительные данные
        """
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            **(additional_data or {})
        }

        self.log_operation(
            OperationType.MODIFY,
            LogCategory.SYSTEM,
            f"Ошибка: {type(error).__name__}: {str(error)}",
            workstation_id=workstation_id,
            emulator_id=emulator_id,
            additional_data=error_details,
            level=LogLevel.ERROR
        )


class LogManager:
    """Менеджер логирования системы."""

    def __init__(self, logs_dir: Path):
        """Инициализация менеджера логирования.

        Args:
            logs_dir: Директория для хранения логов
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Создать логгеры для разных компонентов
        self.system_logger = StructuredLogger(
            "system",
            str(self.logs_dir / "system.log")
        )

        self.workstation_logger = StructuredLogger(
            "workstation",
            str(self.logs_dir / "workstations.log")
        )

        self.emulator_logger = StructuredLogger(
            "emulator",
            str(self.logs_dir / "emulators.log")
        )

        self.api_logger = StructuredLogger(
            "api",
            str(self.logs_dir / "api.log")
        )

        self.websocket_logger = StructuredLogger(
            "websocket",
            str(self.logs_dir / "websocket.log")
        )

        self.security_logger = StructuredLogger(
            "security",
            str(self.logs_dir / "security.log")
        )

        self.backup_logger = StructuredLogger(
            "backup",
            str(self.logs_dir / "backups.log")
        )

        self.monitoring_logger = StructuredLogger(
            "monitoring",
            str(self.logs_dir / "monitoring.log")
        )

    def get_logger(self, category: LogCategory) -> StructuredLogger:
        """Получить логгер по категории.

        Args:
            category: Категория логгера

        Returns:
            StructuredLogger: Логгер для категории
        """
        loggers = {
            LogCategory.SYSTEM: self.system_logger,
            LogCategory.WORKSTATION: self.workstation_logger,
            LogCategory.EMULATOR: self.emulator_logger,
            LogCategory.OPERATION: self.system_logger,
            LogCategory.API: self.api_logger,
            LogCategory.WEBSOCKET: self.websocket_logger,
            LogCategory.SECURITY: self.security_logger,
            LogCategory.BACKUP: self.backup_logger,
            LogCategory.MONITORING: self.monitoring_logger
        }

        return loggers.get(category, self.system_logger)

    def log_operation_start(
        self,
        operation_id: str,
        operation_type: OperationType,
        workstation_id: str,
        emulator_id: str = None,
        user_id: str = None
    ):
        """Записать начало операции.

        Args:
            operation_id: ID операции
            operation_type: Тип операции
            workstation_id: ID рабочей станции
            emulator_id: ID эмулятора
            user_id: ID пользователя
        """
        logger = self.get_logger(LogCategory.OPERATION)

        logger.log_operation(
            operation_type,
            LogCategory.OPERATION,
            f"Операция начата: {operation_id}",
            workstation_id=workstation_id,
            emulator_id=emulator_id,
            user_id=user_id,
            additional_data={"operation_id": operation_id, "status": "started"}
        )

    def log_operation_complete(
        self,
        operation_id: str,
        success: bool,
        message: str = None,
        error: str = None,
        duration: float = None
    ):
        """Записать завершение операции.

        Args:
            operation_id: ID операции
            success: Успешность операции
            message: Сообщение о результате
            error: Сообщение об ошибке
            duration: Длительность операции в секундах
        """
        logger = self.get_logger(LogCategory.OPERATION)

        level = LogLevel.INFO if success else LogLevel.ERROR

        logger.log_operation(
            OperationType.MODIFY,
            LogCategory.OPERATION,
            f"Операция завершена: {operation_id}",
            additional_data={
                "operation_id": operation_id,
                "success": success,
                "message": message,
                "error": error,
                "duration_seconds": duration
            },
            level=level
        )

    def log_emulator_created(
        self,
        emulator_id: str,
        name: str,
        workstation_id: str,
        user_id: str = None
    ):
        """Записать создание эмулятора.

        Args:
            emulator_id: ID эмулятора
            name: Имя эмулятора
            workstation_id: ID рабочей станции
            user_id: ID пользователя
        """
        logger = self.get_logger(LogCategory.EMULATOR)

        logger.log_emulator_event(
            emulator_id,
            workstation_id,
            f"Эмулятор создан: {name}",
            {"action": "created", "emulator_name": name},
            LogLevel.INFO
        )

    def log_emulator_deleted(
        self,
        emulator_id: str,
        name: str,
        workstation_id: str,
        user_id: str = None
    ):
        """Записать удаление эмулятора.

        Args:
            emulator_id: ID эмулятора
            name: Имя эмулятора
            workstation_id: ID рабочей станции
            user_id: ID пользователя
        """
        logger = self.get_logger(LogCategory.EMULATOR)

        logger.log_emulator_event(
            emulator_id,
            workstation_id,
            f"Эмулятор удален: {name}",
            {"action": "deleted", "emulator_name": name},
            LogLevel.WARNING
        )

    def log_emulator_started(
        self,
        emulator_id: str,
        name: str,
        workstation_id: str,
        user_id: str = None
    ):
        """Записать запуск эмулятора.

        Args:
            emulator_id: ID эмулятора
            name: Имя эмулятора
            workstation_id: ID рабочей станции
            user_id: ID пользователя
        """
        logger = self.get_logger(LogCategory.EMULATOR)

        logger.log_emulator_event(
            emulator_id,
            workstation_id,
            f"Эмулятор запущен: {name}",
            {"action": "started", "emulator_name": name},
            LogLevel.INFO
        )

    def log_emulator_stopped(
        self,
        emulator_id: str,
        name: str,
        workstation_id: str,
        user_id: str = None
    ):
        """Записать остановку эмулятора.

        Args:
            emulator_id: ID эмулятора
            name: Имя эмулятора
            workstation_id: ID рабочей станции
            user_id: ID пользователя
        """
        logger = self.get_logger(LogCategory.EMULATOR)

        logger.log_emulator_event(
            emulator_id,
            workstation_id,
            f"Эмулятор остановлен: {name}",
            {"action": "stopped", "emulator_name": name},
            LogLevel.INFO
        )

    def log_workstation_connected(self, workstation_id: str, ip_address: str) -> None:
        """Записать подключение к рабочей станции.

        Args:
            workstation_id: ID рабочей станции
            ip_address: IP адрес станции
        """
        logger = self.get_logger(LogCategory.WORKSTATION)

        logger.log_workstation_event(
            workstation_id,
            f"Подключение установлено: {ip_address}",
            {"action": "connected", "ip_address": ip_address},
            LogLevel.INFO
        )

    def log_workstation_disconnected(self, workstation_id: str, reason: str = None) -> None:
        """Записать отключение от рабочей станции.

        Args:
            workstation_id: ID рабочей станции
            reason: Причина отключения
        """
        logger = self.get_logger(LogCategory.WORKSTATION)

        logger.log_workstation_event(
            workstation_id,
            "Подключение потеряно",
            {"action": "disconnected", "reason": reason},
            LogLevel.WARNING
        )

    def log_backup_created(self, backup_name: str, total_files: int, size_mb: float) -> None:
        """Записать создание резервной копии.

        Args:
            backup_name: Имя резервной копии
            total_files: Количество файлов
            size_mb: Размер в МБ
        """
        logger = self.get_logger(LogCategory.BACKUP)

        logger.log_operation(
            OperationType.BACKUP,
            LogCategory.BACKUP,
            f"Резервная копия создана: {backup_name}",
            additional_data={
                "backup_name": backup_name,
                "total_files": total_files,
                "size_mb": size_mb
            },
            level=LogLevel.INFO
        )

    def log_system_startup(self, version: str) -> None:
        """Записать запуск системы.

        Args:
            version: Версия системы
        """
        logger = self.get_logger(LogCategory.SYSTEM)

        logger.log_system_event(
            "Система запущена",
            {"version": version, "action": "startup"},
            LogLevel.INFO
        )

    def log_system_shutdown(self) -> None:
        """Записать остановку системы."""
        logger = self.get_logger(LogCategory.SYSTEM)

        logger.log_system_event(
            "Система остановлена",
            {"action": "shutdown"},
            LogLevel.INFO
        )

    def cleanup_old_logs(self, max_age_days: int = 30) -> int:
        """Очистить старые логи.

        Args:
            max_age_days: Максимальный возраст файлов в днях

        Returns:
            int: Количество удаленных файлов
        """
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0

        try:
            for log_file in self.logs_dir.glob("*.log"):
                try:
                    # Проверить дату изменения файла
                    file_modified = datetime.fromtimestamp(log_file.stat().st_mtime)

                    if file_modified < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1

                except Exception as e:
                    print(f"Ошибка удаления файла {log_file}: {e}")

            if deleted_count > 0:
                self.system_logger.log_system_event(
                    "Старые логи удалены",
                    {"deleted_files": deleted_count, "max_age_days": max_age_days},
                    LogLevel.INFO
                )

            return deleted_count

        except Exception as e:
            self.system_logger.log_error(e, "Очистка старых логов")
            return 0


# Глобальный экземпляр менеджера логирования
_log_manager: Optional[LogManager] = None


def get_log_manager() -> LogManager:
    """Получить глобальный экземпляр менеджера логирования.

    Returns:
        LogManager: Менеджер логирования
    """
    global _log_manager

    if _log_manager is None:
        from ..core.config import get_config
        config = get_config()
        _log_manager = LogManager(config.logs_dir)

    return _log_manager


def get_logger(category: LogCategory) -> StructuredLogger:
    """Получить логгер по категории.

    Args:
        category: Категория логгера

    Returns:
        StructuredLogger: Логгер для категории
    """
    return get_log_manager().get_logger(category)


# Удобные функции для быстрого логирования

def log_system_info(message: str, **kwargs):
    """Записать информационное сообщение системы."""
    get_logger(LogCategory.SYSTEM).log_system_event(message, kwargs, LogLevel.INFO)


def log_system_error(error: Exception, context: str = "", **kwargs):
    """Записать ошибку системы."""
    logger = get_logger(LogCategory.SYSTEM)
    logger.log_error(error, context, additional_data=kwargs)


def log_workstation_info(workstation_id: str, message: str, **kwargs):
    """Записать информационное сообщение о рабочей станции."""
    get_logger(LogCategory.WORKSTATION).log_workstation_event(
        workstation_id, message, kwargs, LogLevel.INFO
    )


def log_emulator_info(emulator_id: str, workstation_id: str, message: str, **kwargs):
    """Записать информационное сообщение об эмуляторе."""
    get_logger(LogCategory.EMULATOR).log_emulator_event(
        emulator_id, workstation_id, message, kwargs, LogLevel.INFO
    )


def log_api_request(method: str, endpoint: str, status_code: int, **kwargs):
    """Записать API запрос."""
    get_logger(LogCategory.API).log_api_request(method, endpoint, status_code, **kwargs)


def log_backup_info(message: str, **kwargs):
    """Записать информационное сообщение о резервном копировании."""
    get_logger(LogCategory.BACKUP).log_operation(
        OperationType.BACKUP,
        LogCategory.BACKUP,
        message,
        additional_data=kwargs,
        level=LogLevel.INFO
    )