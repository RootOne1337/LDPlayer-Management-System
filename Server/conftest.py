"""
Pytest конфигурация и fixtures для тестирования LDPlayerManagementSystem
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Generator

# Добавить корневую папку в путь
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.core.container import DIContainer, container
from src.models.entities import Workstation, Emulator, WorkstationStatus, EmulatorStatus
from src.services.workstation_service import WorkstationService
from src.services.emulator_service import EmulatorService
from src.remote.ldplayer_manager import LDPlayerManager
from fastapi.testclient import TestClient


# ============================================================================
# ENTITY FIXTURES (Без зависимостей - первые)
# ============================================================================

@pytest.fixture
def mock_workstation() -> Workstation:
    """Создать mock Workstation entity."""
    return Workstation(
        id="ws-001",
        name="Test Workstation",
        ip_address="192.168.1.100",
        port=5555,
        status=WorkstationStatus.ONLINE,
        config={}
    )


@pytest.fixture
def mock_emulator() -> Emulator:
    """Создать mock Emulator entity."""
    return Emulator(
        id="emu-001",
        name="TestEmulator",
        workstation_id="ws-001",
        status=EmulatorStatus.RUNNING,
        config={},
        created_at="2025-10-17T00:00:00",
        updated_at="2025-10-17T00:00:00"
    )


# ============================================================================
# EMPTY MANAGER FIXTURES (для "not found" cases)
# ============================================================================

@pytest.fixture
def empty_mock_ldplayer_manager() -> MagicMock:
    """Создать mock LDPlayerManager который возвращает пустые результаты."""
    manager = MagicMock()
    
    # Все методы возвращают пустые значения или None
    manager.get_workstations = AsyncMock(return_value=[])
    manager.get_emulators = MagicMock(return_value=[])  # Синхронный метод!
    manager.find_workstation = AsyncMock(return_value=None)
    manager.find_emulator = AsyncMock(return_value=None)
    manager.is_connected = True
    
    return manager


@pytest.fixture
def multi_emulator_mock_ldplayer_manager() -> MagicMock:
    """Создать mock LDPlayerManager с несколькими эмуляторами для фильтрации."""
    emu1 = Emulator(
        id="emu-001", name="Emu1", workstation_id="ws-001",
        status=EmulatorStatus.RUNNING, config={},
        created_at="2025-10-17T00:00:00", updated_at="2025-10-17T00:00:00"
    )
    emu2 = Emulator(
        id="emu-002", name="Emu2", workstation_id="ws-002",
        status=EmulatorStatus.STOPPED, config={},
        created_at="2025-10-17T00:00:00", updated_at="2025-10-17T00:00:00"
    )
    
    manager = MagicMock()
    manager.get_workstations = AsyncMock(return_value=[])
    manager.get_emulators = MagicMock(return_value=[emu1, emu2])  # Синхронный метод!
    manager.find_workstation = AsyncMock(return_value=Workstation(
        id="ws-001", name="WS1", ip_address="192.168.1.1", port=5555
    ))
    manager.find_emulator = AsyncMock(return_value=None)
    manager.is_connected = True
    
    return manager


# ============================================================================
# DI КОНТЕЙНЕР FIXTURES
# ============================================================================

@pytest.fixture
def di_container() -> Generator[DIContainer, None, None]:
    """Создать чистый DI контейнер для каждого теста."""
    test_container = DIContainer()
    yield test_container
    # Cleanup после теста
    test_container.clear()


@pytest.fixture
def mock_ldplayer_manager(mock_workstation, mock_emulator) -> MagicMock:
    """Создать mock LDPlayerManager с правильными методами."""
    manager = MagicMock()
    
    # Методы возвращают конкретные значения
    manager.get_workstations = AsyncMock(return_value=[mock_workstation])
    manager.get_emulators = MagicMock(return_value=[mock_emulator])  # Синхронный!
    manager.find_workstation = AsyncMock(return_value=mock_workstation)
    manager.find_emulator = AsyncMock(return_value=mock_emulator)
    manager.is_connected = True
    
    return manager


@pytest.fixture
def workstation_service(mock_ldplayer_manager) -> WorkstationService:
    """Создать WorkstationService с mock'ированным LDPlayerManager."""
    service = WorkstationService(mock_ldplayer_manager)
    return service


@pytest.fixture
def workstation_service_empty(empty_mock_ldplayer_manager) -> WorkstationService:
    """Создать WorkstationService с пустым mock manager (для "not found" cases)."""
    service = WorkstationService(empty_mock_ldplayer_manager)
    return service


@pytest.fixture
def emulator_service(mock_ldplayer_manager) -> EmulatorService:
    """Создать EmulatorService с mock'ированным LDPlayerManager."""
    service = EmulatorService(mock_ldplayer_manager)
    return service


@pytest.fixture
def emulator_service_empty(empty_mock_ldplayer_manager) -> EmulatorService:
    """Создать EmulatorService с пустым mock manager (для "not found" cases)."""
    service = EmulatorService(empty_mock_ldplayer_manager)
    return service


@pytest.fixture
def emulator_service_multi(multi_emulator_mock_ldplayer_manager) -> EmulatorService:
    """Создать EmulatorService с несколькими эмуляторами (для фильтрации)."""
    service = EmulatorService(multi_emulator_mock_ldplayer_manager)
    return service


# ============================================================================
# FASTAPI FIXTURES
# ============================================================================

@pytest.fixture
def test_app():
    """Создать TestClient для FastAPI приложения."""
    from src.core.server import app
    return TestClient(app)


@pytest.fixture
def test_app_with_di(di_container, mock_ldplayer_manager):
    """Создать TestClient с настроенным DI контейнером."""
    from src.core.server import app, initialize_di_services
    
    # Переопределить инициализацию DI для тестов
    di_container.register("ldplayer_manager", mock_ldplayer_manager)
    di_container.register("workstation_service", WorkstationService(mock_ldplayer_manager))
    di_container.register("emulator_service", EmulatorService(mock_ldplayer_manager))
    
    return TestClient(app)


# ============================================================================
# DATABASE FIXTURES (когда будет БД)
# ============================================================================

@pytest.fixture
def test_db():
    """Подключение к тестовой БД."""
    # TODO: Когда добавим БД (PostgreSQL)
    # db = SessionLocal()
    # yield db
    # db.close()
    yield None


# ============================================================================
# PYTEST HOOKS
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Настройка окружения для всех тестов."""
    # Установить переменные окружения для тестирования
    import os
    os.environ["LOG_LEVEL"] = "WARNING"  # Меньше логов при тестировании
    os.environ["DEV_MODE"] = "false"
    yield


def pytest_configure(config):
    """Настройка pytest при запуске."""
    # Можно добавить кастомные настройки
    pass


def pytest_collection_modifyitems(config, items):
    """Модификация собранных тестов."""
    for item in items:
        # Если в имени теста "async", добавить маркер
        if "async" in item.nodeid:
            item.add_marker(pytest.mark.asyncio)
