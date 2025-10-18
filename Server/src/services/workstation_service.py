"""Workstation service with business logic."""

from typing import List, Optional, Dict, Any, Tuple
from src.services.base_service import BaseService
from src.models.entities import Workstation, WorkstationStatus
from src.utils.exceptions import WorkstationNotFoundError
import logging

logger = logging.getLogger(__name__)


class WorkstationService(BaseService[Workstation]):
    """
    Service for managing workstations.
    
    Encapsulates all workstation-related business logic.
    """
    
    def __init__(self, manager: Any):
        """
        Initialize WorkstationService.
        
        Args:
            manager: LDPlayerManager instance
        """
        super().__init__()
        self.manager = manager
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Workstation], int]:
        """
        Get all workstations with pagination.
        
        Args:
            limit: Number of items to return
            offset: Offset for pagination
        
        Returns:
            Tuple of (workstations, total_count)
        """
        try:
            # Get all workstations from manager
            all_workstations = await self.manager.get_workstations()
            total = len(all_workstations)
            
            # Apply pagination
            paginated = all_workstations[offset:offset + limit]
            
            return paginated, total
        except Exception as e:
            logger.error(f"Error getting workstations: {e}")
            raise
    
    async def get_by_id(self, workstation_id: str) -> Optional[Workstation]:
        """
        Get workstation by ID.
        
        Args:
            workstation_id: Workstation identifier
        
        Returns:
            Workstation or None if not found
        """
        try:
            ws = await self.manager.find_workstation(workstation_id)
            return ws
        except Exception as e:
            logger.error(f"Error getting workstation {workstation_id}: {e}")
            return None
    
    async def create(self, data: Dict[str, Any]) -> Workstation:
        """
        Create new workstation.
        
        Args:
            data: Workstation data (name, ip_address, port, config)
        
        Returns:
            Created workstation
        
        Raises:
            ValueError: If data is invalid
        """
        try:
            name = data.get("name")
            ip_address = data.get("ip_address")
            port = data.get("port", 5985)
            config = data.get("config", {})
            
            if not name or not ip_address:
                raise ValueError("name and ip_address are required")
            
            ws = Workstation(
                id=f"ws_{name.lower().replace(' ', '_')}",
                name=name,
                ip_address=ip_address,
                port=port,
                status=WorkstationStatus.OFFLINE,
                config=config
            )
            
            logger.info(f"Created workstation: {ws.id}")
            return ws
        except Exception as e:
            logger.error(f"Error creating workstation: {e}")
            raise
    
    async def update(
        self,
        workstation_id: str,
        data: Dict[str, Any]
    ) -> Workstation:
        """
        Update workstation.
        
        Args:
            workstation_id: Workstation identifier
            data: Update data
        
        Returns:
            Updated workstation
        
        Raises:
            WorkstationNotFoundError: If workstation not found
        """
        ws = await self.get_or_fail(workstation_id)
        
        # Update fields
        if "name" in data:
            ws.name = data["name"]
        if "ip_address" in data:
            ws.ip_address = data["ip_address"]
        if "port" in data:
            ws.port = data["port"]
        if "config" in data:
            ws.config = data["config"]
        
        logger.info(f"Updated workstation: {workstation_id}")
        return ws
    
    async def delete(self, workstation_id: str) -> bool:
        """
        Delete workstation.
        
        Args:
            workstation_id: Workstation identifier
        
        Returns:
            True if deleted, False if not found
        """
        ws = await self.get_by_id(workstation_id)
        if ws is None:
            return False
        
        logger.info(f"Deleted workstation: {workstation_id}")
        return True
    
    async def test_connection(self, workstation_id: str) -> Dict[str, Any]:
        """
        Test connection to a workstation.
        
        Attempts to connect to the workstation using its credentials
        and reports the connection status.
        
        Args:
            workstation_id: Workstation identifier
        
        Returns:
            Dict with connection status and diagnostics:
            {
                "connected": bool,
                "workstation_id": str,
                "workstation_name": str,
                "status": "online" | "offline" | "error",
                "response_time_ms": float,
                "error_message": str (optional)
            }
        """
        import time
        import socket
        
        ws = await self.get_or_fail(workstation_id)
        start_time = time.time()
        
        try:
            # Test TCP connection to workstation
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            
            # Try to connect to workstation IP + WinRM port (5985)
            result = sock.connect_ex((ws.ip_address, 5985))
            sock.close()
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if result == 0:
                logger.info(f"Connection test succeeded for {workstation_id}")
                return {
                    "connected": True,
                    "workstation_id": workstation_id,
                    "workstation_name": ws.name,
                    "status": "online",
                    "response_time_ms": response_time_ms
                }
            else:
                logger.warning(f"Connection test failed for {workstation_id}: Connection refused")
                return {
                    "connected": False,
                    "workstation_id": workstation_id,
                    "workstation_name": ws.name,
                    "status": "offline",
                    "response_time_ms": response_time_ms,
                    "error_message": "Connection refused"
                }
                
        except socket.timeout:
            response_time_ms = (time.time() - start_time) * 1000
            logger.warning(f"Connection test timeout for {workstation_id}")
            return {
                "connected": False,
                "workstation_id": workstation_id,
                "workstation_name": ws.name,
                "status": "offline",
                "response_time_ms": response_time_ms,
                "error_message": "Connection timeout"
            }
        except socket.error as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Connection test error for {workstation_id}: {e}")
            return {
                "connected": False,
                "workstation_id": workstation_id,
                "workstation_name": ws.name,
                "status": "error",
                "response_time_ms": response_time_ms,
                "error_message": str(e)
            }
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error during connection test: {e}")
            return {
                "connected": False,
                "workstation_id": workstation_id,
                "workstation_name": ws.name,
                "status": "error",
                "response_time_ms": response_time_ms,
                "error_message": str(e)
            }
    
    def _not_found_exception(self, item_id: str) -> Exception:
        """Create WorkstationNotFoundError."""
        return WorkstationNotFoundError(item_id)
