"""
API модули для LDPlayer Management System.

Содержит разделенные роуты для различных endpoint'ов.
"""

from .workstations import router as workstations_router
from .emulators import router as emulators_router
from .operations import router as operations_router
from .health import router as health_router

__all__ = [
    'workstations_router',
    'emulators_router',
    'operations_router',
    'health_router'
]
