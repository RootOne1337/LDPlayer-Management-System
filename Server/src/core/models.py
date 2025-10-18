"""
Модели данных для системы управления LDPlayer эмуляторами.

Определяет структуры данных для эмуляторов, рабочих станций,
операций и других сущностей системы.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from ..utils.logger import get_logger, LogCategory
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, ConfigDict


class EmulatorStatus(str, Enum):
    """Статус эмулятора."""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class WorkstationStatus(str, Enum):
    """Статус рабочей станции."""
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ERROR = "error"
    UNKNOWN = "unknown"


class OperationType(str, Enum):
    """Тип операции с эмулятором."""
    CREATE = "create"
    DELETE = "delete"
    RENAME = "rename"
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    CLONE = "clone"
    MODIFY = "modify"


class OperationStatus(str, Enum):
    """Статус операции."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class EmulatorConfig:
    """Конфигурация эмулятора LDPlayer."""
    android_version: str = "9.0"
    screen_size: str = "1280x720"
    cpu_cores: int = 2
    memory_mb: int = 2048
    dpi: int = 320
    fps: int = 60

    # Дополнительные настройки
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def to_ldconsole_params(self) -> List[str]:
        """Преобразовать конфигурацию в параметры для ldconsole.exe.

        Returns:
            List[str]: Список параметров командной строки
        """
        params = []

        # ✅ FIXED: Добавить разрешение если указано (с валидацией формата)
        if self.screen_size:
            try:
                width, height = self.screen_size.split('x')
                # Проверяем что это числа
                int(width)
                int(height)
                params.extend(['--resolution', f'{width},{height},{self.dpi}'])
            except (ValueError, IndexError) as e:
                logger = get_logger(LogCategory.CORE)
                logger.error(f"Invalid screen_size format '{self.screen_size}': {e}")
                # Пропускаем некорректное разрешение

        # Добавить память если указана
        if self.memory_mb:
            params.extend(['--memory', str(self.memory_mb)])

        # Добавить CPU если указано
        if self.cpu_cores:
            params.extend(['--cpu', str(self.cpu_cores)])

        return params


class Emulator:
    """Модель эмулятора LDPlayer."""

    def __init__(
        self,
        id: str,
        name: str,
        workstation_id: str,
        status: EmulatorStatus = EmulatorStatus.CREATED,
        config: Optional[EmulatorConfig] = None,
        **kwargs
    ):
        """Инициализация эмулятора.

        Args:
            id: Уникальный идентификатор эмулятора
            name: Имя эмулятора
            workstation_id: ID рабочей станции
            status: Статус эмулятора
            config: Конфигурация эмулятора
            **kwargs: Дополнительные параметры
        """
        self.id = id
        self.name = name
        self.workstation_id = workstation_id
        self.status = status
        self.config = config or EmulatorConfig()

        # Дополнительные поля
        self.created_date = kwargs.get('created_date', datetime.now())
        self.last_activity = kwargs.get('last_activity', datetime.now())
        self.uptime = kwargs.get('uptime', 0)
        self.adb_port = kwargs.get('adb_port', 5555)
        self.config_path = kwargs.get('config_path', '')

        # Статистика
        self.start_count = kwargs.get('start_count', 0)
        self.error_count = kwargs.get('error_count', 0)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать эмулятор в словарь.

        Returns:
            Dict[str, Any]: Словарь с данными эмулятора
        """
        return {
            'id': self.id,
            'name': self.name,
            'workstation_id': self.workstation_id,
            'status': self.status.value,
            'config': {
                'android_version': self.config.android_version,
                'screen_size': self.config.screen_size,
                'cpu_cores': self.config.cpu_cores,
                'memory_mb': self.config.memory_mb,
                'dpi': self.config.dpi,
                'fps': self.config.fps,
                'custom_settings': self.config.custom_settings
            },
            'created_date': self.created_date.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'uptime': self.uptime,
            'adb_port': self.adb_port,
            'config_path': self.config_path,
            'start_count': self.start_count,
            'error_count': self.error_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Emulator':
        """Создать эмулятор из словаря.

        Args:
            data: Словарь с данными эмулятора

        Returns:
            Emulator: Объект эмулятора
        """
        # Создать конфигурацию
        config_data = data.get('config', {})
        config = EmulatorConfig(
            android_version=config_data.get('android_version', '9.0'),
            screen_size=config_data.get('screen_size', '1280x720'),
            cpu_cores=config_data.get('cpu_cores', 2),
            memory_mb=config_data.get('memory_mb', 2048),
            dpi=config_data.get('dpi', 320),
            fps=config_data.get('fps', 60),
            custom_settings=config_data.get('custom_settings', {})
        )

        return cls(
            id=data['id'],
            name=data['name'],
            workstation_id=data['workstation_id'],
            status=EmulatorStatus(data.get('status', 'created')),
            config=config,
            # ✅ FIXED: Безопасный парсинг дат с fallback на текущее время
            created_date=cls._parse_datetime(data.get('created_date')),
            last_activity=cls._parse_datetime(data.get('last_activity')),
            uptime=data.get('uptime', 0),
            adb_port=data.get('adb_port', 5555),
            config_path=data.get('config_path', ''),
            start_count=data.get('start_count', 0),
            error_count=data.get('error_count', 0)
        )
    
    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> datetime:
        """Безопасно распарсить строку в datetime.
        
        Args:
            date_str: ISO format date string или None
            
        Returns:
            datetime: Распарсенная дата или текущее время при ошибке
        """
        if not date_str:
            return datetime.now()
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError) as e:
            logger = get_logger(LogCategory.CORE)
            logger.warning(f"Failed to parse datetime '{date_str}': {e}, using current time")
            return datetime.now()

    def update_status(self, new_status: EmulatorStatus) -> None:
        """Обновить статус эмулятора.

        Args:
            new_status: Новый статус эмулятора
        """
        old_status = self.status
        self.status = new_status
        self.last_activity = datetime.now()

        # Обновить статистику
        if new_status == EmulatorStatus.RUNNING and old_status != EmulatorStatus.RUNNING:
            self.start_count += 1
        elif new_status == EmulatorStatus.ERROR:
            self.error_count += 1


@dataclass
class Workstation:
    """Модель рабочей станции."""

    id: str
    name: str
    ip_address: str
    username: str = "administrator"
    password: str = ""

    # LDPlayer настройки
    ldplayer_path: str = r"C:\LDPlayer\LDPlayer9.0"
    ldconsole_path: str = r"C:\LDPlayer\LDPlayer9.0\ldconsole.exe"
    configs_path: str = r"C:\LDPlayer\LDPlayer9.0\customizeConfigs"

    # Сетевые настройки
    smb_enabled: bool = True
    powershell_remoting_enabled: bool = True
    winrm_port: int = 5985

    # Мониторинг
    monitoring_enabled: bool = True
    monitoring_interval: int = 30

    # Статус
    status: WorkstationStatus = WorkstationStatus.UNKNOWN
    last_seen: Optional[datetime] = None

    # Статистика
    total_emulators: int = 0
    active_emulators: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать рабочую станцию в словарь."""
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'username': self.username,
            'password': self.password,
            'ldplayer_path': self.ldplayer_path,
            'ldconsole_path': self.ldconsole_path,
            'configs_path': self.configs_path,
            'smb_enabled': self.smb_enabled,
            'powershell_remoting_enabled': self.powershell_remoting_enabled,
            'winrm_port': self.winrm_port,
            'monitoring_enabled': self.monitoring_enabled,
            'monitoring_interval': self.monitoring_interval,
            'status': self.status.value,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'total_emulators': self.total_emulators,
            'active_emulators': self.active_emulators,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage
        }

    def update_status(self, new_status: WorkstationStatus) -> None:
        """Обновить статус рабочей станции."""
        self.status = new_status
        self.last_seen = datetime.now()


@dataclass
class Operation:
    """Операция с эмулятором."""

    id: str
    type: OperationType
    emulator_id: str
    workstation_id: str
    status: OperationStatus = OperationStatus.PENDING

    # Параметры операции
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Временные метки
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Результат
    result: Optional[str] = None
    error_message: Optional[str] = None

    def start(self) -> None:
        """Начать выполнение операции."""
        self.status = OperationStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, success: bool = True, result: str = None, error: str = None) -> None:
        """Завершить операцию.

        Args:
            success: Успешность выполнения
            result: Результат выполнения
            error: Сообщение об ошибке
        """
        self.status = OperationStatus.COMPLETED if success else OperationStatus.FAILED
        self.completed_at = datetime.now()
        self.result = result
        self.error_message = error

    def cancel(self) -> None:
        """Отменить операцию."""
        self.status = OperationStatus.CANCELLED
        self.completed_at = datetime.now()


# Pydantic модели для API

class EmulatorCreate(BaseModel):
    """Модель для создания эмулятора."""
    name: str = Field(..., min_length=1, max_length=100)
    workstation_id: str = Field(..., min_length=1)
    config: Optional[EmulatorConfig] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Test Emulator",
                "workstation_id": "ws_001",
                "config": {
                    "android_version": "9.0",
                    "screen_size": "1280x720",
                    "cpu_cores": 2,
                    "memory_mb": 2048
                }
            }
        }
    )


class EmulatorUpdate(BaseModel):
    """Модель для обновления эмулятора."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[EmulatorConfig] = None


class EmulatorResponse(BaseModel):
    """Модель ответа с информацией об эмуляторе."""
    id: str
    name: str
    workstation_id: str
    status: str
    config: Dict[str, Any]
    created_date: str
    last_activity: str
    uptime: int
    adb_port: int
    start_count: int
    error_count: int


class WorkstationCreate(BaseModel):
    """Модель для создания рабочей станции."""
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: str = Field(..., pattern=r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    username: str = "administrator"
    password: str = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Рабочая станция 1",
                "ip_address": "192.168.1.101",
                "username": "administrator",
                "password": "password123"
            }
        }
    )


class WorkstationResponse(BaseModel):
    """Модель ответа с информацией о рабочей станции."""
    id: str
    name: str
    ip_address: str
    status: str
    total_emulators: int
    active_emulators: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    last_seen: Optional[str]


class OperationResponse(BaseModel):
    """Модель ответа с информацией об операции."""
    id: str
    type: str
    emulator_id: str
    workstation_id: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[str]
    error_message: Optional[str]


# Исключения

class EmulatorNotFoundError(Exception):
    """Исключение для случая, когда эмулятор не найден."""
    pass


class WorkstationNotFoundError(Exception):
    """Исключение для случая, когда рабочая станция не найдена."""
    pass


class OperationFailedError(Exception):
    """Исключение для случая неудачного выполнения операции."""
    pass


class WorkstationConnectionError(Exception):
    """Исключение для проблем с подключением к рабочей станции."""
    pass


# ============================================================================
# AUTHENTICATION & AUTHORIZATION MODELS
# ============================================================================

class UserRole(str, Enum):
    """Роли пользователей в системе."""
    ADMIN = "admin"        # Полный доступ ко всем функциям
    OPERATOR = "operator"  # Управление эмуляторами, чтение станций
    VIEWER = "viewer"      # Только просмотр


class User(BaseModel):
    """Модель пользователя."""
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: Optional[str] = Field(None, description="Email пользователя")
    full_name: Optional[str] = Field(None, description="Полное имя")
    role: UserRole = Field(default=UserRole.VIEWER, description="Роль пользователя")
    disabled: bool = Field(default=False, description="Аккаунт отключён")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")
    last_login: Optional[datetime] = Field(None, description="Последний вход")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "System Administrator",
                "role": "admin",
                "disabled": False
            }
        }
    )


class UserInDB(User):
    """Модель пользователя в БД с хэшем пароля."""
    hashed_password: str = Field(..., description="Хэш пароля")


class UserCreate(BaseModel):
    """Модель для создания пользователя."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, description="Пароль (мин. 6 символов)")
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    """Модель для входа пользователя."""
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")


class Token(BaseModel):
    """Модель JWT токена."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    refresh_token: Optional[str] = Field(None, description="Refresh token")


class TokenData(BaseModel):
    """Данные внутри JWT токена."""
    username: Optional[str] = None
    role: Optional[UserRole] = None
    exp: Optional[int] = None  # Expiration timestamp


class TokenRefresh(BaseModel):
    """Модель для обновления токена."""
    refresh_token: str = Field(..., description="Refresh token")

