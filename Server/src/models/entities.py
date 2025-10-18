"""Domain entities for the application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class WorkstationStatus(str, Enum):
    """Workstation status enum."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class EmulatorStatus(str, Enum):
    """Emulator status enum."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class Workstation:
    """
    Domain entity for Workstation.
    
    Represents a remote workstation that can manage emulators.
    """
    id: str
    name: str
    ip_address: str
    port: int
    status: WorkstationStatus = WorkstationStatus.OFFLINE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure datetime fields are set."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'port': self.port,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'config': self.config,
        }


@dataclass
class Emulator:
    """
    Domain entity for Emulator.
    
    Represents an emulator instance running on a workstation.
    """
    id: str
    name: str
    workstation_id: str
    status: EmulatorStatus = EmulatorStatus.STOPPED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure datetime fields are set."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'workstation_id': self.workstation_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'config': self.config,
        }


@dataclass
class OperationResult:
    """Result of an operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
        }
