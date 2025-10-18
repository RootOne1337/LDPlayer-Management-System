"""
Класс для управления удаленными рабочими станциями с LDPlayer.

Предоставляет интерфейс для подключения к удаленным машинам,
выполнения команд ldconsole.exe и мониторинга состояния.
"""

import asyncio
import json
import os
import subprocess
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path

# Retry mechanism
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    print("⚠️ Tenacity не установлена. Retry механизм недоступен. Используйте: pip install tenacity")
    # Создаём dummy decorator если tenacity нет
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    stop_after_attempt = wait_exponential = retry_if_exception_type = lambda x: x

try:
    import winrm
    WINRM_AVAILABLE = True
except ImportError:
    WINRM_AVAILABLE = False
    print("PyWinRM не установлен. Используйте: pip install pywinrm")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil не установлен. Локальный мониторинг недоступен.")

from ..core.models import Workstation as WorkstationModel, WorkstationStatus, Emulator, EmulatorStatus
from ..core.config import WorkstationConfig
from ..utils.error_handler import with_circuit_breaker, ErrorCategory


class WorkstationManager:
    """Менеджер для управления удаленными рабочими станциями."""

    def __init__(self, config: WorkstationConfig):
        """Инициализация менеджера рабочей станции.

        Args:
            config: Конфигурация рабочей станции
        """
        self.config = config
        self._winrm_session: Optional[winrm.Session] = None
        self._last_connection_attempt: Optional[datetime] = None
        self._connection_errors: int = 0
        self._max_connection_errors: int = 3

        # Кэш данных
        self._emulators_cache: Optional[List[Emulator]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl: int = 30  # секунды

    @property
    def is_connected(self) -> bool:
        """Проверить подключение к рабочей станции.

        Returns:
            bool: True если подключение активно
        """
        if self._winrm_session is None:
            return False

        try:
            # Простая проверка подключения
            self._winrm_session.run_cmd('echo', ['test'])
            return True
        except Exception:
            return False

    @with_circuit_breaker(ErrorCategory.NETWORK, operation_name="Connect to workstation")
    def connect(self) -> bool:
        """Подключиться к рабочей станции.

        Returns:
            bool: True если подключение успешно
        """
        # Проверка частоты попыток подключения
        if (self._last_connection_attempt and
            datetime.now() - self._last_connection_attempt < timedelta(seconds=10)):
            return False

        self._last_connection_attempt = datetime.now()

        try:
            if not WINRM_AVAILABLE:
                print(f"PyWinRM недоступен для станции {self.config.name}")
                return False

            # Создание сессии WinRM
            endpoint = f"http://{self.config.ip_address}:{self.config.winrm_port}/wsman"

            if self.config.domain:
                # Доменная аутентификация
                self._winrm_session = winrm.Session(
                    endpoint,
                    auth=(f"{self.config.domain}\\{self.config.username}", self.config.password)
                )
            else:
                # Локальная аутентификация
                self._winrm_session = winrm.Session(
                    endpoint,
                    auth=(self.config.username, self.config.password)
                )

            # Тест подключения
            result = self._winrm_session.run_cmd('echo', ['test'])
            if result.status_code == 0:
                self._connection_errors = 0
                self.config.status = WorkstationStatus.ONLINE
                self.config.last_seen = datetime.now()
                return True
            else:
                self._connection_errors += 1
                return False

        except Exception as e:
            print(f"Ошибка подключения к {self.config.name}: {e}")
            self._connection_errors += 1
            self.config.status = WorkstationStatus.ERROR
            return False

    def disconnect(self) -> None:
        """Отключиться от рабочей станции."""
        if self._winrm_session:
            try:
                self._winrm_session.close()
            except Exception:
                pass
            finally:
                self._winrm_session = None

        self.config.status = WorkstationStatus.OFFLINE

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
        reraise=True
    )
    def run_command(self, command: str, args: List[str] = None, timeout: int = 30) -> Tuple[int, str, str]:
        """Выполнить команду на удаленной рабочей станции.

        Args:
            command: Команда для выполнения
            args: Аргументы команды
            timeout: Таймаут выполнения команды в секундах (default: 30)

        Returns:
            Tuple[int, str, str]: (код возврата, stdout, stderr)
        
        Raises:
            ConnectionError: Если не удалось подключиться
            TimeoutError: Если команда выполнялась дольше timeout
        """
        if not self.is_connected and not self.connect():
            raise ConnectionError("Не удалось подключиться к рабочей станции")

        try:
            args = args or []
            # Используем timeout если WinRM поддерживает
            result = self._winrm_session.run_cmd(command, args)

            stdout = result.std_out.decode('utf-8', errors='ignore') if result.std_out else ""
            stderr = result.std_err.decode('utf-8', errors='ignore') if result.std_err else ""

            return result.status_code, stdout, stderr

        except Exception as e:
            self._connection_errors += 1
            # Преобразуем в типы для retry
            if "timeout" in str(e).lower():
                raise TimeoutError(f"Команда превысила timeout ({timeout}s): {e}")
            elif "connection" in str(e).lower() or "network" in str(e).lower():
                raise ConnectionError(f"Ошибка подключения: {e}")
            else:
                raise OSError(f"Ошибка выполнения команды: {e}")

    @with_circuit_breaker(ErrorCategory.EXTERNAL, operation_name="Run LDConsole command")
    def run_ldconsole_command(self, action: str, emulator_name: str = None, timeout: int = 60, **kwargs) -> Tuple[int, str, str]:
        """Выполнить команду ldconsole.exe на удаленной станции.

        Args:
            action: Действие (add, remove, launch, quit, list, etc.)
            emulator_name: Имя эмулятора (если требуется)
            timeout: Таймаут выполнения команды в секундах (default: 60)
            **kwargs: Дополнительные параметры

        Returns:
            Tuple[int, str, str]: (код возврата, stdout, stderr)
        
        Note:
            Retry механизм наследуется от run_command (3 попытки с экспоненциальной задержкой)
        """
        # Подготовка команды
        cmd_args = [action]

        if emulator_name:
            cmd_args.extend(['--name', emulator_name])

        # Добавление дополнительных параметров
        for key, value in kwargs.items():
            if value is not None:
                cmd_args.extend([f'--{key}', str(value)])

        return self.run_command(self.config.ldconsole_path, cmd_args, timeout=timeout)

    @with_circuit_breaker(ErrorCategory.EXTERNAL, operation_name="Get emulators list")
    def get_emulators_list(self) -> List[Emulator]:
        """Получить список эмуляторов на рабочей станции.

        Returns:
            List[Emulator]: Список эмуляторов
        """
        # Проверка кэша
        if (self._emulators_cache and self._cache_timestamp and
            datetime.now() - self._cache_timestamp < timedelta(seconds=self._cache_ttl)):
            return self._emulators_cache

        try:
            # Выполнить команду list2 (расширенная информация)
            status_code, stdout, stderr = self.run_ldconsole_command('list2')

            if status_code != 0:
                print(f"Ошибка получения списка эмуляторов: {stderr}")
                return []

            # Парсинг вывода команды list2
            emulators = self._parse_emulators_list2(stdout)

            # Обновить кэш
            self._emulators_cache = emulators
            self._cache_timestamp = datetime.now()

            return emulators

        except Exception as e:
            print(f"Ошибка при получении списка эмуляторов: {e}")
            return []

    def _parse_emulators_list2(self, output: str) -> List[Emulator]:
        """Распарсить вывод команды list2.

        Args:
            output: Вывод команды ldconsole.exe list2

        Returns:
            List[Emulator]: Список эмуляторов
            
        Формат вывода list2:
        index,name,topWindowHandle,vBoxWindowHandle,binderWindowHandle,width,height,resWidth,resHeight,dpi
        Пример: 0,LDPlayer,0,0,0,-1,-1,960,540,160
        """
        emulators = []

        try:
            lines = output.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Парсинг CSV формата
                parts = line.split(',')
                
                if len(parts) >= 10:
                    try:
                        index = int(parts[0])
                        name = parts[1]
                        top_handle = int(parts[2])
                        vbox_handle = int(parts[3])
                        binder_handle = int(parts[4])
                        
                        # Определить статус по наличию активных handle
                        is_running = (top_handle != 0 or vbox_handle != 0 or binder_handle != 0)
                        status = EmulatorStatus.RUNNING if is_running else EmulatorStatus.STOPPED
                        
                        # Создать объект эмулятора
                        emulator = Emulator(
                            id=f"{self.config.id}_{name}",
                            name=name,
                            workstation_id=self.config.id,
                            status=status
                        )

                        emulators.append(emulator)
                        
                    except (ValueError, IndexError) as e:
                        print(f"Ошибка парсинга строки '{line}': {e}")
                        continue

        except Exception as e:
            print(f"Ошибка парсинга списка эмуляторов: {e}")

        return emulators

    def _parse_status(self, status_str: str) -> EmulatorStatus:
        """Преобразовать строковый статус в enum.

        Args:
            status_str: Строковое представление статуса

        Returns:
            EmulatorStatus: Статус эмулятора
        """
        status_map = {
            'running': EmulatorStatus.RUNNING,
            'stopped': EmulatorStatus.STOPPED,
            'starting': EmulatorStatus.STARTING,
            'stopping': EmulatorStatus.STOPPING,
            'error': EmulatorStatus.ERROR
        }

        return status_map.get(status_str.lower(), EmulatorStatus.UNKNOWN)

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Create emulator")
    def create_emulator(self, name: str, config: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Создать новый эмулятор на рабочей станции.

        Args:
            name: Имя эмулятора
            config: Конфигурация эмулятора (опционально)

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Шаг 1: Создать эмулятор (без параметров - ldconsole создаст с автоименем)
            # ВАЖНО: ldconsole add возвращает индекс созданного эмулятора, а не 0!
            status_code, stdout, stderr = self.run_ldconsole_command('add')

            # Код возврата - это индекс созданного эмулятора (может быть > 0)
            # Ошибка только если код < 0 или есть stderr
            if status_code < 0 or (stderr and 'error' in stderr.lower()):
                return False, f"Ошибка создания эмулятора: {stderr if stderr else 'Неизвестная ошибка'}"

            # Шаг 2: Найти созданный эмулятор (будет последний в списке)
            # Получить список эмуляторов
            list_code, list_out, list_err = self.run_ldconsole_command('list2')
            
            if list_code != 0:
                return False, f"Эмулятор создан, но не удалось получить его имя: {list_err}"
            
            # Парсинг последнего эмулятора
            lines = list_out.strip().split('\n')
            if not lines:
                return False, "Эмулятор создан, но список пуст"
            
            last_line = lines[-1]
            parts = last_line.split(',')
            
            if len(parts) < 2:
                return False, f"Не удалось распарсить имя созданного эмулятора: {last_line}"
            
            created_name = parts[1]
            
            # Шаг 3: Переименовать в нужное имя
            if created_name != name:
                rename_code, rename_out, rename_err = self.run_ldconsole_command(
                    'rename',
                    created_name,
                    title=name
                )
                
                if rename_code != 0:
                    return False, f"Эмулятор '{created_name}' создан, но не удалось переименовать в '{name}': {rename_err}"
            
            # Шаг 4: Применить конфигурацию если есть
            if config:
                modify_params = {}
                
                if 'resolution' in config:
                    modify_params['resolution'] = config['resolution']
                if 'memory' in config:
                    modify_params['memory'] = config['memory']
                if 'cpu' in config:
                    modify_params['cpu'] = config['cpu']
                
                if modify_params:
                    # Применить конфигурацию через modify
                    mod_status, mod_stdout, mod_stderr = self.run_ldconsole_command('modify', name, **modify_params)
                    
                    if mod_status != 0:
                        return True, f"Эмулятор '{name}' создан, но не удалось применить конфигурацию: {mod_stderr}"
            
            # Очистить кэш
            self._emulators_cache = None
            return True, f"Эмулятор '{name}' успешно создан"

        except Exception as e:
            return False, f"Исключение при создании эмулятора: {e}"

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Delete emulator")
    def delete_emulator(self, name: str) -> Tuple[bool, str]:
        """Удалить эмулятор с рабочей станции.

        Args:
            name: Имя эмулятора для удаления

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Проверить, что эмулятор существует
            emulators = self.get_emulators_list()
            emulator_exists = any(emu.name == name for emu in emulators)

            if not emulator_exists:
                return False, f"Эмулятор '{name}' не найден"

            # Выполнить команду удаления
            status_code, stdout, stderr = self.run_ldconsole_command('remove', name)

            if status_code == 0:
                # Очистить кэш
                self._emulators_cache = None
                return True, f"Эмулятор '{name}' успешно удален"
            else:
                return False, f"Ошибка удаления эмулятора: {stderr}"

        except Exception as e:
            return False, f"Исключение при удалении эмулятора: {e}"

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Start emulator")
    def start_emulator(self, name: str) -> Tuple[bool, str]:
        """Запустить эмулятор на рабочей станции.

        Args:
            name: Имя эмулятора для запуска

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Проверить, что эмулятор существует
            emulators = self.get_emulators_list()
            emulator = next((emu for emu in emulators if emu.name == name), None)

            if not emulator:
                return False, f"Эмулятор '{name}' не найден"

            if emulator.status == EmulatorStatus.RUNNING:
                return True, f"Эмулятор '{name}' уже запущен"

            # Выполнить команду запуска
            status_code, stdout, stderr = self.run_ldconsole_command('launch', name)

            if status_code == 0:
                return True, f"Эмулятор '{name}' успешно запущен"
            else:
                return False, f"Ошибка запуска эмулятора: {stderr}"

        except Exception as e:
            return False, f"Исключение при запуске эмулятора: {e}"

    @with_circuit_breaker(ErrorCategory.EMULATOR, operation_name="Stop emulator")
    def stop_emulator(self, name: str) -> Tuple[bool, str]:
        """Остановить эмулятор на рабочей станции.

        Args:
            name: Имя эмулятора для остановки

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Проверить, что эмулятор существует
            emulators = self.get_emulators_list()
            emulator = next((emu for emu in emulators if emu.name == name), None)

            if not emulator:
                return False, f"Эмулятор '{name}' не найден"

            if emulator.status == EmulatorStatus.STOPPED:
                return True, f"Эмулятор '{name}' уже остановлен"

            # Выполнить команду остановки
            status_code, stdout, stderr = self.run_ldconsole_command('quit', name)

            if status_code == 0:
                return True, f"Эмулятор '{name}' успешно остановлен"
            else:
                return False, f"Ошибка остановки эмулятора: {stderr}"

        except Exception as e:
            return False, f"Исключение при остановке эмулятора: {e}"

    def rename_emulator(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """Переименовать эмулятор на рабочей станции.

        Args:
            old_name: Текущее имя эмулятора
            new_name: Новое имя эмулятора

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Проверить, что эмулятор существует
            emulators = self.get_emulators_list()
            emulator_exists = any(emu.name == old_name for emu in emulators)

            if not emulator_exists:
                return False, f"Эмулятор '{old_name}' не найден"

            # Проверить, что новое имя не занято
            name_taken = any(emu.name == new_name for emu in emulators)
            if name_taken:
                return False, f"Имя '{new_name}' уже используется"

            # Выполнить команду переименования
            # LDPlayer команда: ldconsole.exe rename <index|name> --title <new_name>
            status_code, stdout, stderr = self.run_ldconsole_command('rename', old_name, title=new_name)

            if status_code == 0:
                # Очистить кэш
                self._emulators_cache = None
                return True, f"Эмулятор переименован с '{old_name}' на '{new_name}'"
            else:
                return False, f"Ошибка переименования эмулятора: {stderr}"

        except Exception as e:
            return False, f"Исключение при переименовании эмулятора: {e}"

    def modify_emulator(self, name: str, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Изменить настройки эмулятора.

        Args:
            name: Имя эмулятора
            settings: Словарь с настройками для изменения

        Поддерживаемые настройки:
            - resolution: str - "width,height,dpi" (например: "1920,1080,240")
            - cpu: int - количество ядер (1, 2, 3, 4)
            - memory: int - размер памяти в MB (256, 512, 1024, 2048, 4096, 8192)
            - manufacturer: str - производитель (samsung, xiaomi, huawei, etc.)
            - model: str - модель устройства (SM-G960F, etc.)
            - pnumber: str - номер телефона
            - imei: str - IMEI (или "auto" для автогенерации)
            - imsi: str - IMSI (или "auto" для автогенерации)
            - simserial: str - серийный номер SIM (или "auto")
            - androidid: str - Android ID (или "auto")
            - mac: str - MAC адрес (или "auto")
            - autorotate: int - автоповорот (1 или 0)
            - lockwindow: int - блокировка окна (1 или 0)
            - root: int - root режим (1 или 0)

        Returns:
            Tuple[bool, str]: (успех, сообщение)

        Examples:
            # Изменить разрешение и производительность
            success, msg = manager.modify_emulator("nifilim", {
                "resolution": "1920,1080,240",
                "cpu": 4,
                "memory": 8192
            })

            # Изменить идентификацию устройства
            success, msg = manager.modify_emulator("nifilim", {
                "manufacturer": "samsung",
                "model": "SM-G960F",
                "imei": "auto",
                "mac": "auto"
            })
        """
        try:
            # Проверить, что эмулятор существует
            emulators = self.get_emulators_list()
            emulator_exists = any(emu.name == name for emu in emulators)

            if not emulator_exists:
                return False, f"Эмулятор '{name}' не найден"

            # Подготовить параметры для команды modify
            modify_params = {}

            # Производительность
            if 'resolution' in settings:
                modify_params['resolution'] = settings['resolution']
            
            if 'cpu' in settings:
                cpu_value = settings['cpu']
                if cpu_value not in [1, 2, 3, 4, 8]:
                    return False, f"Недопустимое значение CPU: {cpu_value}. Допустимые: 1, 2, 3, 4, 8"
                modify_params['cpu'] = cpu_value
            
            if 'memory' in settings:
                memory_value = settings['memory']
                allowed_memory = [256, 512, 768, 1024, 1536, 2048, 4096, 8192]
                if memory_value not in allowed_memory:
                    return False, f"Недопустимое значение памяти: {memory_value}. Допустимые: {allowed_memory}"
                modify_params['memory'] = memory_value

            # Идентификация устройства
            if 'manufacturer' in settings:
                modify_params['manufacturer'] = settings['manufacturer']
            
            if 'model' in settings:
                modify_params['model'] = settings['model']
            
            if 'pnumber' in settings:
                modify_params['pnumber'] = settings['pnumber']
            
            if 'imei' in settings:
                modify_params['imei'] = settings['imei']
            
            if 'imsi' in settings:
                modify_params['imsi'] = settings['imsi']
            
            if 'simserial' in settings:
                modify_params['simserial'] = settings['simserial']
            
            if 'androidid' in settings:
                modify_params['androidid'] = settings['androidid']
            
            if 'mac' in settings:
                modify_params['mac'] = settings['mac']

            # Системные настройки
            if 'autorotate' in settings:
                modify_params['autorotate'] = 1 if settings['autorotate'] else 0
            
            if 'lockwindow' in settings:
                modify_params['lockwindow'] = 1 if settings['lockwindow'] else 0
            
            if 'root' in settings:
                modify_params['root'] = 1 if settings['root'] else 0

            if not modify_params:
                return False, "Не указаны параметры для изменения"

            # Выполнить команду modify
            status_code, stdout, stderr = self.run_ldconsole_command('modify', name, **modify_params)

            if status_code == 0:
                # Очистить кэш
                self._emulators_cache = None
                
                # Сформировать сообщение с перечислением изменений
                changes = ", ".join([f"{k}={v}" for k, v in modify_params.items()])
                return True, f"Настройки эмулятора '{name}' изменены: {changes}"
            else:
                return False, f"Ошибка изменения настроек: {stderr if stderr else 'Неизвестная ошибка'}"

        except Exception as e:
            return False, f"Исключение при изменении настроек эмулятора: {e}"

    def get_emulator_status(self, name: str) -> Tuple[Optional[EmulatorStatus], str]:
        """Получить статус конкретного эмулятора.

        Args:
            name: Имя эмулятора

        Returns:
            Tuple[Optional[EmulatorStatus], str]: (статус, сообщение)
        """
        try:
            emulators = self.get_emulators_list()
            emulator = next((emu for emu in emulators if emu.name == name), None)

            if emulator:
                return emulator.status, "Статус получен успешно"
            else:
                return None, f"Эмулятор '{name}' не найден"

        except Exception as e:
            return None, f"Ошибка получения статуса: {e}"

    def get_system_info(self) -> Dict[str, Any]:
        """Получить информацию о системе рабочей станции.

        Returns:
            Dict[str, Any]: Информация о системе
        """
        info = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'ldplayer_processes': 0,
            'total_emulators': 0,
            'running_emulators': 0
        }

        try:
            # Получить информацию о процессах
            if self.is_connected:
                status_code, stdout, stderr = self.run_command('powershell', [
                    'Get-Process | Where-Object {$_.ProcessName -like "*ld*"} | Measure-Object | Select-Object -ExpandProperty Count'
                ])

                if status_code == 0:
                    try:
                        info['ldplayer_processes'] = int(stdout.strip())
                    except ValueError:
                        pass

            # Получить статистику эмуляторов
            emulators = self.get_emulators_list()
            info['total_emulators'] = len(emulators)
            info['running_emulators'] = len([emu for emu in emulators if emu.status == EmulatorStatus.RUNNING])

        except Exception as e:
            print(f"Ошибка получения системной информации: {e}")

        return info

    def backup_configs(self, backup_path: str) -> Tuple[bool, str]:
        """Создать резервную копию конфигураций эмуляторов.

        Args:
            backup_path: Путь для сохранения резервной копии

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Создать локальную папку для резервной копии
            backup_dir = Path(backup_path) / self.config.id / datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Скопировать конфигурационные файлы через SMB
            source_path = f'\\\\{self.config.ip_address}\\{self.config.configs_path.replace(":", "$")}'

            if self._copy_directory_smb(source_path, str(backup_dir)):
                return True, f"Резервная копия создана: {backup_dir}"
            else:
                return False, "Ошибка создания резервной копии"

        except Exception as e:
            return False, f"Исключение при создании резервной копии: {e}"

    def _copy_directory_smb(self, source: str, destination: str) -> bool:
        """Скопировать директорию через SMB.

        Args:
            source: Исходный путь SMB
            destination: Локальный путь назначения

        Returns:
            bool: True если копирование успешно
        """
        try:
            # Использовать robocopy для копирования
            cmd = f'robocopy "{source}" "{destination}" /E /COPY:DAT /R:3 /W:10'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            return result.returncode in [0, 1]  # 0 - успех, 1 - только копирование

        except Exception as e:
            print(f"Ошибка копирования через SMB: {e}")
            return False

    def test_connection(self) -> Tuple[bool, str]:
        """Протестировать подключение к рабочей станции.

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Тест базового подключения
            if not self.connect():
                return False, "Не удалось установить соединение"

            # Тест команды echo
            status_code, stdout, stderr = self.run_command('echo', ['test'])
            if status_code != 0:
                return False, f"Ошибка выполнения тестовой команды: {stderr}"

            # Тест существования ldconsole.exe
            status_code, _, stderr = self.run_command('dir', [self.config.ldconsole_path])
            if status_code != 0:
                return False, f"ldconsole.exe не найден: {stderr}"

            return True, "Подключение успешно протестировано"

        except Exception as e:
            return False, f"Ошибка тестирования подключения: {e}"

    def __enter__(self) -> 'WorkstationManager':
        """Контекстный менеджер - вход."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход."""
        self.disconnect()


class WorkstationMonitor:
    """Мониторинг рабочих станций."""

    def __init__(self, workstations: List[WorkstationManager]):
        """Инициализация мониторинга.

        Args:
            workstations: Список менеджеров рабочих станций
        """
        self.workstations = workstations
        self.monitoring_tasks: List[asyncio.Task] = []

    async def start_monitoring(self, interval: int = 30) -> None:
        """Начать мониторинг всех рабочих станций.

        Args:
            interval: Интервал мониторинга в секундах
        """
        for workstation in self.workstations:
            if workstation.config.monitoring_enabled:
                task = asyncio.create_task(
                    self._monitor_workstation(workstation, interval)
                )
                self.monitoring_tasks.append(task)

    async def stop_monitoring(self) -> None:
        """Остановить мониторинг всех рабочих станций."""
        for task in self.monitoring_tasks:
            task.cancel()

        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()

    async def _monitor_workstation(self, workstation: WorkstationManager, interval: int) -> None:
        """Мониторить отдельную рабочую станцию.

        Args:
            workstation: Менеджер рабочей станции
            interval: Интервал мониторинга
        """
        while True:
            try:
                # Получить информацию о системе
                system_info = workstation.get_system_info()

                # Получить список эмуляторов
                emulators = workstation.get_emulators_list()

                # Обновить статистику в конфигурации
                workstation.config.total_emulators = len(emulators)
                workstation.config.active_emulators = len([
                    emu for emu in emulators
                    if emu.status == EmulatorStatus.RUNNING
                ])

                # Обновить статус подключения
                if workstation.is_connected:
                    workstation.config.status = WorkstationStatus.ONLINE
                else:
                    workstation.config.status = WorkstationStatus.OFFLINE

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка мониторинга станции {workstation.config.name}: {e}")
                await asyncio.sleep(interval)