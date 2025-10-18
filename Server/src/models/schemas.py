"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')


# ============================================================================
# PAGINATION
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1, description="Page number (starting from 1)")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and per_page."""
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    
    @staticmethod
    def create(
        items: List[T],
        total: int,
        page: int,
        per_page: int
    ) -> 'PaginatedResponse[T]':
        """Factory method to create paginated response."""
        pages = (total + per_page - 1) // per_page
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )


# ============================================================================
# WORKSTATION SCHEMAS
# ============================================================================

class WorkstationSchema(BaseModel):
    """Schema for Workstation API."""
    id: str
    name: str
    ip_address: str
    port: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class WorkstationCreateSchema(BaseModel):
    """Schema for creating Workstation."""
    name: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., description="IP address of workstation")
    port: int = Field(default=5985, ge=1, le=65535)
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkstationUpdateSchema(BaseModel):
    """Schema for updating Workstation."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    config: Optional[Dict[str, Any]] = None


# ============================================================================
# EMULATOR SCHEMAS
# ============================================================================

class EmulatorSchema(BaseModel):
    """Schema for Emulator API."""
    id: str
    name: str
    workstation_id: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class EmulatorCreateSchema(BaseModel):
    """Schema for creating Emulator."""
    name: str = Field(..., min_length=1, max_length=255)
    workstation_id: str = Field(..., description="ID of workstation")
    config: Dict[str, Any] = Field(default_factory=dict)


class EmulatorUpdateSchema(BaseModel):
    """Schema for updating Emulator."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    config: Optional[Dict[str, Any]] = None


# ============================================================================
# OPERATION RESULT
# ============================================================================

class OperationResultSchema(BaseModel):
    """Schema for operation result."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthCheckSchema(BaseModel):
    """Schema for health check response."""
    status: str
    message: str
    timestamp: datetime
    version: str
