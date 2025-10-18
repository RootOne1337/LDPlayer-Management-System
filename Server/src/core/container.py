"""Dependency Injection Container for managing service instances."""

from typing import Dict, Callable, Any, Optional, TypeVar, Generic
import threading

T = TypeVar('T')


class DIContainer:
    """
    Simple Dependency Injection Container.
    
    Supports:
    - Singleton registration (register)
    - Factory registration (register_factory)
    - Service retrieval (get)
    - Thread-safe access
    """
    
    def __init__(self):
        """Initialize the DI container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._lock = threading.RLock()
    
    def register(self, name: str, service: Any) -> None:
        """
        Register a singleton service.
        
        Args:
            name: Service name/identifier
            service: Service instance
        
        Example:
            container.register('workstation_manager', manager_instance)
        """
        with self._lock:
            self._services[name] = service
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory function that creates new instances.
        
        Args:
            name: Service name/identifier
            factory: Callable that returns service instance
        
        Example:
            container.register_factory('config', lambda: Config())
        """
        with self._lock:
            self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """
        Get a registered service.
        
        Args:
            name: Service name/identifier
        
        Returns:
            Service instance (singleton or factory result)
        
        Raises:
            KeyError: If service not registered
        """
        with self._lock:
            # Check singletons first
            if name in self._services:
                return self._services[name]
            
            # Check factories
            if name in self._factories:
                return self._factories[name]()
            
            # Not found
            raise KeyError(f"Service '{name}' not registered in DI container")
    
    def has(self, name: str) -> bool:
        """
        Check if service is registered.
        
        Args:
            name: Service name/identifier
        
        Returns:
            True if service is registered
        """
        with self._lock:
            return name in self._services or name in self._factories
    
    def clear(self) -> None:
        """Clear all registered services."""
        with self._lock:
            self._services.clear()
            self._factories.clear()


# Global container instance
container = DIContainer()


def get_container() -> DIContainer:
    """Get the global DI container instance."""
    return container
