"""
Модуль конфигурации системы управления LDPlayer эмуляторами.

Определяет настройки сервера, параметры подключения к рабочим станциям,
пути к файлам и другие системные параметры.

SECURITY PATCH v2.0:
- Все секретные значения загружаются из переменных окружения
- Валидация на startup для обязательных параметров
- Никаких захардкодированных паролей или ключей
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Загруженне переменных окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv не установлен


@dataclass
class ServerConfig:
    """Конфигурация сервера."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    reload: bool = True

    # WebSocket настройки
    websocket_port: int = 8001

    # Логирование
    log_level: str = "INFO"
    log_file: str = "logs/server.log"

    # База данных
    database_url: str = "sqlite:///./ldplayer_manager.db"

    # Безопасность - ЗАГРУЖАЕТСЯ ИЗ .env (никогда не захардкодируй!)
    # Валидация происходит в load_config() - если не установлено, сервер не запустится
    secret_key: str = os.getenv("JWT_SECRET_KEY", "")  # ПУСТО - ошибка если не в .env!
    access_token_expire_minutes: int = 30


@dataclass
class WorkstationConfig:
    """Конфигурация рабочей станции."""
    id: str
    name: str
    ip_address: str
    username: str = "administrator"
    password: str = ""  # ЗАГРУЖАЕТСЯ ИЗ .env - см. load_config()
    domain: str = ""

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
    monitoring_interval: int = 30  # секунды

    # Статус
    status: str = "unknown"
    last_seen: Optional[str] = None
    
    # Эмуляторы (кэшированный список, может быть пустым)
    emulators: List[Dict] = field(default_factory=list)
    
    # Статистика (добавлено для мониторинга)
    total_emulators: int = 0
    active_emulators: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0


@dataclass
class SystemConfig:
    """Основная конфигурация системы."""
    server: ServerConfig = field(default_factory=ServerConfig)
    workstations: List[WorkstationConfig] = field(default_factory=list)

    # Пути к файлам
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    configs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "configs")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")
    backups_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "backups")

    # Настройки резервного копирования
    backup_enabled: bool = True
    backup_interval: int = 3600  # секунды
    max_backups: int = 10

    # Настройки мониторинга
    global_monitoring: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "disk_usage": 90.0
    })


class ConfigManager:
    """Менеджер конфигурации системы."""

    def __init__(self, config_file: str = "config.json"):
        """Инициализация менеджера конфигурации.

        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = Path(__file__).parent.parent.parent / config_file
        self._config: Optional[SystemConfig] = None

    def load_config(self) -> SystemConfig:
        """Загрузить конфигурацию из файла.

        Returns:
            SystemConfig: Объект конфигурации системы
        """
        if self._config is not None:
            return self._config

        # Создать директории если не существуют
        self._ensure_directories()

        # Загрузить конфигурацию из файла или создать по умолчанию
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = self._from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                self._config = self._create_default_config()
        else:
            self._config = self._create_default_config()
            self.save_config()

        return self._config

    def save_config(self) -> None:
        """Сохранить конфигурацию в файл."""
        if self._config is None:
            return

        self._ensure_directories()

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._to_dict(self._config), f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            from ..core.exceptions import FileWriteError
            logger.error(f"Failed to save config: {e}")
            raise FileWriteError(f"Failed to save configuration: {str(e)}", 
                               details={"file": self.config_file, "error": str(e)})
        except (TypeError, ValueError) as e:
            from ..core.exceptions import ConfigException
            logger.error(f"Failed to serialize config: {e}")
            raise ConfigException(f"Configuration serialization failed: {str(e)}")

    def _create_default_config(self) -> SystemConfig:
        """
        Создать конфигурацию по умолчанию.
        
        🔐 SECURITY PATCH v2.0:
        Пароли загружаются из переменных окружения (.env файла).
        Если пароль не установлен - валидация на startup не позволит запустить сервер.
        """
        # Пример конфигурации с тестовыми рабочими станциями
        workstations = [
            WorkstationConfig(
                id="ws_001",
                name="Рабочая станция 1",
                ip_address="192.168.1.101",
                username="administrator",
                password=os.getenv("WS_001_PASSWORD", "")  # Загружаем из .env
            ),
            WorkstationConfig(
                id="ws_002",
                name="Рабочая станция 2",
                ip_address="192.168.1.102",
                username="administrator",
                password=os.getenv("WS_002_PASSWORD", "")  # Загружаем из .env
            )
        ]

        return SystemConfig(
            server=ServerConfig(),
            workstations=workstations
        )

    def _to_dict(self, config: SystemConfig) -> dict:
        """Преобразовать конфигурацию в словарь."""
        return {
            "server": {
                "host": config.server.host,
                "port": config.server.port,
                "debug": config.server.debug,
                "reload": config.server.reload,
                "websocket_port": config.server.websocket_port,
                "log_level": config.server.log_level,
                "log_file": config.server.log_file,
                "database_url": config.server.database_url,
                "secret_key": config.server.secret_key,
                "access_token_expire_minutes": config.server.access_token_expire_minutes
            },
            "workstations": [
                {
                    "id": ws.id,
                    "name": ws.name,
                    "ip_address": ws.ip_address,
                    "username": ws.username,
                    "password": ws.password,
                    "domain": ws.domain,
                    "ldplayer_path": ws.ldplayer_path,
                    "ldconsole_path": ws.ldconsole_path,
                    "configs_path": ws.configs_path,
                    "smb_enabled": ws.smb_enabled,
                    "powershell_remoting_enabled": ws.powershell_remoting_enabled,
                    "winrm_port": ws.winrm_port,
                    "monitoring_enabled": ws.monitoring_enabled,
                    "monitoring_interval": ws.monitoring_interval,
                    "status": ws.status,
                    "last_seen": ws.last_seen
                }
                for ws in config.workstations
            ],
            "system": {
                "base_dir": str(config.base_dir),
                "configs_dir": str(config.configs_dir),
                "logs_dir": str(config.logs_dir),
                "backups_dir": str(config.backups_dir),
                "backup_enabled": config.backup_enabled,
                "backup_interval": config.backup_interval,
                "max_backups": config.max_backups,
                "global_monitoring": config.global_monitoring,
                "alert_thresholds": config.alert_thresholds
            }
        }

    def _from_dict(self, data: dict) -> SystemConfig:
        """Создать конфигурацию из словаря."""
        # Загрузить настройки сервера
        server_data = data.get("server", {})
        server = ServerConfig(**server_data)

        # Загрузить настройки рабочих станций
        workstations_data = data.get("workstations", [])
        workstations = [
            WorkstationConfig(**ws_data) for ws_data in workstations_data
        ]

        # Загрузить системные настройки
        system_data = data.get("system", {})

        return SystemConfig(
            server=server,
            workstations=workstations,
            base_dir=Path(system_data.get("base_dir", "")),
            configs_dir=Path(system_data.get("configs_dir", "")),
            logs_dir=Path(system_data.get("logs_dir", "")),
            backups_dir=Path(system_data.get("backups_dir", "")),
            backup_enabled=system_data.get("backup_enabled", True),
            backup_interval=system_data.get("backup_interval", 3600),
            max_backups=system_data.get("max_backups", 10),
            global_monitoring=system_data.get("global_monitoring", True),
            alert_thresholds=system_data.get("alert_thresholds", {})
        )

    def _ensure_directories(self) -> None:
        """Создать необходимые директории."""
        directories = [
            self._config.base_dir if self._config else Path(__file__).parent.parent.parent,
            Path(__file__).parent.parent.parent / "configs",
            Path(__file__).parent.parent.parent / "logs",
            Path(__file__).parent.parent.parent / "backups"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_workstation(self, workstation_id: str) -> Optional[WorkstationConfig]:
        """Получить конфигурацию рабочей станции по ID.

        Args:
            workstation_id: ID рабочей станции

        Returns:
            WorkstationConfig или None если не найдена
        """
        config = self.load_config()
        for workstation in config.workstations:
            if workstation.id == workstation_id:
                return workstation
        return None

    def add_workstation(self, workstation: WorkstationConfig) -> None:
        """Добавить рабочую станцию в конфигурацию.

        Args:
            workstation: Конфигурация рабочей станции
        """
        config = self.load_config()
        # Проверить, что станция с таким ID не существует
        for existing in config.workstations:
            if existing.id == workstation.id:
                raise ValueError(f"Рабочая станция с ID {workstation.id} уже существует")

        config.workstations.append(workstation)
        self.save_config()

    def remove_workstation(self, workstation_id: str) -> None:
        """Удалить рабочую станцию из конфигурации.

        Args:
            workstation_id: ID рабочей станции для удаления
        """
        config = self.load_config()
        config.workstations = [
            ws for ws in config.workstations
            if ws.id != workstation_id
        ]
        self.save_config()

    def update_workstation(self, workstation: WorkstationConfig) -> None:
        """Обновить конфигурацию рабочей станции.

        Args:
            workstation: Обновленная конфигурация рабочей станции
        """
        config = self.load_config()
        for i, existing in enumerate(config.workstations):
            if existing.id == workstation.id:
                config.workstations[i] = workstation
                break
        self.save_config()


# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()


def validate_security_configuration() -> None:
    """
    🔐 ВАЛИДАЦИЯ БЕЗОПАСНОСТИ НА STARTUP
    
    Проверяет все критические параметры безопасности перед запуском сервера.
    Если валидация не пройдена - сервер НЕ ЗАПУСТИТСЯ!
    
    Raises:
        RuntimeError: Если критический параметр безопасности не установлен
    """
    errors = []
    
    # ✅ Проверка 1: JWT Secret Key должен быть установлен и не быть дефолтным
    jwt_secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if not jwt_secret:
        errors.append(
            "❌ CRITICAL: JWT_SECRET_KEY не установлена в .env файле!\n"
            "   Сгенерируй случайный ключ: python -c \"import secrets; print(secrets.token_urlsafe(32))\"\n"
            "   Добавь в .env: JWT_SECRET_KEY=<твой_ключ>"
        )
    elif jwt_secret == "your-secret-key-change-in-production":
        errors.append(
            "❌ CRITICAL: JWT_SECRET_KEY - это дефолтное значение!\n"
            "   Сгенерируй новый ключ и обнови .env файл."
        )
    elif len(jwt_secret) < 32:
        errors.append(
            f"❌ WARNING: JWT_SECRET_KEY слишком короткий ({len(jwt_secret)} символов)\n"
            "   Рекомендуемая длина: минимум 32 символа."
        )
    
    # ✅ Проверка 2: Пароли рабочих станций
    config = get_config()
    for ws in config.workstations:
        if not ws.password or ws.password.strip() == "":
            errors.append(
                f"❌ CRITICAL: Рабочая станция '{ws.name}' (ID: {ws.id}) не имеет пароля!\n"
                f"   Установи пароль в .env: WS_{ws.id.upper()}_PASSWORD=<пароль>"
            )
        elif len(ws.password) < 8:
            errors.append(
                f"⚠️  WARNING: Пароль рабочей станции '{ws.name}' слишком короткий ({len(ws.password)} символов)\n"
                f"   Рекомендуемая длина: минимум 8 символов."
            )
    
    # ✅ Проверка 3: Database URL не должна быть пустой
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        errors.append(
            "❌ WARNING: DATABASE_URL не установлена в .env файле!\n"
            "   Используется дефолтное значение: sqlite:///./ldplayer_manager.db"
        )
    
    # 🚨 Если есть CRITICAL ошибки - не запускаем сервер
    critical_errors = [e for e in errors if "CRITICAL" in e]
    warnings = [e for e in errors if "WARNING" in e]
    
    if critical_errors:
        print("\n" + "="*80)
        print("🚨 SECURITY VALIDATION FAILED - CRITICAL ERRORS FOUND")
        print("="*80)
        for error in critical_errors:
            print(error)
        print("="*80)
        raise RuntimeError("Security validation failed. Server cannot start.")
    
    # ⚠️ Выводим warning'и если есть
    if warnings:
        print("\n" + "="*80)
        print("⚠️  SECURITY VALIDATION - WARNINGS")
        print("="*80)
        for warning in warnings:
            print(warning)
        print("="*80)
    
    print("✅ Security validation passed!")


def get_config() -> SystemConfig:
    """Получить текущую конфигурацию системы.

    Returns:
        SystemConfig: Текущая конфигурация системы
    """
    return config_manager.load_config()


# Alias для совместимости с API модулями
get_system_config = get_config


def reload_config() -> SystemConfig:
    """Перезагрузить конфигурацию из файла.

    Returns:
        SystemConfig: Обновленная конфигурация системы
    """
    config_manager._config = None
    return config_manager.load_config()