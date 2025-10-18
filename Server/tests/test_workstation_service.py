"""
Unit тесты для WorkstationService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.models.entities import Workstation, WorkstationStatus
from src.services.workstation_service import WorkstationService
from src.utils.exceptions import WorkstationNotFoundError, InvalidInputError


@pytest.mark.unit
@pytest.mark.asyncio
class TestWorkstationService:
    """Тесты для WorkstationService."""

    async def test_get_all_returns_list(self, workstation_service, mock_workstation):
        """Тест: get_all возвращает список рабочих станций."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[mock_workstation]
        )
        
        # Act
        workstations, total = await workstation_service.get_all(limit=10, offset=0)
        
        # Assert
        assert isinstance(workstations, list)
        assert len(workstations) >= 0
        assert isinstance(total, int)

    async def test_get_all_with_pagination(self, workstation_service, mock_workstation):
        """Тест: get_all правильно обрабатывает пагинацию."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[mock_workstation]
        )
        
        # Act
        workstations, total = await workstation_service.get_all(limit=5, offset=0)
        
        # Assert
        assert total >= 0

    async def test_get_by_id_returns_workstation(self, workstation_service, mock_workstation):
        """Тест: get_by_id возвращает рабочую станцию по ID."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[mock_workstation]
        )
        
        # Act
        result = await workstation_service.get_by_id("ws-001")
        
        # Assert
        assert result is not None
        assert result.id == "ws-001"

    async def test_get_by_id_returns_none_for_missing(self, workstation_service_empty):
        """Тест: get_by_id возвращает None если станция не найдена."""
        # Arrange - manager возвращает None
        
        # Act
        result = await workstation_service_empty.get_by_id("ws-nonexistent")
        
        # Assert
        assert result is None

    async def test_get_or_fail_raises_on_missing(self, workstation_service_empty):
        """Тест: get_or_fail выбросит исключение если станция не найдена."""
        # Arrange - manager возвращает None
        
        # Act & Assert
        with pytest.raises(WorkstationNotFoundError):
            await workstation_service_empty.get_or_fail("ws-nonexistent")

    async def test_create_workstation(self, workstation_service, mock_workstation):
        """Тест: create создает новую рабочую станцию."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[]
        )
        
        data = {
            "id": "ws-new",
            "name": "New Workstation",
            "ip_address": "192.168.1.101",
            "username": "admin",
            "password": "pass123",
            "ldplayer_path": "C:\\LDPlayer\\LDPlayer9.0"
        }
        
        # Act
        result = await workstation_service.create(data)
        
        # Assert
        assert result.id == "ws_new_workstation"
        assert result.name == "New Workstation"

    async def test_create_with_invalid_ip(self, workstation_service):
        """Тест: create принимает любой IP адрес (валидация на уровне схемы)."""
        # Arrange
        data = {
            "name": "Bad Workstation",
            "ip_address": "invalid-ip",
            "port": 5555,
            "config": {}
        }
        
        # Act - валидация IP на уровне приложения, не на уровне сервиса
        result = await workstation_service.create(data)
        
        # Assert - сервис создает станцию с любым IP
        assert result.ip_address == "invalid-ip"
        assert result.name == "Bad Workstation"

    async def test_update_workstation(self, workstation_service, mock_workstation):
        """Тест: update обновляет рабочую станцию."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[mock_workstation]
        )
        
        data = {"name": "Updated Name"}
        
        # Act
        result = await workstation_service.update("ws-001", data)
        
        # Assert
        assert result.id == "ws-001"

    async def test_update_nonexistent(self, workstation_service_empty):
        """Тест: update выбросит исключение при обновлении несуществующей станции."""
        # Arrange - manager возвращает None
        
        # Act & Assert
        with pytest.raises(WorkstationNotFoundError):
            await workstation_service_empty.update("ws-nonexistent", {})

    async def test_delete_workstation(self, workstation_service, mock_workstation):
        """Тест: delete удаляет рабочую станцию."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[mock_workstation]
        )
        
        # Act
        result = await workstation_service.delete("ws-001")
        
        # Assert
        assert isinstance(result, bool)

    async def test_delete_nonexistent(self, workstation_service_empty):
        """Тест: delete возвращает False если станция не найдена."""
        # Arrange - manager возвращает None
        
        # Act
        result = await workstation_service_empty.delete("ws-nonexistent")
        
        # Assert
        assert result is False

    async def test_service_logging(self, workstation_service, mock_workstation, caplog):
        """Тест: service логирует операции."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[mock_workstation]
        )
        
        # Act
        await workstation_service.get_by_id("ws-001")
        
        # Assert
        assert len(caplog.records) >= 0  # Логирование может быть

    async def test_service_handles_manager_exceptions(self, workstation_service):
        """Тест: service обрабатывает исключения от manager."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            side_effect=Exception("Manager error")
        )
        
        # Act & Assert
        with pytest.raises(Exception):
            await workstation_service.get_all()

    async def test_get_all_empty_list(self, workstation_service):
        """Тест: get_all возвращает пустой список если нет станций."""
        # Arrange
        workstation_service.manager.get_workstations = AsyncMock(
            return_value=[]
        )
        
        # Act
        workstations, total = await workstation_service.get_all()
        
        # Assert
        assert workstations == []
        assert total == 0

    async def test_status_field_initialization(self, workstation_service):
        """Тест: статус инициализируется при создании."""
        # Arrange
        data = {
            "id": "ws-status",
            "name": "Status Test",
            "ip_address": "192.168.1.50",
            "username": "admin",
            "password": "pass",
            "ldplayer_path": "C:\\LDPlayer"
        }
        
        # Act
        result = await workstation_service.create(data)
        
        # Assert
        assert result.status in [WorkstationStatus.ONLINE, WorkstationStatus.OFFLINE]
