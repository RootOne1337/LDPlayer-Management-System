"""
Unit тесты для EmulatorService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.models.entities import Emulator, EmulatorStatus
from src.services.emulator_service import EmulatorService
from src.utils.exceptions import EmulatorNotFoundError


@pytest.mark.unit
@pytest.mark.asyncio
class TestEmulatorService:
    """Тесты для EmulatorService."""

    async def test_get_all_returns_list(self, emulator_service, mock_emulator):
        """Тест: get_all возвращает список эмуляторов."""
        # Arrange
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[mock_emulator]
        )
        
        # Act
        emulators, total = await emulator_service.get_all(limit=10, offset=0)
        
        # Assert
        assert isinstance(emulators, list)
        assert isinstance(total, int)

    async def test_get_by_id_returns_emulator(self, emulator_service, mock_emulator):
        """Тест: get_by_id возвращает эмулятор по ID."""
        # Arrange
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[mock_emulator]
        )
        
        # Act
        result = await emulator_service.get_by_id("emu-001")
        
        # Assert
        assert result is not None
        assert result.id == "emu-001"

    async def test_get_by_id_returns_none_for_missing(self, emulator_service_empty):
        """Тест: get_by_id возвращает None если эмулятор не найден."""
        # Arrange - manager возвращает None
        
        # Act
        result = await emulator_service_empty.get_by_id("emu-nonexistent")
        
        # Assert
        assert result is None

    async def test_get_by_workstation(self, emulator_service, mock_emulator):
        """Тест: get_by_workstation фильтрует эмуляторы по станции."""
        # Arrange
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[mock_emulator]
        )
        
        # Act
        emulators = await emulator_service.get_by_workstation("ws-001")
        
        # Assert
        assert isinstance(emulators, list)
        for emu in emulators:
            assert emu.workstation_id == "ws-001"

    async def test_get_by_workstation_filters_correctly(self, emulator_service_multi):
        """Тест: get_by_workstation не возвращает эмуляторы других станций."""
        # Arrange - manager возвращает два эмулятора для разных станций
        
        # Act
        emulators = await emulator_service_multi.get_by_workstation("ws-001")
        
        # Assert
        assert len(emulators) == 1
        assert emulators[0].id == "emu-001"
        assert emulators[0].workstation_id == "ws-001"

    async def test_create_emulator(self, emulator_service):
        """Тест: create создает новый эмулятор."""
        # Arrange
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[]
        )
        
        data = {
            "id": "emu-new",
            "name": "NewEmulator",
            "workstation_id": "ws-001",
            "config": {}
        }
        
        # Act
        result = await emulator_service.create(data)
        
        # Assert
        assert result.id == "em_newemulator"
        assert result.name == "NewEmulator"
        assert result.workstation_id == "ws-001"

    async def test_create_with_default_status(self, emulator_service):
        """Тест: create инициализирует статус эмулятора."""
        # Arrange
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[]
        )
        
        data = {
            "id": "emu-status",
            "name": "StatusEmulator",
            "workstation_id": "ws-001",
            "config": {}
        }
        
        # Act
        result = await emulator_service.create(data)
        
        # Assert
        assert result.status in [EmulatorStatus.STOPPED, EmulatorStatus.RUNNING]

    async def test_update_emulator(self, emulator_service, mock_emulator):
        """Тест: update обновляет эмулятор."""
        # Arrange
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[mock_emulator]
        )
        
        data = {"name": "UpdatedName"}
        
        # Act
        result = await emulator_service.update("emu-001", data)
        
        # Assert
        assert result.id == "emu-001"

    async def test_update_nonexistent(self, emulator_service_empty):
        """Тест: update выбросит исключение при обновлении несуществующего эмулятора."""
        # Arrange - manager возвращает None
        
        # Act & Assert
        with pytest.raises(EmulatorNotFoundError):
            await emulator_service_empty.update("emu-nonexistent", {})

    async def test_delete_emulator(self, emulator_service, mock_emulator):
        """Тест: delete удаляет эмулятор."""
        # Arrange
        mock_operation = MagicMock(id="op-001", type="delete", status="queued")
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[mock_emulator]
        )
        emulator_service.manager.delete_emulator = MagicMock(
            return_value=mock_operation
        )
        
        # Act
        result = await emulator_service.delete("emu-001")
        
        # Assert
        assert isinstance(result, dict)
        assert "operation_id" in result
        assert result["operation_type"] == "delete"

    async def test_delete_nonexistent(self, emulator_service_empty):
        """Тест: delete возвращает operation dict если эмулятор не найден."""
        # Arrange - manager возвращает None, но operation все равно ставится в очередь
        mock_operation = MagicMock(id="op-002", type="delete", status="queued")
        emulator_service_empty.manager.delete_emulator = MagicMock(
            return_value=mock_operation
        )
        
        # Act
        result = await emulator_service_empty.delete("emu-nonexistent")
        
        # Assert
        assert isinstance(result, dict)
        assert "operation_id" in result

    async def test_start_emulator(self, emulator_service, mock_emulator):
        """Тест: start запускает эмулятор."""
        # Arrange
        mock_operation = MagicMock(id="op-003", type="start", status="queued")
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[mock_emulator]
        )
        emulator_service.manager.start_emulator = MagicMock(
            return_value=mock_operation
        )
        
        # Act
        result = await emulator_service.start("emu-001")
        
        # Assert
        assert isinstance(result, dict)
        assert result["operation_type"] == "start"
        assert "operation_id" in result

    async def test_start_nonexistent(self, emulator_service_empty):
        """Тест: start ставит операцию в очередь даже для несуществующего эмулятора."""
        # Arrange - manager возвращает None, но operation все равно ставится в очередь
        mock_operation = MagicMock(id="op-004", type="start", status="queued")
        emulator_service_empty.manager.start_emulator = MagicMock(
            return_value=mock_operation
        )
        
        # Act
        result = await emulator_service_empty.start("emu-nonexistent")
        
        # Assert
        assert isinstance(result, dict)
        assert "operation_id" in result
        assert result["operation_type"] == "start"

    async def test_stop_emulator(self, emulator_service, mock_emulator):
        """Тест: stop останавливает эмулятор."""
        # Arrange
        mock_operation = MagicMock(id="op-005", type="stop", status="queued")
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[mock_emulator]
        )
        emulator_service.manager.stop_emulator = MagicMock(
            return_value=mock_operation
        )
        
        # Act
        result = await emulator_service.stop("emu-001")
        
        # Assert
        assert isinstance(result, dict)
        assert result["operation_type"] == "stop"
        assert "operation_id" in result

    async def test_stop_nonexistent(self, emulator_service_empty):
        """Тест: stop ставит операцию в очередь даже для несуществующего эмулятора."""
        # Arrange - manager возвращает None, но operation все равно ставится в очередь
        mock_operation = MagicMock(id="op-006", type="stop", status="queued")
        emulator_service_empty.manager.stop_emulator = MagicMock(
            return_value=mock_operation
        )
        
        # Act
        result = await emulator_service_empty.stop("emu-nonexistent")
        
        # Assert
        assert isinstance(result, dict)
        assert "operation_id" in result
        assert result["operation_type"] == "stop"

    async def test_get_all_empty_list(self, emulator_service_empty):
        """Тест: get_all возвращает пустой список если нет эмуляторов."""
        # Arrange - manager возвращает []
        
        # Act
        emulators, total = await emulator_service_empty.get_all()
        
        # Assert
        assert emulators == []
        assert total == 0

    async def test_get_by_workstation_empty(self, emulator_service):
        """Тест: get_by_workstation возвращает пустой список если нет эмуляторов."""
        # Arrange
        emulator_service.manager.get_emulators = MagicMock(
            return_value=[]
        )
        
        # Act
        emulators = await emulator_service.get_by_workstation("ws-nonexistent")
        
        # Assert
        assert emulators == []
