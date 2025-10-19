"""
LDPlayer Emulator Scanner - сканирование эмуляторов локально и удалённо.

Поддерживает:
- Локальное сканирование (127.0.0.1, localhost)
- Удалённое сканирование через WinRM
- Парсинг вывода ldconsole.exe list2
- Анализ конфигурационных файлов
"""

import os
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EmulatorStatus(str, Enum):
    """Статусы эмулятора."""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class EmulatorInfo:
    """Информация об эмуляторе."""
    name: str
    id: Optional[str] = None
    status: EmulatorStatus = EmulatorStatus.UNKNOWN
    pid: Optional[int] = None
    port: Optional[int] = None
    memory_mb: Optional[int] = None
    cpu_cores: Optional[int] = None
    resolution: Optional[str] = None
    android_version: Optional[str] = None
    config_path: Optional[str] = None
    adb_port: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            "name": self.name,
            "id": self.id,
            "status": self.status.value,
            "pid": self.pid,
            "port": self.port,
            "memory_mb": self.memory_mb,
            "cpu_cores": self.cpu_cores,
            "resolution": self.resolution,
            "android_version": self.android_version,
            "config_path": self.config_path,
            "adb_port": self.adb_port
        }


class LocalLDPlayerScanner:
    """Сканер эмуляторов на локальной машине."""
    
    LDPLAYER_PATHS = [
        r"C:\LDPlayer\LDPlayer9",
        r"C:\LDPlayer\LDPlayer9.0",
        r"C:\LDPlayer\LDPlayer4",
        r"D:\LDPlayer\LDPlayer9",
        r"C:\Program Files\LDPlayer",
    ]
    
    def __init__(self, ldplayer_path: Optional[str] = None):
        """Инициализировать сканер.
        
        Args:
            ldplayer_path: Путь к LDPlayer (автоопределение если None)
        """
        self.ldplayer_path = ldplayer_path
        self._find_ldplayer_path()
        self.ldconsole_path = self._find_ldconsole()
    
    def _find_ldplayer_path(self) -> None:
        """Найти путь к LDPlayer."""
        if self.ldplayer_path and Path(self.ldplayer_path).exists():
            return
        
        for path in self.LDPLAYER_PATHS:
            if Path(path).exists():
                self.ldplayer_path = path
                logger.info(f"Found LDPlayer at: {path}")
                return
        
        logger.warning("LDPlayer not found in standard locations")
    
    def _find_ldconsole(self) -> Optional[str]:
        """Найти ldconsole.exe."""
        if not self.ldplayer_path:
            return None
        
        # Проверить разные имена в разных версиях
        for name in ["ldconsole.exe", "dnconsole.exe"]:
            path = Path(self.ldplayer_path) / name
            if path.exists():
                logger.info(f"Found LDConsole at: {path}")
                return str(path)
        
        return None
    
    def scan(self) -> List[EmulatorInfo]:
        """Сканировать эмуляторы.
        
        Returns:
            Список эмуляторов
        """
        if not self.ldconsole_path:
            logger.error("LDConsole not found")
            return []
        
        emulators = []
        
        # 1. Получить список через ldconsole list2
        emulators = self._parse_ldconsole_list2()
        
        # 2. Дополнить информацией из конфигов
        self._enhance_with_configs(emulators)
        
        # 3. Проверить статусы запущенных
        self._check_running_status(emulators)
        
        return emulators
    
    def _parse_ldconsole_list2(self) -> List[EmulatorInfo]:
        """Парсить вывод ldconsole list2.
        
        Формат:
        Name,Pid,Status,TopWindowHandle
        leidian0,1234,Running,0x12345678
        leidian1,0,Stop,0
        """
        if not self.ldconsole_path:
            return []
        
        try:
            result = subprocess.run(
                [self.ldconsole_path, "list2"],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            emulators = []
            lines = result.stdout.strip().split('\n')
            
            # Пропустить заголовок
            if not lines or "Name" in lines[0]:
                lines = lines[1:]
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 2:
                    continue
                
                emu = EmulatorInfo(
                    name=parts[0],
                    id=parts[0],
                    pid=int(parts[1]) if parts[1].isdigit() else None,
                    status=self._parse_status(parts[2] if len(parts) > 2 else "")
                )
                emulators.append(emu)
                logger.debug(f"Found emulator: {emu.name} (PID: {emu.pid})")
            
            return emulators
        
        except subprocess.TimeoutExpired:
            logger.error("ldconsole list2 timed out")
            return []
        except Exception as e:
            logger.error(f"Error parsing ldconsole output: {e}")
            return []
    
    def _parse_status(self, status_str: str) -> EmulatorStatus:
        """Парсить статус эмулятора."""
        status_lower = status_str.lower()
        if "run" in status_lower:
            return EmulatorStatus.RUNNING
        elif "stop" in status_lower:
            return EmulatorStatus.STOPPED
        else:
            return EmulatorStatus.UNKNOWN
    
    def _enhance_with_configs(self, emulators: List[EmulatorInfo]) -> None:
        """Дополнить информацию из конфигурационных файлов."""
        if not self.ldplayer_path:
            return
        
        config_dirs = [
            Path(self.ldplayer_path) / "vms" / "config",
            Path(self.ldplayer_path) / "vms" / "leidian",
        ]
        
        for config_dir in config_dirs:
            if not config_dir.exists():
                continue
            
            for emu in emulators:
                config_file = config_dir / f"{emu.name}.config"
                if not config_file.exists():
                    continue
                
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if '=' not in line or line.startswith('#'):
                                continue
                            
                            key, value = line.split('=', 1)
                            key = key.strip().lower()
                            value = value.strip().strip('"')
                            
                            # Парсить значения
                            if 'memory' in key and 'phone' in key:
                                try:
                                    emu.memory_mb = int(value)
                                except:
                                    pass
                            elif 'cpucore' in key:
                                try:
                                    emu.cpu_cores = int(value)
                                except:
                                    pass
                            elif 'width' in key:
                                try:
                                    width = int(value)
                                    if emu.resolution:
                                        height = emu.resolution.split('x')[1]
                                        emu.resolution = f"{width}x{height}"
                                    else:
                                        emu.resolution = f"{width}x?"
                                except:
                                    pass
                            elif 'height' in key:
                                try:
                                    height = int(value)
                                    if emu.resolution:
                                        width = emu.resolution.split('x')[0]
                                        emu.resolution = f"{width}x{height}"
                                    else:
                                        emu.resolution = f"?x{height}"
                                except:
                                    pass
                    
                    emu.config_path = str(config_file)
                except Exception as e:
                    logger.warning(f"Error reading config for {emu.name}: {e}")
        
    def _check_running_status(self, emulators: List[EmulatorInfo]) -> None:
        """Проверить статус запущенных эмуляторов через ldconsole isrunning."""
        if not self.ldconsole_path:
            return
        
        for emu in emulators:
            if emu.status != EmulatorStatus.UNKNOWN:
                continue
            
            try:
                result = subprocess.run(
                    [self.ldconsole_path, "isrunning", emu.name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if "1" in result.stdout:
                    emu.status = EmulatorStatus.RUNNING
                else:
                    emu.status = EmulatorStatus.STOPPED
            
            except Exception as e:
                logger.warning(f"Error checking status for {emu.name}: {e}")
                emu.status = EmulatorStatus.UNKNOWN


class RemoteLDPlayerScanner:
    """Сканер эмуляторов на удалённой машине через WinRM."""
    
    def __init__(
        self,
        host: str,
        username: str = "Administrator",
        password: str = "",
        ldplayer_path: str = r"C:\LDPlayer\LDPlayer9"
    ):
        """Инициализировать удалённый сканер.
        
        Args:
            host: IP адрес или имя хоста
            username: Имя пользователя для WinRM
            password: Пароль
            ldplayer_path: Путь к LDPlayer на удалённой машине
        """
        self.host = host
        self.username = username
        self.password = password
        self.ldplayer_path = ldplayer_path
        self._session = None
    
    def _create_session(self):
        """Создать WinRM сессию."""
        try:
            import winrm
            self._session = winrm.Session(
                self.host,
                auth=(self.username, self.password),
                transport='ntlm'
            )
            logger.info(f"Created WinRM session to {self.host}")
            return True
        except Exception as e:
            logger.error(f"Failed to create WinRM session: {e}")
            return False
    
    def scan(self) -> List[EmulatorInfo]:
        """Сканировать эмуляторы на удалённой машине.
        
        Returns:
            Список эмуляторов
        """
        if not self._create_session():
            return []
        
        try:
            # Выполнить PowerShell команду для получения списка
            script = f"""
            $emulators = @()
            $ldconsole = '{self.ldplayer_path}\\ldconsole.exe'
            
            if (Test-Path $ldconsole) {{
                $output = & $ldconsole list2 2>$null
                foreach ($line in $output | Select-Object -Skip 1) {{
                    if ($line.Trim()) {{
                        $parts = $line -split ','
                        $emulators += @{{
                            name = $parts[0].Trim()
                            pid = [int]::TryParse($parts[1].Trim(), [ref]0)
                            status = if ($parts[2] -like '*run*') {{ 'Running' }} else {{ 'Stopped' }}
                        }}
                    }}
                }}
            }}
            
            $emulators | ConvertTo-Json
            """
            
            response = self._session.run_ps(script)
            
            if response.status_code != 0:
                logger.error(f"Remote script error: {response.std_err}")
                return []
            
            data = json.loads(response.std_out)
            if not isinstance(data, list):
                data = [data]
            
            emulators = []
            for item in data:
                emu = EmulatorInfo(
                    name=item.get("name", ""),
                    status=EmulatorStatus.RUNNING if item.get("status") == "Running" else EmulatorStatus.STOPPED
                )
                emulators.append(emu)
            
            return emulators
        
        except Exception as e:
            logger.error(f"Error scanning remote emulators: {e}")
            return []


class EmulatorScanner:
    """Универсальный сканер эмуляторов (локальный или удалённый)."""
    
    @staticmethod
    def create(
        host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ldplayer_path: Optional[str] = None
    ) -> "LocalLDPlayerScanner | RemoteLDPlayerScanner":
        """Создать сканер в зависимости от хоста.
        
        Args:
            host: IP адрес или имя хоста
            username: Имя пользователя (для удалённого доступа)
            password: Пароль (для удалённого доступа)
            ldplayer_path: Путь к LDPlayer
        
        Returns:
            Локальный или удалённый сканер
        """
        if host in ["127.0.0.1", "localhost", "0.0.0.0"]:
            return LocalLDPlayerScanner(ldplayer_path)
        else:
            return RemoteLDPlayerScanner(
                host=host,
                username=username or "Administrator",
                password=password or "",
                ldplayer_path=ldplayer_path or r"C:\LDPlayer\LDPlayer9"
            )
