"""
Менеджер для управления LDPlayer эмуляторами через командную строку.

Предоставляет высокоуровневый интерфейс для выполнения операций
с эмуляторами на удаленных рабочих станциях.
"""

import asyncio
import json
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum

from ..core.models import (
    Emulator, EmulatorStatus, EmulatorConfig,
    Operation, OperationType, OperationStatus
)
from .workstation import WorkstationManager
from ..utils.error_handler import with_circuit_breaker, ErrorCategory


class CommandType(str, Enum):
    """Типы команд LDPlayer."""
    ADD = "add"
    REMOVE = "remove"
    LAUNCH = "launch"
    QUIT = "quit"
    RENAME = "rename"
    LIST = "list"
    RUNNING_LIST = "runninglist"
    RUN_APP = "runapp"
    INSTALL_APP = "installapp"
    MODIFY = "modify"
    COPY = "copy"
    BACKUP = "backup"
    RESTORE = "restore"


class LDPlayerManager:
    """Менеджер операций с LDPlayer эмуляторами."""

    def __init__(self, workstation_manager: WorkstationManager):
        """Инициализация менеджера LDPlayer.

        Args:
            workstation_manager: Менеджер рабочей станции
        """
        self.workstation = workstation_manager
        self._operation_queue: asyncio.Queue[Operation] = asyncio.Queue()
        self._active_operations: Dict[str, Operation] = {}
        self._operation_timeout: int = 300  # 5 минут таймаут

    async def start_operation_processor(self) -> None:
        """Запустить обработчик очереди операций."""
        while True:
            try:
                # Получить операцию из очереди
                operation = await self._operation_queue.get()

                # Выполнить операцию асинхронно
                asyncio.create_task(self._execute_operation(operation))

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка в обработчике операций: {e}")

    def queue_operation(self, operation: Operation) -> None:
        """Добавить операцию в очередь.

        Args:
            operation: Операция для выполнения
        """
        self._active_operations[operation.id] = operation
        self._operation_queue.put_nowait(operation)

    async def _execute_operation(self, operation: Operation) -> None:
        """Выполнить операцию.

        Args:
            operation: Операция для выполнения
        """
        try:
            operation.start()

            # Выполнить операцию в зависимости от типа
            if operation.type == OperationType.CREATE:
                success, message = await self._create_emulator_async(
                    operation.parameters.get('name', ''),
                    operation.parameters.get('config')
                )
            elif operation.type == OperationType.DELETE:
                success, message = await self._delete_emulator_async(
                    operation.parameters.get('name', '')
                )
            elif operation.type == OperationType.START:
                success, message = await self._start_emulator_async(
                    operation.parameters.get('name', '')
                )
            elif operation.type == OperationType.STOP:
                success, message = await self._stop_emulator_async(
                    operation.parameters.get('name', '')
                )
            elif operation.type == OperationType.RENAME:
                success, message = await self._rename_emulator_async(
                    operation.parameters.get('old_name', ''),
                    operation.parameters.get('new_name', '')
                )
            else:
                success = False
                message = f"Неизвестный тип операции: {operation.type}"

            # Завершить операцию
            operation.complete(success, message)

        except Exception as e:
            operation.complete(False, error=str(e))
        finally:
            # Удалить из активных операций
            self._active_operations.pop(operation.id, None)

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Create emulator async")
    async def _create_emulator_async(self, name: str, config: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Асинхронное создание эмулятора.

        Args:
            name: Имя эмулятора
            config: Конфигурация эмулятора

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        # Выполнить в executor для избежания блокировки
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.workstation.create_emulator,
            name,
            config
        )

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Delete emulator async")
    async def _delete_emulator_async(self, name: str) -> Tuple[bool, str]:
        """Асинхронное удаление эмулятора."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.workstation.delete_emulator,
            name
        )

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Start emulator async")
    async def _start_emulator_async(self, name: str) -> Tuple[bool, str]:
        """Асинхронный запуск эмулятора."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.workstation.start_emulator,
            name
        )

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Stop emulator async")
    async def _stop_emulator_async(self, name: str) -> Tuple[bool, str]:
        """Асинхронная остановка эмулятора."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.workstation.stop_emulator,
            name
        )

    async def _rename_emulator_async(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """Асинхронное переименование эмулятора."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.workstation.rename_emulator,
            old_name,
            new_name
        )

    def create_emulator(self, name: str, config: EmulatorConfig = None) -> Operation:
        """Создать эмулятор.

        Args:
            name: Имя эмулятора
            config: Конфигурация эмулятора

        Returns:
            Operation: Объект операции
        """
        operation = Operation(
            id=f"create_{name}_{int(time.time())}",
            type=OperationType.CREATE,
            emulator_id=f"{self.workstation.config.id}_{name}",
            workstation_id=self.workstation.config.id,
            parameters={
                'name': name,
                'config': config.__dict__ if config else None
            }
        )

        self.queue_operation(operation)
        return operation

    def delete_emulator(self, name: str) -> Operation:
        """Удалить эмулятор.

        Args:
            name: Имя эмулятора

        Returns:
            Operation: Объект операции
        """
        operation = Operation(
            id=f"delete_{name}_{int(time.time())}",
            type=OperationType.DELETE,
            emulator_id=f"{self.workstation.config.id}_{name}",
            workstation_id=self.workstation.config.id,
            parameters={'name': name}
        )

        self.queue_operation(operation)
        return operation

    def start_emulator(self, name: str) -> Operation:
        """Запустить эмулятор.

        Args:
            name: Имя эмулятора

        Returns:
            Operation: Объект операции
        """
        operation = Operation(
            id=f"start_{name}_{int(time.time())}",
            type=OperationType.START,
            emulator_id=f"{self.workstation.config.id}_{name}",
            workstation_id=self.workstation.config.id,
            parameters={'name': name}
        )

        self.queue_operation(operation)
        return operation

    def stop_emulator(self, name: str) -> Operation:
        """Остановить эмулятор.

        Args:
            name: Имя эмулятора

        Returns:
            Operation: Объект операции
        """
        operation = Operation(
            id=f"stop_{name}_{int(time.time())}",
            type=OperationType.STOP,
            emulator_id=f"{self.workstation.config.id}_{name}",
            workstation_id=self.workstation.config.id,
            parameters={'name': name}
        )

        self.queue_operation(operation)
        return operation

    def rename_emulator(self, old_name: str, new_name: str) -> Operation:
        """Переименовать эмулятор.

        Args:
            old_name: Текущее имя эмулятора
            new_name: Новое имя эмулятора

        Returns:
            Operation: Объект операции
        """
        operation = Operation(
            id=f"rename_{old_name}_{new_name}_{int(time.time())}",
            type=OperationType.RENAME,
            emulator_id=f"{self.workstation.config.id}_{old_name}",
            workstation_id=self.workstation.config.id,
            parameters={
                'old_name': old_name,
                'new_name': new_name
            }
        )

        self.queue_operation(operation)
        return operation

    def get_emulators(self) -> List[Emulator]:
        """Получить список эмуляторов на рабочей станции.

        Returns:
            List[Emulator]: Список эмуляторов
        """
        return self.workstation.get_emulators_list()

    def get_emulator(self, name: str) -> Optional[Emulator]:
        """Получить эмулятор по имени.

        Args:
            name: Имя эмулятора

        Returns:
            Optional[Emulator]: Объект эмулятора или None
        """
        emulators = self.get_emulators()
        return next((emu for emu in emulators if emu.name == name), None)

    def get_operation(self, operation_id: str) -> Optional[Operation]:
        """Получить операцию по ID.

        Args:
            operation_id: ID операции

        Returns:
            Optional[Operation]: Объект операции или None
        """
        return self._active_operations.get(operation_id)

    def get_active_operations(self) -> List[Operation]:
        """Получить список активных операций.

        Returns:
            List[Operation]: Список активных операций
        """
        return list(self._active_operations.values())

    def cancel_operation(self, operation_id: str) -> bool:
        """Отменить операцию.

        Args:
            operation_id: ID операции для отмены

        Returns:
            bool: True если операция была отменена
        """
        operation = self._active_operations.get(operation_id)
        if operation and operation.status == OperationStatus.RUNNING:
            operation.cancel()
            return True
        return False

    async def wait_for_operation(self, operation_id: str, timeout: int = None) -> Operation:
        """Ожидать завершения операции.

        Args:
            operation_id: ID операции
            timeout: Таймаут ожидания в секундах

        Returns:
            Operation: Завершенная операция

        Raises:
            asyncio.TimeoutError: Если операция не завершилась в таймаут
        """
        operation = self._active_operations.get(operation_id)
        if not operation:
            raise ValueError(f"Операция {operation_id} не найдена")

        timeout = timeout or self._operation_timeout

        start_time = datetime.now()
        while operation.status in [OperationStatus.PENDING, OperationStatus.RUNNING]:
            if datetime.now() - start_time > timedelta(seconds=timeout):
                raise asyncio.TimeoutError(f"Таймаут ожидания операции {operation_id}")

            await asyncio.sleep(1)

        return operation

    def cleanup_completed_operations(self, keep_hours: int = 1) -> int:
        """
        Clean up completed operations from memory.
        
        Removes operations that have been completed for more than keep_hours.
        Useful for preventing memory leaks from accumulation of old operations.
        
        Args:
            keep_hours: Hours to keep completed operations (default 1 hour)
        
        Returns:
            int: Number of operations cleaned up
        """
        from datetime import datetime, timedelta
        from ..core.models import OperationStatus
        
        current_time = datetime.now()
        threshold_time = current_time - timedelta(hours=keep_hours)
        
        operations_to_remove = []
        
        for op_id, operation in self._active_operations.items():
            # Check if operation is completed
            if operation.status in [OperationStatus.SUCCESS, OperationStatus.FAILED, OperationStatus.CANCELLED]:
                # Check if it completed before threshold
                if hasattr(operation, 'completed_at') and operation.completed_at:
                    if operation.completed_at < threshold_time:
                        operations_to_remove.append(op_id)
                # If no completed_at time, check against end_time from update
                elif hasattr(operation, 'updated_at') and operation.updated_at:
                    if operation.updated_at < threshold_time:
                        operations_to_remove.append(op_id)
        
        # Remove identified operations
        for op_id in operations_to_remove:
            del self._active_operations[op_id]
        
        return len(operations_to_remove)

    def clone_emulator(self, source_name: str, new_name: str, config: EmulatorConfig = None) -> Operation:
        """Клонировать эмулятор.

        Args:
            source_name: Имя исходного эмулятора
            new_name: Имя нового эмулятора
            config: Конфигурация для нового эмулятора

        Returns:
            Operation: Объект операции клонирования
        """
        # Получить конфигурацию исходного эмулятора
        source_emulator = self.get_emulator(source_name)
        if not source_emulator:
            raise ValueError(f"Исходный эмулятор '{source_name}' не найден")

        # Создать операцию клонирования
        operation = Operation(
            id=f"clone_{source_name}_{new_name}_{int(time.time())}",
            type=OperationType.CLONE,
            emulator_id=f"{self.workstation.config.id}_{new_name}",
            workstation_id=self.workstation.config.id,
            parameters={
                'source_name': source_name,
                'new_name': new_name,
                # ✅ SAFE: Проверяем наличие config перед обращением
                'config': (config.__dict__ if config 
                          else (source_emulator.config.__dict__ if hasattr(source_emulator, 'config') and source_emulator.config
                                else {}))
            }
        )

        self.queue_operation(operation)
        return operation

    def batch_operation(self, emulator_names: List[str], operation_type: OperationType,
                       **kwargs) -> List[Operation]:
        """Выполнить групповую операцию с несколькими эмуляторами.

        Args:
            emulator_names: Список имен эмуляторов
            operation_type: Тип операции
            **kwargs: Дополнительные параметры операции

        Returns:
            List[Operation]: Список операций
        """
        operations = []

        for name in emulator_names:
            operation = Operation(
                id=f"batch_{operation_type.value}_{name}_{int(time.time())}",
                type=operation_type,
                emulator_id=f"{self.workstation.config.id}_{name}",
                workstation_id=self.workstation.config.id,
                parameters={'name': name, **kwargs}
            )

            operations.append(operation)
            self.queue_operation(operation)

        return operations

    def get_system_stats(self) -> Dict[str, Any]:
        """Получить статистику системы.

        Returns:
            Dict[str, Any]: Статистика системы
        """
        return self.workstation.get_system_info()

    def backup_emulators(self, backup_path: str) -> Tuple[bool, str]:
        """Создать резервную копию всех эмуляторов.

        Args:
            backup_path: Путь для сохранения резервной копии

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        return self.workstation.backup_configs(backup_path)

    def is_operation_safe(self, operation: Operation, active_emulators: List[Emulator]) -> Tuple[bool, str]:
        """Проверить безопасность выполнения операции.

        Args:
            operation: Операция для проверки
            active_emulators: Список активных эмуляторов

        Returns:
            Tuple[bool, str]: (безопасно, причина)
        """
        emulator_name = operation.parameters.get('name')

        if operation.type == OperationType.DELETE:
            # Проверить, что эмулятор не запущен
            emulator = next((emu for emu in active_emulators if emu.name == emulator_name), None)
            if emulator and emulator.status == EmulatorStatus.RUNNING:
                return False, f"Нельзя удалить запущенный эмулятор '{emulator_name}'"

        elif operation.type == OperationType.CREATE:
            # Проверить, что имя не занято
            name_exists = any(emu.name == emulator_name for emu in active_emulators)
            if name_exists:
                return False, f"Эмулятор с именем '{emulator_name}' уже существует"

        elif operation.type == OperationType.RENAME:
            new_name = operation.parameters.get('new_name')
            # Проверить, что новое имя не занято
            name_exists = any(emu.name == new_name for emu in active_emulators)
            if name_exists:
                return False, f"Эмулятор с именем '{new_name}' уже существует"

        return True, "Операция безопасна"


class LDPlayerCommandBuilder:
    """Построитель команд для LDPlayer."""

    @staticmethod
    def build_create_command(name: str, config: EmulatorConfig) -> List[str]:
        """Построить команду создания эмулятора.

        Args:
            name: Имя эмулятора
            config: Конфигурация эмулятора

        Returns:
            List[str]: Список параметров команды
        """
        params = ['add', '--name', name]

        # Добавить параметры конфигурации
        config_params = config.to_ldconsole_params()
        params.extend(config_params)

        return params

    @staticmethod
    def build_launch_command(name: str) -> List[str]:
        """Построить команду запуска эмулятора.

        Args:
            name: Имя эмулятора

        Returns:
            List[str]: Список параметров команды
        """
        return ['launch', '--name', name]

    @staticmethod
    def build_quit_command(name: str) -> List[str]:
        """Построить команду остановки эмулятора.

        Args:
            name: Имя эмулятора

        Returns:
            List[str]: Список параметров команды
        """
        return ['quit', '--name', name]

    @staticmethod
    def build_remove_command(name: str) -> List[str]:
        """Построить команду удаления эмулятора.

        Args:
            name: Имя эмулятора

        Returns:
            List[str]: Список параметров команды
        """
        return ['remove', '--name', name]

    @staticmethod
    def build_rename_command(old_name: str, new_name: str) -> List[str]:
        """Построить команду переименования эмулятора.

        Args:
            old_name: Текущее имя эмулятора
            new_name: Новое имя эмулятора

        Returns:
            List[str]: Список параметров команды
        """
        # ✅ FIX: Используем --title вместо --newname согласно LDPlayer документации
        return ['rename', '--name', old_name, '--title', new_name]

    @staticmethod
    def build_list_command() -> List[str]:
        """Построить команду получения списка эмуляторов.

        Returns:
            List[str]: Список параметров команды
        """
        return ['list']

    @staticmethod
    def build_running_list_command() -> List[str]:
        """Построить команду получения списка запущенных эмуляторов.

        Returns:
            List[str]: Список параметров команды
        """
        return ['runninglist']
