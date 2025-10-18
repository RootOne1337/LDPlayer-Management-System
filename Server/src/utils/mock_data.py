"""
Mock data для разработки Web UI.
Предоставляет тестовые данные когда реальные workstations недоступны.
"""

from typing import List, Dict, Any
from datetime import datetime
import random

# Mock эмуляторы для тестирования
MOCK_EMULATORS = [
    {
        "id": "emu-001",
        "name": "Android-Game-1",
        "workstation_id": "localhost",
        "status": "running",
        "created_at": "2025-10-15T10:30:00",
        "config": {
            "cpu": 4,
            "memory": 4096,
            "resolution": "1920x1080",
            "android_version": "9.0"
        }
    },
    {
        "id": "emu-002",
        "name": "Android-Game-2",
        "workstation_id": "localhost",
        "status": "stopped",
        "created_at": "2025-10-15T11:00:00",
        "config": {
            "cpu": 2,
            "memory": 2048,
            "resolution": "1280x720",
            "android_version": "7.1"
        }
    },
    {
        "id": "emu-003",
        "name": "Test-Device",
        "workstation_id": "workstation-1",
        "status": "running",
        "created_at": "2025-10-16T09:15:00",
        "config": {
            "cpu": 4,
            "memory": 3072,
            "resolution": "1920x1080",
            "android_version": "9.0"
        }
    },
    {
        "id": "emu-004",
        "name": "Production-Bot-1",
        "workstation_id": "workstation-2",
        "status": "running",
        "created_at": "2025-10-14T14:20:00",
        "config": {
            "cpu": 6,
            "memory": 6144,
            "resolution": "2560x1440",
            "android_version": "11.0"
        }
    },
    {
        "id": "emu-005",
        "name": "Production-Bot-2",
        "workstation_id": "workstation-2",
        "status": "stopped",
        "created_at": "2025-10-14T14:25:00",
        "config": {
            "cpu": 6,
            "memory": 6144,
            "resolution": "2560x1440",
            "android_version": "11.0"
        }
    },
    {
        "id": "emu-006",
        "name": "Dev-Testing",
        "workstation_id": "workstation-3",
        "status": "running",
        "created_at": "2025-10-17T08:00:00",
        "config": {
            "cpu": 2,
            "memory": 2048,
            "resolution": "1280x720",
            "android_version": "7.1"
        }
    }
]

# Mock workstations
MOCK_WORKSTATIONS = [
    {
        "id": "localhost",
        "name": "Development Machine",
        "host": "127.0.0.1",
        "port": 5985,
        "status": "online",
        "emulator_count": 2,
        "last_check": datetime.now().isoformat()
    },
    {
        "id": "workstation-1",
        "name": "Work Station 1",
        "host": "192.168.1.101",
        "port": 5985,
        "status": "online",
        "emulator_count": 1,
        "last_check": datetime.now().isoformat()
    },
    {
        "id": "workstation-2",
        "name": "Work Station 2",
        "host": "192.168.1.102",
        "port": 5985,
        "status": "online",
        "emulator_count": 2,
        "last_check": datetime.now().isoformat()
    },
    {
        "id": "workstation-3",
        "name": "Work Station 3",
        "host": "192.168.1.103",
        "port": 5985,
        "status": "offline",
        "emulator_count": 1,
        "last_check": datetime.now().isoformat()
    }
]

# Mock операции
MOCK_OPERATIONS = [
    {
        "id": "op-001",
        "type": "start_emulator",
        "emulator_id": "emu-001",
        "status": "completed",
        "created_at": "2025-10-17T10:30:00",
        "completed_at": "2025-10-17T10:30:15",
        "progress": 100
    },
    {
        "id": "op-002",
        "type": "stop_emulator",
        "emulator_id": "emu-002",
        "status": "in_progress",
        "created_at": "2025-10-17T10:35:00",
        "completed_at": None,
        "progress": 65
    }
]


def get_mock_emulators(workstation_id: str = None) -> List[Dict[str, Any]]:
    """Получить mock эмуляторы."""
    if workstation_id:
        return [e for e in MOCK_EMULATORS if e["workstation_id"] == workstation_id]
    return MOCK_EMULATORS


def get_mock_emulator(emulator_id: str) -> Dict[str, Any] | None:
    """Получить один mock эмулятор."""
    for emu in MOCK_EMULATORS:
        if emu["id"] == emulator_id:
            return emu
    return None


def get_mock_workstations() -> List[Dict[str, Any]]:
    """Получить mock workstations."""
    return MOCK_WORKSTATIONS


def get_mock_system_status() -> Dict[str, Any]:
    """Получить mock системный статус."""
    return {
        "server_version": "1.0.0-dev",
        "server_status": "running",
        "total_workstations": len(MOCK_WORKSTATIONS),
        "online_workstations": sum(1 for w in MOCK_WORKSTATIONS if w["status"] == "online"),
        "total_emulators": len(MOCK_EMULATORS),
        "running_emulators": sum(1 for e in MOCK_EMULATORS if e["status"] == "running"),
        "stopped_emulators": sum(1 for e in MOCK_EMULATORS if e["status"] == "stopped"),
        "active_operations": len([o for o in MOCK_OPERATIONS if o["status"] == "in_progress"]),
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": random.randint(3600, 86400)
    }


def get_mock_operations() -> List[Dict[str, Any]]:
    """Получить mock операции."""
    return MOCK_OPERATIONS
