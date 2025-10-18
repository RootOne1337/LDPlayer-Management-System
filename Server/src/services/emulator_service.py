"""Emulator service with business logic."""

from typing import List, Optional, Dict, Any, Tuple
from src.services.base_service import BaseService
from src.models.entities import Emulator, EmulatorStatus
from src.utils.exceptions import EmulatorNotFoundError, WorkstationNotFoundError
import logging

logger = logging.getLogger(__name__)


class EmulatorService(BaseService[Emulator]):
    """
    Service for managing emulators.
    
    Encapsulates all emulator-related business logic.
    """
    
    def __init__(self, manager: Any):
        """
        Initialize EmulatorService.
        
        Args:
            manager: LDPlayerManager instance
        """
        super().__init__()
        self.manager = manager
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        workstation_id: Optional[str] = None
    ) -> Tuple[List[Emulator], int]:
        """
        Get all emulators with optional filtering.
        
        Args:
            limit: Number of items to return
            offset: Offset for pagination
            workstation_id: Filter by workstation (optional)
        
        Returns:
            Tuple of (emulators, total_count)
        """
        try:
            # Get all emulators from LDPlayer via manager
            # LDPlayerManager.get_emulators() -> WorkstationManager.get_emulators_list()
            all_emulators = self.manager.get_emulators()
            
            # Filter by workstation if specified
            if workstation_id:
                all_emulators = [
                    em for em in all_emulators
                    if em.workstation_id == workstation_id
                ]
            
            total = len(all_emulators)
            
            # Apply pagination
            paginated = all_emulators[offset:offset + limit]
            
            return paginated, total
        except Exception as e:
            logger.error(f"Error getting emulators: {e}")
            raise
    
    async def get_by_id(self, emulator_id: str) -> Optional[Emulator]:
        """
        Get emulator by ID.
        
        Args:
            emulator_id: Emulator identifier
        
        Returns:
            Emulator or None if not found
        """
        try:
            em = await self.manager.find_emulator(emulator_id)
            return em
        except Exception as e:
            logger.error(f"Error getting emulator {emulator_id}: {e}")
            return None
    
    async def get_by_workstation(self, workstation_id: str) -> List[Emulator]:
        """
        Get all emulators for a workstation.
        
        Args:
            workstation_id: Workstation identifier
        
        Returns:
            List of emulators
        
        Raises:
            WorkstationNotFoundError: If workstation not found
        """
        try:
            # Verify workstation exists
            ws = await self.manager.find_workstation(workstation_id)
            if not ws:
                raise WorkstationNotFoundError(workstation_id)
            
            # Get emulators for this workstation
            all_emus = self.manager.get_emulators()  # Синхронный метод!
            emulators = [
                em for em in all_emus
                if em.workstation_id == workstation_id
            ]
            return emulators
        except WorkstationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting emulators for workstation {workstation_id}: {e}")
            raise
    
    async def create(self, data: Dict[str, Any]) -> Emulator:
        """
        Create new emulator.
        
        Args:
            data: Emulator data (name, workstation_id, config)
        
        Returns:
            Created emulator
        
        Raises:
            ValueError: If data is invalid
            WorkstationNotFoundError: If workstation not found
        """
        try:
            name = data.get("name")
            workstation_id = data.get("workstation_id")
            config = data.get("config", {})
            
            if not name or not workstation_id:
                raise ValueError("name and workstation_id are required")
            
            # Verify workstation exists
            ws = await self.manager.find_workstation(workstation_id)
            if not ws:
                raise WorkstationNotFoundError(workstation_id)
            
            em = Emulator(
                id=f"em_{name.lower().replace(' ', '_')}",
                name=name,
                workstation_id=workstation_id,
                status=EmulatorStatus.STOPPED,
                config=config
            )
            
            logger.info(f"Created emulator: {em.id}")
            return em
        except Exception as e:
            logger.error(f"Error creating emulator: {e}")
            raise
    
    async def update(
        self,
        emulator_id: str,
        data: Dict[str, Any]
    ) -> Emulator:
        """
        Update emulator.
        
        Args:
            emulator_id: Emulator identifier
            data: Update data
        
        Returns:
            Updated emulator
        
        Raises:
            EmulatorNotFoundError: If emulator not found
        """
        em = await self.get_or_fail(emulator_id)
        
        # Update fields
        if "name" in data:
            em.name = data["name"]
        if "config" in data:
            em.config = data["config"]
        
        logger.info(f"Updated emulator: {emulator_id}")
        return em
    
    async def delete(self, emulator_id: str) -> Dict[str, Any]:
        """
        Delete emulator.
        
        Args:
            emulator_id: Emulator identifier
        
        Returns:
            Dict with operation status
        
        Raises:
            EmulatorNotFoundError: If emulator not found
        """
        try:
            # Extract emulator name from ID or use it directly
            emulator_name = emulator_id.split("_", 1)[-1] if "_" in emulator_id else emulator_id
            
            # Queue operation with LDPlayerManager
            operation = self.manager.delete_emulator(emulator_name)
            
            logger.info(f"Queued delete operation for emulator: {emulator_id}")
            
            return {
                "status": "queued",
                "operation_id": operation.id,
                "emulator_id": emulator_id,
                "operation_type": "delete"
            }
        except Exception as e:
            logger.error(f"Error deleting emulator {emulator_id}: {e}")
            raise
    
    async def start(self, emulator_id: str, workstation_id: str = None) -> Dict[str, Any]:
        """
        Start emulator.
        
        Args:
            emulator_id: Emulator identifier (name)
            workstation_id: Workstation ID (optional)
        
        Returns:
            Dict with operation status
        
        Raises:
            EmulatorNotFoundError: If emulator not found
        """
        try:
            # Extract emulator name from ID or use it directly
            emulator_name = emulator_id.split("_", 1)[-1] if "_" in emulator_id else emulator_id
            
            # Queue operation with LDPlayerManager
            operation = self.manager.start_emulator(emulator_name)
            
            logger.info(f"Queued start operation for emulator: {emulator_id}")
            
            return {
                "status": "queued",
                "operation_id": operation.id,
                "emulator_id": emulator_id,
                "operation_type": "start"
            }
        except Exception as e:
            logger.error(f"Error starting emulator {emulator_id}: {e}")
            raise
    
    async def stop(self, emulator_id: str, workstation_id: str = None) -> Dict[str, Any]:
        """
        Stop emulator.
        
        Args:
            emulator_id: Emulator identifier (name)
            workstation_id: Workstation ID (optional)
        
        Returns:
            Dict with operation status
        
        Raises:
            EmulatorNotFoundError: If emulator not found
        """
        try:
            # Extract emulator name from ID or use it directly
            emulator_name = emulator_id.split("_", 1)[-1] if "_" in emulator_id else emulator_id
            
            # Queue operation with LDPlayerManager
            operation = self.manager.stop_emulator(emulator_name)
            
            logger.info(f"Queued stop operation for emulator: {emulator_id}")
            
            return {
                "status": "queued",
                "operation_id": operation.id,
                "emulator_id": emulator_id,
                "operation_type": "stop"
            }
        except Exception as e:
            logger.error(f"Error stopping emulator {emulator_id}: {e}")
            raise
    
    async def rename(self, emulator_id: str, new_name: str) -> Dict[str, Any]:
        """
        Rename emulator.
        
        Args:
            emulator_id: Emulator identifier (current name)
            new_name: New name for emulator
        
        Returns:
            Dict with operation status
        
        Raises:
            EmulatorNotFoundError: If emulator not found
        """
        try:
            # Extract emulator name from ID or use it directly
            old_name = emulator_id.split("_", 1)[-1] if "_" in emulator_id else emulator_id
            
            # Queue operation with LDPlayerManager
            operation = self.manager.rename_emulator(old_name, new_name)
            
            logger.info(f"Queued rename operation for emulator: {emulator_id} -> {new_name}")
            
            return {
                "status": "queued",
                "operation_id": operation.id,
                "emulator_id": emulator_id,
                "new_name": new_name,
                "operation_type": "rename"
            }
        except Exception as e:
            logger.error(f"Error renaming emulator {emulator_id}: {e}")
            raise
    
    async def batch_start(self, emulator_ids: List[str]) -> Dict[str, Any]:
        """
        Start multiple emulators.
        
        Args:
            emulator_ids: List of emulator identifiers
        
        Returns:
            Dict with operation statuses
        """
        try:
            operations = []
            
            for emulator_id in emulator_ids:
                emulator_name = emulator_id.split("_", 1)[-1] if "_" in emulator_id else emulator_id
                operation = self.manager.start_emulator(emulator_name)
                operations.append({
                    "emulator_id": emulator_id,
                    "operation_id": operation.id
                })
            
            logger.info(f"Queued batch start for {len(emulator_ids)} emulators")
            
            return {
                "status": "queued",
                "operation_type": "batch_start",
                "count": len(operations),
                "operations": operations
            }
        except Exception as e:
            logger.error(f"Error batch starting emulators: {e}")
            raise
    
    async def batch_stop(self, emulator_ids: List[str]) -> Dict[str, Any]:
        """
        Stop multiple emulators.
        
        Args:
            emulator_ids: List of emulator identifiers
        
        Returns:
            Dict with operation statuses
        """
        try:
            operations = []
            
            for emulator_id in emulator_ids:
                emulator_name = emulator_id.split("_", 1)[-1] if "_" in emulator_id else emulator_id
                operation = self.manager.stop_emulator(emulator_name)
                operations.append({
                    "emulator_id": emulator_id,
                    "operation_id": operation.id
                })
            
            logger.info(f"Queued batch stop for {len(emulator_ids)} emulators")
            
            return {
                "status": "queued",
                "operation_type": "batch_stop",
                "count": len(operations),
                "operations": operations
            }
        except Exception as e:
            logger.error(f"Error batch stopping emulators: {e}")
            raise
    
    def _not_found_exception(self, item_id: str) -> Exception:
        """Create EmulatorNotFoundError."""
        return EmulatorNotFoundError(item_id)
