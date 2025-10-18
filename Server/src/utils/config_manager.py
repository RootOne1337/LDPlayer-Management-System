"""
Менеджер конфигурационных файлов эмуляторов.

Предоставляет функции для чтения, записи, валидации и резервного копирования
JSON конфигураций LDPlayer эмуляторов.
"""

import json
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import os
from dataclasses import dataclass, asdict


@dataclass
class EmulatorConfiguration:
    """Конфигурация эмулятора LDPlayer."""

    # Основные параметры
    name: str
    android_version: str = "9.0"
    screen_size: str = "1280x720"
    cpu_cores: int = 2
    memory_mb: int = 2048
    dpi: int = 320
    fps: int = 60

    # Сетевые настройки
    adb_port: int = 5555
    enable_audio: bool = True
    enable_gps: bool = False

    # Производительность
    opengl_mode: str = "angle"  # angle, swiftshader, native
    render_quality: str = "high"  # low, medium, high, ultra

    # Дополнительные настройки
    custom_settings: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Пост-инициализация."""
        if self.custom_settings is None:
            self.custom_settings = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmulatorConfiguration':
        """Создать из словаря."""
        return cls(**data)

    def to_ldplayer_config(self) -> Dict[str, Any]:
        """Преобразовать в формат конфигурации LDPlayer."""
        return {
            "name": self.name,
            "android_version": self.android_version,
            "resolution": self.screen_size,
            "cpu": self.cpu_cores,
            "memory": self.memory_mb,
            "dpi": self.dpi,
            "fps": self.fps,
            "adb_port": self.adb_port,
            "audio": self.enable_audio,
            "gps": self.enable_gps,
            "opengl": self.opengl_mode,
            "quality": self.render_quality,
            **self.custom_settings
        }


class ConfigValidationError(Exception):
    """Ошибка валидации конфигурации."""
    pass


class ConfigManager:
    """Менеджер конфигурационных файлов."""

    def __init__(self, base_path: Path):
        """Инициализация менеджера конфигураций.

        Args:
            base_path: Базовая директория для хранения конфигураций
        """
        self.base_path = Path(base_path)
        self.configs_path = self.base_path / "configs"
        self.backups_path = self.base_path / "backups"
        self.templates_path = self.base_path / "templates"

        # Создать директории если не существуют
        self._ensure_directories()

        # Загрузить схемы валидации
        self.validation_schemas = self._load_validation_schemas()

    def _ensure_directories(self) -> None:
        """Создать необходимые директории."""
        directories = [
            self.configs_path,
            self.backups_path,
            self.templates_path
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Загрузить схемы валидации."""
        schemas = {
            "emulator_config": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "minLength": 1, "maxLength": 100},
                    "android_version": {"type": "string"},
                    "screen_size": {"type": "string", "pattern": r"^\d+x\d+$"},
                    "cpu_cores": {"type": "integer", "minimum": 1, "maximum": 16},
                    "memory_mb": {"type": "integer", "minimum": 512, "maximum": 8192},
                    "dpi": {"type": "integer", "minimum": 120, "maximum": 480},
                    "fps": {"type": "integer", "minimum": 30, "maximum": 120},
                    "adb_port": {"type": "integer", "minimum": 5555, "maximum": 5585},
                    "enable_audio": {"type": "boolean"},
                    "enable_gps": {"type": "boolean"},
                    "opengl_mode": {"type": "string", "enum": ["angle", "swiftshader", "native"]},
                    "render_quality": {"type": "string", "enum": ["low", "medium", "high", "ultra"]}
                }
            }
        }

        return schemas

    def validate_config(self, config: EmulatorConfiguration) -> Tuple[bool, List[str]]:
        """Валидировать конфигурацию эмулятора.

        Args:
            config: Конфигурация для валидации

        Returns:
            Tuple[bool, List[str]]: (валидна, список ошибок)
        """
        errors = []
        schema = self.validation_schemas.get("emulator_config", {})

        # Проверка обязательных полей
        if not config.name or not config.name.strip():
            errors.append("Имя эмулятора обязательно")

        # Проверка формата разрешения экрана
        if config.screen_size:
            if 'x' not in config.screen_size:
                errors.append("Неверный формат разрешения экрана (должно быть ШИРИНАxВЫСОТА)")
            else:
                try:
                    width, height = config.screen_size.split('x')
                    int(width), int(height)  # Проверка что числа
                except ValueError:
                    errors.append("Разрешение экрана должно содержать только числа")

        # Проверка диапазонов
        if not (1 <= config.cpu_cores <= 16):
            errors.append("Количество CPU ядер должно быть от 1 до 16")

        if not (512 <= config.memory_mb <= 8192):
            errors.append("Объем памяти должен быть от 512 до 8192 МБ")

        if not (120 <= config.dpi <= 480):
            errors.append("DPI должен быть от 120 до 480")

        if not (30 <= config.fps <= 120):
            errors.append("FPS должен быть от 30 до 120")

        if not (5555 <= config.adb_port <= 5585):
            errors.append("ADB порт должен быть от 5555 до 5585")

        return len(errors) == 0, errors

    def save_config(self, emulator_id: str, config: EmulatorConfiguration) -> Tuple[bool, str]:
        """Сохранить конфигурацию эмулятора.

        Args:
            emulator_id: ID эмулятора
            config: Конфигурация для сохранения

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Валидация конфигурации
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                return False, f"Ошибка валидации: {'; '.join(errors)}"

            # Создать файл конфигурации
            config_file = self.configs_path / f"{emulator_id}.json"

            config_data = {
                "emulator_id": emulator_id,
                "config": config.to_dict(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0"
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            return True, f"Конфигурация сохранена: {config_file}"

        except Exception as e:
            return False, f"Ошибка сохранения конфигурации: {e}"

    def load_config(self, emulator_id: str) -> Tuple[Optional[EmulatorConfiguration], str]:
        """Загрузить конфигурацию эмулятора.

        Args:
            emulator_id: ID эмулятора

        Returns:
            Tuple[Optional[EmulatorConfiguration], str]: (конфигурация, сообщение)
        """
        try:
            config_file = self.configs_path / f"{emulator_id}.json"

            if not config_file.exists():
                return None, f"Файл конфигурации не найден: {config_file}"

            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            config_data = data.get("config", {})
            config = EmulatorConfiguration.from_dict(config_data)

            return config, "Конфигурация загружена успешно"

        except json.JSONDecodeError as e:
            return None, f"Ошибка чтения JSON: {e}"
        except Exception as e:
            return None, f"Ошибка загрузки конфигурации: {e}"

    def list_configs(self) -> List[Dict[str, Any]]:
        """Получить список всех конфигураций.

        Returns:
            List[Dict[str, Any]]: Список конфигураций с метаданными
        """
        configs = []

        try:
            for config_file in self.configs_path.glob("*.json"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Получить информацию о файле
                    stat = config_file.stat()

                    config_info = {
                        "emulator_id": data.get("emulator_id", config_file.stem),
                        "filename": config_file.name,
                        "size": stat.st_size,
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "version": data.get("version", "1.0"),
                        "config_name": data.get("config", {}).get("name", "Без имени")
                    }

                    configs.append(config_info)

                except Exception as e:
                    print(f"Ошибка чтения файла {config_file}: {e}")

        except Exception as e:
            print(f"Ошибка получения списка конфигураций: {e}")

        return configs

    def delete_config(self, emulator_id: str) -> Tuple[bool, str]:
        """Удалить конфигурацию эмулятора.

        Args:
            emulator_id: ID эмулятора

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            config_file = self.configs_path / f"{emulator_id}.json"

            if not config_file.exists():
                return False, f"Файл конфигурации не найден: {config_file}"

            # Создать резервную копию перед удалением
            backup_file = self._create_backup_file(config_file)
            shutil.move(str(config_file), str(backup_file))

            return True, f"Конфигурация удалена, резервная копия: {backup_file}"

        except Exception as e:
            return False, f"Ошибка удаления конфигурации: {e}"

    def backup_config(self, emulator_id: str, backup_name: str = None) -> Tuple[bool, str]:
        """Создать резервную копию конфигурации.

        Args:
            emulator_id: ID эмулятора
            backup_name: Имя резервной копии (опционально)

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            config_file = self.configs_path / f"{emulator_id}.json"

            if not config_file.exists():
                return False, f"Файл конфигурации не найден: {config_file}"

            # Создать имя резервной копии
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{emulator_id}_backup_{timestamp}.json"

            backup_file = self.backups_path / backup_name

            # Создать резервную копию
            shutil.copy2(config_file, backup_file)

            return True, f"Резервная копия создана: {backup_file}"

        except Exception as e:
            return False, f"Ошибка создания резервной копии: {e}"

    def restore_config(self, emulator_id: str, backup_name: str) -> Tuple[bool, str]:
        """Восстановить конфигурацию из резервной копии.

        Args:
            emulator_id: ID эмулятора
            backup_name: Имя файла резервной копии

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            backup_file = self.backups_path / backup_name

            if not backup_file.exists():
                return False, f"Файл резервной копии не найден: {backup_file}"

            config_file = self.configs_path / f"{emulator_id}.json"

            # Создать резервную копию текущей конфигурации
            if config_file.exists():
                current_backup = self.backups_path / f"{emulator_id}_before_restore_{int(time.time())}.json"
                shutil.copy2(config_file, current_backup)

            # Восстановить из резервной копии
            shutil.copy2(backup_file, config_file)

            return True, f"Конфигурация восстановлена из: {backup_file}"

        except Exception as e:
            return False, f"Ошибка восстановления конфигурации: {e}"

    def _create_backup_file(self, original_file: Path) -> Path:
        """Создать файл резервной копии.

        Args:
            original_file: Исходный файл

        Returns:
            Path: Путь к файлу резервной копии
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{original_file.stem}_deleted_{timestamp}{original_file.suffix}"
        return self.backups_path / backup_name

    def export_configs(self, export_path: str, emulator_ids: List[str] = None) -> Tuple[bool, str]:
        """Экспортировать конфигурации в ZIP архив.

        Args:
            export_path: Путь для сохранения архива
            emulator_ids: Список ID эмуляторов для экспорта (если None - все)

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Создать ZIP архив
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Добавить конфигурации
                if emulator_ids is None:
                    config_files = self.configs_path.glob("*.json")
                else:
                    config_files = [
                        self.configs_path / f"{emulator_id}.json"
                        for emulator_id in emulator_ids
                    ]

                for config_file in config_files:
                    if config_file.exists():
                        zipf.write(config_file, config_file.name)

                # Добавить метаданные
                metadata = {
                    "export_date": datetime.now().isoformat(),
                    "total_configs": len(list(config_files)),
                    "emulator_ids": emulator_ids or "all"
                }

                zipf.writestr("metadata.json", json.dumps(metadata, indent=2))

            return True, f"Конфигурации экспортированы: {export_path}"

        except Exception as e:
            return False, f"Ошибка экспорта конфигураций: {e}"

    def import_configs(self, archive_path: str, overwrite: bool = False) -> Tuple[bool, str]:
        """Импортировать конфигурации из ZIP архива.

        Args:
            archive_path: Путь к архиву
            overwrite: Перезаписывать существующие конфигурации

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            imported_count = 0

            with zipfile.ZipFile(archive_path, 'r') as zipf:
                # Проверить метаданные
                if "metadata.json" in zipf.namelist():
                    with zipf.open("metadata.json") as f:
                        metadata = json.load(f)
                    print(f"Импорт архива от {metadata.get('export_date', 'неизвестно')}")

                # Импортировать конфигурации
                for file_info in zipf.filelist:
                    if file_info.filename.endswith('.json') and file_info.filename != "metadata.json":
                        with zipf.open(file_info) as f:
                            data = json.load(f)

                        emulator_id = data.get("emulator_id")
                        if emulator_id:
                            config_file = self.configs_path / f"{emulator_id}.json"

                            # Проверить перезапись
                            if config_file.exists() and not overwrite:
                                print(f"Пропуск {emulator_id} (файл существует)")
                                continue

                            with open(config_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)

                            imported_count += 1

            return True, f"Импортировано конфигураций: {imported_count}"

        except Exception as e:
            return False, f"Ошибка импорта конфигураций: {e}"

    def create_template(self, template_name: str, config: EmulatorConfiguration) -> Tuple[bool, str]:
        """Создать шаблон конфигурации.

        Args:
            template_name: Имя шаблона
            config: Конфигурация для шаблона

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Валидация конфигурации
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                return False, f"Ошибка валидации шаблона: {'; '.join(errors)}"

            template_file = self.templates_path / f"{template_name}.json"

            template_data = {
                "template_name": template_name,
                "config": config.to_dict(),
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }

            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            return True, f"Шаблон '{template_name}' создан: {template_file}"

        except Exception as e:
            return False, f"Ошибка создания шаблона: {e}"

    def get_templates(self) -> List[Dict[str, Any]]:
        """Получить список шаблонов конфигураций.

        Returns:
            List[Dict[str, Any]]: Список шаблонов
        """
        templates = []

        try:
            for template_file in self.templates_path.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    templates.append({
                        "name": data.get("template_name", template_file.stem),
                        "filename": template_file.name,
                        "created_at": data.get("created_at"),
                        "version": data.get("version", "1.0"),
                        "config_name": data.get("config", {}).get("name", "Без имени")
                    })

                except Exception as e:
                    print(f"Ошибка чтения шаблона {template_file}: {e}")

        except Exception as e:
            print(f"Ошибка получения списка шаблонов: {e}")

        return templates

    def apply_template(self, template_name: str, emulator_id: str) -> Tuple[bool, str]:
        """Применить шаблон к эмулятору.

        Args:
            template_name: Имя шаблона
            emulator_id: ID эмулятора

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            template_file = self.templates_path / f"{template_name}.json"

            if not template_file.exists():
                return False, f"Шаблон '{template_name}' не найден"

            # Загрузить шаблон
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            config_data = data.get("config", {})
            config = EmulatorConfiguration.from_dict(config_data)

            # Обновить имя в конфигурации
            config.name = emulator_id

            # Сохранить конфигурацию
            return self.save_config(emulator_id, config)

        except Exception as e:
            return False, f"Ошибка применения шаблона: {e}"

    def cleanup_backups(self, max_age_days: int = 30) -> Tuple[int, str]:
        """Очистить старые резервные копии.

        Args:
            max_age_days: Максимальный возраст файлов в днях

        Returns:
            Tuple[int, str]: (количество удаленных файлов, сообщение)
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0

            for backup_file in self.backups_path.glob("*.json"):
                try:
                    # Проверить дату изменения файла
                    file_modified = datetime.fromtimestamp(backup_file.stat().st_mtime)

                    if file_modified < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1

                except Exception as e:
                    print(f"Ошибка удаления файла {backup_file}: {e}")

            return deleted_count, f"Удалено старых резервных копий: {deleted_count}"

        except Exception as e:
            return 0, f"Ошибка очистки резервных копий: {e}"

    def get_config_stats(self) -> Dict[str, Any]:
        """Получить статистику конфигураций.

        Returns:
            Dict[str, Any]: Статистика конфигураций
        """
        try:
            configs = self.list_configs()
            templates = self.get_templates()

            total_size = sum(config["size"] for config in configs)

            stats = {
                "total_configs": len(configs),
                "total_templates": len(templates),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "configs_by_version": {},
                "oldest_config": None,
                "newest_config": None
            }

            # Группировка по версиям
            for config in configs:
                version = config.get("version", "1.0")
                stats["configs_by_version"][version] = stats["configs_by_version"].get(version, 0) + 1

            # Поиск самых старых и новых конфигураций
            sorted_configs = sorted(configs, key=lambda x: x.get("created_at", ""))
            if sorted_configs:
                stats["oldest_config"] = sorted_configs[0]
                stats["newest_config"] = sorted_configs[-1]

            return stats

        except Exception as e:
            return {"error": f"Ошибка получения статистики: {e}"}


# Глобальный экземпляр менеджера конфигураций
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Получить глобальный экземпляр менеджера конфигураций.

    Returns:
        ConfigManager: Менеджер конфигураций
    """
    global _config_manager

    if _config_manager is None:
        from ..core.config import get_config
        config = get_config()
        _config_manager = ConfigManager(config.configs_dir)

    return _config_manager


def reset_config_manager():
    """Сбросить глобальный экземпляр менеджера конфигураций."""
    global _config_manager
    _config_manager = None