"""Base service class with common functionality."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any, Tuple

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """
    Abstract base service class.
    
    Provides common methods for all services:
    - get_all: Get all items with pagination
    - get_by_id: Get item by ID or raise error
    - create: Create new item
    - update: Update existing item
    - delete: Delete item
    """
    
    def __init__(self):
        """Initialize base service."""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[T], int]:
        """
        Get all items with pagination.
        
        Args:
            limit: Number of items to return
            offset: Offset for pagination
        
        Returns:
            Tuple of (items, total_count)
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[T]:
        """
        Get item by ID.
        
        Args:
            item_id: Item identifier
        
        Returns:
            Item or None if not found
        """
        pass
    
    async def get_or_fail(self, item_id: str) -> T:
        """
        Get item by ID or raise error.
        
        Args:
            item_id: Item identifier
        
        Returns:
            Item if found
        
        Raises:
            NotFoundError: If item not found
        """
        item = await self.get_by_id(item_id)
        if item is None:
            raise self._not_found_exception(item_id)
        return item
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """
        Create new item.
        
        Args:
            data: Item data
        
        Returns:
            Created item
        """
        pass
    
    @abstractmethod
    async def update(self, item_id: str, data: Dict[str, Any]) -> T:
        """
        Update existing item.
        
        Args:
            item_id: Item identifier
            data: Update data
        
        Returns:
            Updated item
        
        Raises:
            NotFoundError: If item not found
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """
        Delete item.
        
        Args:
            item_id: Item identifier
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def _not_found_exception(self, item_id: str) -> Exception:
        """
        Create "not found" exception for this service.
        
        Args:
            item_id: Item identifier
        
        Returns:
            Exception instance
        """
        pass
