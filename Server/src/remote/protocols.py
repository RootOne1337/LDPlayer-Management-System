"""
Модули для удаленного подключения к рабочим станциям.

Поддерживает несколько протоколов:
- PyWinRM для Windows Remote Management
- SMB для файловой системы
- PowerShell Remoting для выполнения команд
- Альтернативные методы при недоступности основных
"""

import asyncio
import json
import os
import shutil
import subprocess
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager

try:
    import winrm
    WINRM_AVAILABLE = True
except ImportError:
    WINRM_AVAILABLE = False
    print("PyWinRM не установлен. Используйте: pip install pywinrm")

# SMB протокол использует стандартные os функции Windows
# Не требует дополнительных библиотек
SMB_AVAILABLE = True


from ..core.config import WorkstationConfig
from ..core.models import WorkstationStatus


class ConnectionProtocol:
    """Базовый класс для протоколов подключения."""

    def __init__(self, workstation_config: WorkstationConfig):
        """Инициализация протокола подключения.

        Args:
            workstation_config: Конфигурация рабочей станции
        """
        self.config = workstation_config
        self._connected = False
        self._last_error: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        """Проверить состояние подключения."""
        return self._connected

    @property
    def last_error(self) -> Optional[str]:
        """Получить последнее сообщение об ошибке."""
        return self._last_error

    def connect(self) -> bool:
        """Установить подключение."""
        raise NotImplementedError

    def disconnect(self) -> None:
        """Закрыть подключение."""
        self._connected = False

    def test_connection(self) -> bool:
        """Протестировать подключение."""
        raise NotImplementedError

    def execute_command(self, command: str, args: List[str] = None) -> Tuple[int, str, str]:
        """Выполнить команду на удаленной машине."""
        raise NotImplementedError


class WinRMProtocol(ConnectionProtocol):
    """Протокол на основе PyWinRM."""

    def __init__(self, workstation_config: WorkstationConfig):
        """Инициализация WinRM протокола."""
        super().__init__(workstation_config)
        self._session: Optional[winrm.Session] = None

    def connect(self) -> bool:
        """Установить WinRM подключение."""
        if not WINRM_AVAILABLE:
            self._last_error = "PyWinRM не установлен"
            return False

        try:
            # Определить endpoint
            endpoint = f"http://{self.config.ip_address}:{self.config.winrm_port}/wsman"

            # Создать сессию аутентификации
            if self.config.domain:
                # Доменная аутентификация
                self._session = winrm.Session(
                    endpoint,
                    auth=(f"{self.config.domain}\\{self.config.username}", self.config.password)
                )
            else:
                # Локальная аутентификация
                self._session = winrm.Session(
                    endpoint,
                    auth=(self.config.username, self.config.password)
                )

            # Тест подключения
            result = self._session.run_cmd('echo', ['test'])
            if result.status_code == 0:
                self._connected = True
                self._last_error = None
                return True
            else:
                self._last_error = f"Ошибка аутентификации: {result.status_code}"
                return False

        except Exception as e:
            self._last_error = f"Ошибка подключения: {e}"
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Закрыть WinRM подключение."""
        super().disconnect()
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass
            finally:
                self._session = None

    def test_connection(self) -> bool:
        """Протестировать WinRM подключение."""
        if not self._connected and not self.connect():
            return False

        try:
            result = self._session.run_cmd('echo', ['test'])
            return result.status_code == 0
        except Exception as e:
            self._last_error = f"Ошибка теста подключения: {e}"
            return False

    def execute_command(self, command: str, args: List[str] = None) -> Tuple[int, str, str]:
        """Выполнить команду через WinRM.

        Args:
            command: Команда для выполнения
            args: Аргументы команды

        Returns:
            Tuple[int, str, str]: (код возврата, stdout, stderr)
        """
        if not self._connected:
            return 1, "", "Не подключен к рабочей станции"

        try:
            args = args or []
            result = self._session.run_cmd(command, args)

            stdout = result.std_out.decode('utf-8', errors='ignore') if result.std_out else ""
            stderr = result.std_err.decode('utf-8', errors='ignore') if result.std_err else ""

            return result.status_code, stdout, stderr

        except Exception as e:
            self._last_error = f"Ошибка выполнения команды: {e}"
            return 1, "", str(e)


class SMBProtocol(ConnectionProtocol):
    """Протокол для работы с файловой системой через SMB."""

    def __init__(self, workstation_config: WorkstationConfig):
        """Инициализация SMB протокола."""
        super().__init__(workstation_config)
        self._mounted_paths: Dict[str, str] = {}

    def connect(self) -> bool:
        """Установить SMB подключение (проверить доступность)."""
        try:
            # Тест доступа к сетевому пути
            test_path = f'\\\\{self.config.ip_address}\\admin$'
            if os.path.exists(test_path):
                self._connected = True
                self._last_error = None
                return True
            else:
                self._last_error = "SMB путь недоступен"
                return False
        except Exception as e:
            self._last_error = f"Ошибка SMB подключения: {e}"
            return False

    def test_connection(self) -> bool:
        """Протестировать SMB подключение."""
        return self.connect()

    def execute_command(self, command: str, args: List[str] = None) -> Tuple[int, str, str]:
        """Выполнить команду через SMB (не поддерживается).

        SMB протокол предназначен только для файловых операций.
        """
        return 1, "", "SMB протокол не поддерживает выполнение команд"

    def copy_file(self, remote_path: str, local_path: str) -> bool:
        """Скопировать файл с удаленной машины.

        Args:
            remote_path: Путь к файлу на удаленной машине
            local_path: Локальный путь назначения

        Returns:
            bool: True если копирование успешно
        """
        if not self._connected:
            return False

        try:
            # Конвертировать путь в UNC формат
            if remote_path.startswith('C:'):
                remote_path = remote_path.replace('C:', f'\\\\{self.config.ip_address}\\C$', 1)

            # Создать локальную директорию если нужно
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Копировать файл
            shutil.copy2(remote_path, local_path)
            return True

        except Exception as e:
            self._last_error = f"Ошибка копирования файла: {e}"
            return False

    def copy_directory(self, remote_path: str, local_path: str) -> bool:
        """Скопировать директорию с удаленной машины.

        Args:
            remote_path: Путь к директории на удаленной машине
            local_path: Локальный путь назначения

        Returns:
            bool: True если копирование успешно
        """
        if not self._connected:
            return False

        try:
            # Конвертировать путь в UNC формат
            if remote_path.startswith('C:'):
                remote_path = remote_path.replace('C:', f'\\\\{self.config.ip_address}\\C$', 1)

            # Создать локальную директорию
            os.makedirs(local_path, exist_ok=True)

            # Использовать robocopy для копирования
            cmd = f'robocopy "{remote_path}" "{local_path}" /E /COPY:DAT /R:3 /W:10'
            result = subprocess.run(cmd, shell=True, capture_output=True)

            return result.returncode in [0, 1]  # 0 - успех, 1 - только копирование

        except Exception as e:
            self._last_error = f"Ошибка копирования директории: {e}"
            return False


class PowerShellProtocol(ConnectionProtocol):
    """Протокол на основе PowerShell Remoting."""

    def __init__(self, workstation_config: WorkstationConfig):
        """Инициализация PowerShell протокола."""
        super().__init__(workstation_config)
        self._process: Optional[subprocess.Popen] = None

    def connect(self) -> bool:
        """Установить PowerShell подключение."""
        try:
            # Тест PowerShell команды локально сначала
            result = subprocess.run(
                ['powershell', 'echo', 'test'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self._connected = True
                self._last_error = None
                return True
            else:
                self._last_error = f"PowerShell не доступен: {result.stderr}"
                return False

        except Exception as e:
            self._last_error = f"Ошибка PowerShell подключения: {e}"
            return False

    def test_connection(self) -> bool:
        """Протестировать PowerShell подключение."""
        return self.connect()

    def execute_command(self, command: str, args: List[str] = None) -> Tuple[int, str, str]:
        """Выполнить команду через PowerShell.

        Args:
            command: Команда для выполнения
            args: Аргументы команды

        Returns:
            Tuple[int, str, str]: (код возврата, stdout, stderr)
        """
        if not self._connected:
            return 1, "", "PowerShell не подключен"

        try:
            # Подготовить полную команду
            full_command = command
            if args:
                full_command += " " + " ".join(f'"{arg}"' if " " in arg else arg for arg in args)

            # Выполнить команду через PowerShell
            ps_command = f'Invoke-Command -ComputerName {self.config.ip_address} -ScriptBlock {{ {full_command} }}'

            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=60
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return 1, "", "Таймаут выполнения команды"
        except Exception as e:
            self._last_error = f"Ошибка выполнения PowerShell команды: {e}"
            return 1, "", str(e)


class FallbackProtocol(ConnectionProtocol):
    """Резервный протокол с альтернативными методами подключения."""

    def __init__(self, workstation_config: WorkstationConfig):
        """Инициализация резервного протокола."""
        super().__init__(workstation_config)
        self._protocols: List[ConnectionProtocol] = []

        # Создать экземпляры всех доступных протоколов
        if WINRM_AVAILABLE:
            self._protocols.append(WinRMProtocol(workstation_config))
        if SMB_AVAILABLE:
            self._protocols.append(SMBProtocol(workstation_config))
        self._protocols.append(PowerShellProtocol(workstation_config))

    def connect(self) -> bool:
        """Попытаться подключиться через доступные протоколы."""
        for protocol in self._protocols:
            if protocol.connect():
                self._connected = True
                self._last_error = None
                return True

        self._last_error = "Не удалось подключиться ни через один протокол"
        return False

    def test_connection(self) -> bool:
        """Протестировать подключение через доступные протоколы."""
        for protocol in self._protocols:
            if protocol.test_connection():
                return True

        return False

    def execute_command(self, command: str, args: List[str] = None) -> Tuple[int, str, str]:
        """Выполнить команду через первый доступный протокол."""
        for protocol in self._protocols:
            if protocol.is_connected:
                return protocol.execute_command(command, args)

        return 1, "", "Нет доступных протоколов для выполнения команды"


class RemoteConnectionManager:
    """Менеджер удаленных подключений с поддержкой нескольких протоколов."""

    def __init__(self, workstation_config: WorkstationConfig):
        """Инициализация менеджера подключений.

        Args:
            workstation_config: Конфигурация рабочей станции
        """
        self.config = workstation_config
        self._primary_protocol: Optional[ConnectionProtocol] = None
        self._fallback_protocol: Optional[FallbackProtocol] = None
        self._connection_attempts: int = 0
        self._max_attempts: int = 3

    def connect(self) -> bool:
        """Установить подключение к рабочей станции.

        Returns:
            bool: True если подключение успешно
        """
        # Создать протоколы если нужно
        if not self._primary_protocol:
            if WINRM_AVAILABLE:
                self._primary_protocol = WinRMProtocol(self.config)
            else:
                self._primary_protocol = PowerShellProtocol(self.config)

        if not self._fallback_protocol:
            self._fallback_protocol = FallbackProtocol(self.config)

        # Попытка подключения через основной протокол
        if self._primary_protocol.connect():
            self._connection_attempts = 0
            return True

        # Попытка подключения через резервные протоколы
        if self._fallback_protocol.connect():
            self._connection_attempts = 0
            return True

        self._connection_attempts += 1
        return False

    def disconnect(self) -> None:
        """Закрыть все подключения."""
        if self._primary_protocol:
            self._primary_protocol.disconnect()
        if self._fallback_protocol:
            self._fallback_protocol.disconnect()

    def is_connected(self) -> bool:
        """Проверить состояние подключения."""
        if self._primary_protocol and self._primary_protocol.is_connected:
            return True
        if self._fallback_protocol and self._fallback_protocol.is_connected:
            return True
        return False

    def execute_command(self, command: str, args: List[str] = None) -> Tuple[int, str, str]:
        """Выполнить команду на удаленной машине.

        Args:
            command: Команда для выполнения
            args: Аргументы команды

        Returns:
            Tuple[int, str, str]: (код возврата, stdout, stderr)
        """
        # Попробовать через основной протокол
        if self._primary_protocol and self._primary_protocol.is_connected:
            return self._primary_protocol.execute_command(command, args)

        # Попробовать через резервный протокол
        if self._fallback_protocol and self._fallback_protocol.is_connected:
            return self._fallback_protocol.execute_command(command, args)

        # Если не подключены, попробовать подключиться
        if self.connect():
            return self.execute_command(command, args)

        return 1, "", "Не удалось подключиться к рабочей станции"

    def copy_file(self, remote_path: str, local_path: str) -> bool:
        """Скопировать файл с удаленной машины.

        Args:
            remote_path: Путь к файлу на удаленной машине
            local_path: Локальный путь назначения

        Returns:
            bool: True если копирование успешно
        """
        # Найти SMB протокол для файловых операций
        smb_protocol = None

        if self._primary_protocol and isinstance(self._primary_protocol, SMBProtocol):
            smb_protocol = self._primary_protocol
        elif self._fallback_protocol:
            for protocol in self._fallback_protocol._protocols:
                if isinstance(protocol, SMBProtocol):
                    smb_protocol = protocol
                    break

        if smb_protocol and smb_protocol.is_connected:
            return smb_protocol.copy_file(remote_path, local_path)

        return False

    def test_connection(self) -> Tuple[bool, str]:
        """Протестировать подключение к рабочей станции.

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Тест базового подключения
            if not self.is_connected and not self.connect():
                return False, "Не удалось установить соединение"

            # Тест команды echo
            status_code, stdout, stderr = self.execute_command('echo', ['test'])
            if status_code != 0:
                return False, f"Ошибка выполнения тестовой команды: {stderr}"

            # Тест существования ldconsole.exe
            ldconsole_path = self.config.ldconsole_path.replace('\\', '\\\\')
            status_code, _, stderr = self.execute_command('dir', [ldconsole_path])
            if status_code != 0:
                return False, f"ldconsole.exe не найден: {stderr}"

            return True, "Подключение успешно протестировано"

        except Exception as e:
            return False, f"Ошибка тестирования подключения: {e}"

    @contextmanager
    def connection_context(self):
        """Контекстный менеджер для автоматического управления подключением."""
        try:
            self.connect()
            yield self
        finally:
            self.disconnect()


class ConnectionPool:
    """Пул подключений для управления несколькими рабочими станциями."""

    def __init__(self):
        """Инициализация пула подключений."""
        self._connections: Dict[str, RemoteConnectionManager] = {}
        self._lock = asyncio.Lock()

    def get_connection(self, workstation_config: WorkstationConfig) -> RemoteConnectionManager:
        """Получить менеджер подключений для рабочей станции.

        Args:
            workstation_config: Конфигурация рабочей станции

        Returns:
            RemoteConnectionManager: Менеджер подключений
        """
        if workstation_config.id not in self._connections:
            self._connections[workstation_config.id] = RemoteConnectionManager(workstation_config)

        return self._connections[workstation_config.id]

    async def connect_all(self) -> Dict[str, bool]:
        """Подключиться ко всем рабочим станциям.

        Returns:
            Dict[str, bool]: Словарь с результатами подключения
            ключ - ID станции, значение - успех подключения
        """
        results = {}

        async with self._lock:
            for workstation_id, connection in self._connections.items():
                results[workstation_id] = connection.connect()

        return results

    async def disconnect_all(self) -> None:
        """Отключиться от всех рабочих станций."""
        async with self._lock:
            for connection in self._connections.values():
                connection.disconnect()

    def get_connected_workstations(self) -> List[str]:
        """Получить список ID подключенных рабочих станций.

        Returns:
            List[str]: Список ID подключенных станций
        """
        connected = []
        for workstation_id, connection in self._connections.items():
            if connection.is_connected:
                connected.append(workstation_id)
        return connected

    def cleanup(self) -> None:
        """Очистить пул подключений."""
        for connection in self._connections.values():
            connection.disconnect()
        self._connections.clear()


# Глобальный пул подключений
connection_pool = ConnectionPool()


def get_connection_manager(workstation_config: WorkstationConfig) -> RemoteConnectionManager:
    """Получить менеджер подключений для рабочей станции.

    Args:
        workstation_config: Конфигурация рабочей станции

    Returns:
        RemoteConnectionManager: Менеджер подключений
    """
    return connection_pool.get_connection(workstation_config)