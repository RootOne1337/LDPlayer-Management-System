"""
Система резервного копирования конфигураций эмуляторов.

Предоставляет функции для создания, восстановления и управления
резервными копиями конфигураций LDPlayer.
"""

import json
import shutil
import zipfile
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import os


class BackupManager:
    """Менеджер резервного копирования."""

    def __init__(self, base_path: Path, max_backups: int = 10):
        """Инициализация менеджера резервного копирования.

        Args:
            base_path: Базовая директория для резервных копий
            max_backups: Максимальное количество резервных копий
        """
        self.base_path = Path(base_path)
        self.backups_path = self.base_path / "backups"
        self.max_backups = max_backups

        # Создать директории если не существуют
        self.backups_path.mkdir(parents=True, exist_ok=True)

        # Планировщик задач
        self.scheduler = schedule.Scheduler()
        self.scheduler_thread: Optional[threading.Thread] = None
        self._running = False

    def create_backup(self, source_path: Path, backup_name: str = None) -> Tuple[bool, str]:
        """Создать резервную копию конфигураций.

        Args:
            source_path: Путь к исходным конфигурациям
            backup_name: Имя резервной копии (опционально)

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Создать имя резервной копии
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"

            backup_path = self.backups_path / backup_name

            # Создать директорию для резервной копии
            backup_path.mkdir(parents=True, exist_ok=True)

            # Копировать конфигурации
            source_configs = Path(source_path) / "configs"
            if source_configs.exists():
                for config_file in source_configs.glob("*.json"):
                    shutil.copy2(config_file, backup_path / config_file.name)

            # Создать метаданные резервной копии
            metadata = {
                "backup_name": backup_name,
                "created_at": datetime.now().isoformat(),
                "source_path": str(source_path),
                "total_files": len(list(backup_path.glob("*.json"))),
                "version": "1.0"
            }

            metadata_file = backup_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # Очистить старые резервные копии
            self._cleanup_old_backups()

            return True, f"Резервная копия создана: {backup_path}"

        except Exception as e:
            return False, f"Ошибка создания резервной копии: {e}"

    def restore_backup(self, backup_name: str, target_path: Path) -> Tuple[bool, str]:
        """Восстановить конфигурации из резервной копии.

        Args:
            backup_name: Имя резервной копии
            target_path: Путь для восстановления

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            backup_path = self.backups_path / backup_name

            if not backup_path.exists():
                return False, f"Резервная копия не найдена: {backup_path}"

            # Проверить метаданные
            metadata_file = backup_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"Восстановление из резервной копии от {metadata.get('created_at', 'неизвестно')}")

            # Создать целевую директорию
            target_configs = target_path / "configs"
            target_configs.mkdir(parents=True, exist_ok=True)

            # Создать резервную копию текущих конфигураций
            current_backup = self.backups_path / f"before_restore_{int(time.time())}"
            if target_configs.exists():
                shutil.copytree(target_configs, current_backup)

            # Восстановить файлы
            restored_count = 0
            for backup_file in backup_path.glob("*.json"):
                if backup_file.name != "metadata.json":
                    shutil.copy2(backup_file, target_configs / backup_file.name)
                    restored_count += 1

            return True, f"Восстановлено файлов: {restored_count}"

        except Exception as e:
            return False, f"Ошибка восстановления резервной копии: {e}"

    def list_backups(self) -> List[Dict[str, Any]]:
        """Получить список резервных копий.

        Returns:
            List[Dict[str, Any]]: Список резервных копий с метаданными
        """
        backups = []

        try:
            for backup_dir in self.backups_path.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / "metadata.json"

                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)

                            # Получить статистику файлов
                            json_files = list(backup_dir.glob("*.json"))
                            total_files = len([f for f in json_files if f.name != "metadata.json"])

                            backup_info = {
                                "name": backup_dir.name,
                                "path": str(backup_dir),
                                "created_at": metadata.get("created_at"),
                                "total_files": total_files,
                                "size_mb": self._get_directory_size(backup_dir),
                                "source_path": metadata.get("source_path")
                            }

                            backups.append(backup_info)

                        except Exception as e:
                            print(f"Ошибка чтения метаданных {metadata_file}: {e}")

        except Exception as e:
            print(f"Ошибка получения списка резервных копий: {e}")

        # Сортировка по дате создания (новые первыми)
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return backups

    def delete_backup(self, backup_name: str) -> Tuple[bool, str]:
        """Удалить резервную копию.

        Args:
            backup_name: Имя резервной копии

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            backup_path = self.backups_path / backup_name

            if not backup_path.exists():
                return False, f"Резервная копия не найдена: {backup_path}"

            # Удалить директорию
            shutil.rmtree(backup_path)

            return True, f"Резервная копия удалена: {backup_name}"

        except Exception as e:
            return False, f"Ошибка удаления резервной копии: {e}"

    def _cleanup_old_backups(self) -> None:
        """Очистить старые резервные копии."""
        try:
            backups = self.list_backups()

            # Удалить лишние резервные копии
            if len(backups) > self.max_backups:
                backups_to_delete = backups[self.max_backups:]

                for backup in backups_to_delete:
                    try:
                        shutil.rmtree(Path(backup["path"]))
                    except Exception as e:
                        print(f"Ошибка удаления старой резервной копии {backup['name']}: {e}")

        except Exception as e:
            print(f"Ошибка очистки старых резервных копий: {e}")

    def _get_directory_size(self, directory: Path) -> float:
        """Получить размер директории в МБ.

        Args:
            directory: Путь к директории

        Returns:
            float: Размер в МБ
        """
        try:
            total_size = 0
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size

            return round(total_size / (1024 * 1024), 2)

        except Exception:
            return 0.0

    def start_auto_backup(self, source_path: Path, interval_hours: int = 24):
        """Запустить автоматическое резервное копирование.

        Args:
            source_path: Путь к исходным конфигурациям
            interval_hours: Интервал в часах
        """
        def backup_job():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"auto_backup_{timestamp}"
            success, message = self.create_backup(source_path, backup_name)

            if success:
                print(f"✅ Автоматическая резервная копия создана: {backup_name}")
            else:
                print(f"❌ Ошибка автоматической резервной копии: {message}")

        # Запланировать задачу
        interval_seconds = interval_hours * 3600
        self.scheduler.every(interval_seconds).seconds.do(backup_job)

        # Запустить планировщик в отдельном потоке
        if not self._running:
            self._running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()

    def stop_auto_backup(self) -> None:
        """Остановить автоматическое резервное копирование."""
        self._running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

    def _run_scheduler(self) -> None:
        """Запустить планировщик задач."""
        while self._running:
            try:
                self.scheduler.run_pending()
                time.sleep(60)  # Проверка каждую минуту
            except Exception as e:
                print(f"Ошибка в планировщике: {e}")
                time.sleep(60)

    def export_backup(self, backup_name: str, export_path: str) -> Tuple[bool, str]:
        """Экспортировать резервную копию в ZIP архив.

        Args:
            backup_name: Имя резервной копии
            export_path: Путь для экспорта

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            backup_path = self.backups_path / backup_name

            if not backup_path.exists():
                return False, f"Резервная копия не найдена: {backup_path}"

            # Создать ZIP архив
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in backup_path.rglob("*"):
                    if file_path.is_file():
                        arcname = f"{backup_name}/{file_path.relative_to(backup_path)}"
                        zipf.write(file_path, arcname)

            return True, f"Резервная копия экспортирована: {export_path}"

        except Exception as e:
            return False, f"Ошибка экспорта резервной копии: {e}"

    def import_backup(self, archive_path: str) -> Tuple[bool, str]:
        """Импортировать резервную копию из ZIP архива.

        Args:
            archive_path: Путь к архиву

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                # Определить имя резервной копии из архива
                file_list = zipf.namelist()
                if not file_list:
                    return False, "Архив пуст"

                # Предполагаем, что первый элемент - имя директории резервной копии
                first_file = file_list[0]
                backup_name = first_file.split('/')[0]

                # Создать директорию для резервной копии
                backup_path = self.backups_path / backup_name
                backup_path.mkdir(exist_ok=True)

                # Извлечь файлы
                for file_path in file_list:
                    if file_path.startswith(f"{backup_name}/"):
                        relative_path = file_path[len(f"{backup_name}/"):]

                        if relative_path:  # Пропустить корневую директорию
                            target_file = backup_path / relative_path
                            target_file.parent.mkdir(parents=True, exist_ok=True)

                            with zipf.open(file_path) as source, open(target_file, 'wb') as target:
                                shutil.copyfileobj(source, target)

            return True, f"Резервная копия импортирована: {backup_name}"

        except Exception as e:
            return False, f"Ошибка импорта резервной копии: {e}"

    def get_backup_stats(self) -> Dict[str, Any]:
        """Получить статистику резервных копий.

        Returns:
            Dict[str, Any]: Статистика резервных копий
        """
        try:
            backups = self.list_backups()

            total_backups = len(backups)
            total_size = sum(backup["size_mb"] for backup in backups)

            # Статистика по датам
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)

            today_count = 0
            week_count = 0
            month_count = 0

            for backup in backups:
                created_at = datetime.fromisoformat(backup["created_at"]).date()

                if created_at == today:
                    today_count += 1
                if created_at >= week_ago:
                    week_count += 1
                if created_at >= month_ago:
                    month_count += 1

            stats = {
                "total_backups": total_backups,
                "total_size_mb": round(total_size, 2),
                "today_backups": today_count,
                "week_backups": week_count,
                "month_backups": month_count,
                "oldest_backup": backups[-1]["created_at"] if backups else None,
                "newest_backup": backups[0]["created_at"] if backups else None
            }

            return stats

        except Exception as e:
            return {"error": f"Ошибка получения статистики: {e}"}


class WorkstationBackupManager:
    """Менеджер резервного копирования для рабочих станций."""

    def __init__(self, base_path: Path):
        """Инициализация менеджера резервного копирования рабочих станций.

        Args:
            base_path: Базовая директория для резервных копий
        """
        self.base_path = Path(base_path)
        self.workstation_backups_path = self.base_path / "workstation_backups"
        self.workstation_backups_path.mkdir(parents=True, exist_ok=True)

    def backup_workstation_configs(self, workstation_id: str, source_path: str) -> Tuple[bool, str]:
        """Создать резервную копию конфигураций рабочей станции.

        Args:
            workstation_id: ID рабочей станции
            source_path: Путь к конфигурациям на рабочей станции

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{workstation_id}_{timestamp}"

            # Создать локальную директорию для резервной копии
            backup_path = self.workstation_backups_path / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)

            # Копировать конфигурации через SMB
            success = self._copy_workstation_configs(source_path, str(backup_path))

            if success:
                # Создать метаданные
                metadata = {
                    "workstation_id": workstation_id,
                    "backup_name": backup_name,
                    "created_at": datetime.now().isoformat(),
                    "source_path": source_path,
                    "backup_type": "workstation_configs"
                }

                metadata_file = backup_path / "metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

                return True, f"Резервная копия рабочей станции создана: {backup_path}"
            else:
                return False, "Ошибка копирования конфигураций рабочей станции"

        except Exception as e:
            return False, f"Ошибка резервного копирования рабочей станции: {e}"

    def _copy_workstation_configs(self, source_path: str, target_path: str) -> bool:
        """Скопировать конфигурации с рабочей станции.

        Args:
            source_path: Исходный путь SMB
            target_path: Локальный путь назначения

        Returns:
            bool: True если копирование успешно
        """
        try:
            # Использовать robocopy для копирования через SMB
            cmd = f'robocopy "{source_path}" "{target_path}" /E /COPY:DAT /R:3 /W:10 /NFL /NDL'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            return result.returncode in [0, 1]  # 0 - успех, 1 - только копирование

        except Exception as e:
            print(f"Ошибка копирования конфигураций: {e}")
            return False

    def restore_workstation_configs(self, workstation_id: str, target_path: str) -> Tuple[bool, str]:
        """Восстановить конфигурации на рабочую станцию.

        Args:
            workstation_id: ID рабочей станции
            target_path: Путь для восстановления на рабочей станции

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            # Найти последнюю резервную копию для рабочей станции
            backup_path = self._find_latest_workstation_backup(workstation_id)

            if not backup_path:
                return False, f"Резервная копия для станции {workstation_id} не найдена"

            # Копировать файлы обратно на рабочую станцию
            success = self._copy_workstation_configs(str(backup_path), target_path)

            if success:
                return True, f"Конфигурации восстановлены на станцию {workstation_id}"
            else:
                return False, "Ошибка восстановления конфигураций"

        except Exception as e:
            return False, f"Ошибка восстановления конфигураций: {e}"

    def _find_latest_workstation_backup(self, workstation_id: str) -> Optional[Path]:
        """Найти последнюю резервную копию рабочей станции.

        Args:
            workstation_id: ID рабочей станции

        Returns:
            Optional[Path]: Путь к резервной копии или None
        """
        try:
            # Найти все резервные копии для рабочей станции
            workstation_backups = []

            for backup_dir in self.workstation_backups_path.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith(f"{workstation_id}_"):
                    metadata_file = backup_dir / "metadata.json"

                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)

                            if metadata.get("workstation_id") == workstation_id:
                                workstation_backups.append(backup_dir)
                        except Exception:
                            pass

            if workstation_backups:
                # Вернуть самую новую резервную копию
                return max(workstation_backups, key=lambda p: p.stat().st_mtime)

            return None

        except Exception as e:
            print(f"Ошибка поиска резервной копии: {e}")
            return None

    def list_workstation_backups(self, workstation_id: str = None) -> List[Dict[str, Any]]:
        """Получить список резервных копий рабочих станций.

        Args:
            workstation_id: ID рабочей станции (опционально)

        Returns:
            List[Dict[str, Any]]: Список резервных копий
        """
        backups = []

        try:
            for backup_dir in self.workstation_backups_path.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / "metadata.json"

                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)

                            # Фильтр по ID рабочей станции
                            if workstation_id and metadata.get("workstation_id") != workstation_id:
                                continue

                            backup_info = {
                                "name": backup_dir.name,
                                "workstation_id": metadata.get("workstation_id"),
                                "created_at": metadata.get("created_at"),
                                "source_path": metadata.get("source_path"),
                                "size_mb": self._get_directory_size(backup_dir)
                            }

                            backups.append(backup_info)

                        except Exception as e:
                            print(f"Ошибка чтения метаданных {metadata_file}: {e}")

        except Exception as e:
            print(f"Ошибка получения списка резервных копий: {e}")

        # Сортировка по дате создания
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return backups

    def _get_directory_size(self, directory: Path) -> float:
        """Получить размер директории в МБ."""
        try:
            total_size = 0
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size

            return round(total_size / (1024 * 1024), 2)

        except Exception:
            return 0.0


# Глобальные экземпляры менеджеров
_main_backup_manager: Optional[BackupManager] = None
_workstation_backup_manager: Optional[WorkstationBackupManager] = None


def get_backup_manager() -> BackupManager:
    """Получить глобальный экземпляр менеджера резервного копирования.

    Returns:
        BackupManager: Менеджер резервного копирования
    """
    global _main_backup_manager

    if _main_backup_manager is None:
        from ..core.config import get_config
        config = get_config()
        _main_backup_manager = BackupManager(config.backups_dir)

    return _main_backup_manager


def get_workstation_backup_manager() -> WorkstationBackupManager:
    """Получить глобальный экземпляр менеджера резервного копирования рабочих станций.

    Returns:
        WorkstationBackupManager: Менеджер резервного копирования рабочих станций
    """
    global _workstation_backup_manager

    if _workstation_backup_manager is None:
        from ..core.config import get_config
        config = get_config()
        _workstation_backup_manager = WorkstationBackupManager(config.backups_dir)

    return _workstation_backup_manager