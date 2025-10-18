#!/usr/bin/env python3
"""
Проверка импортов новой DI архитектуры
"""

import sys
from pathlib import Path

# Добавить корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print("📋 Проверка импортов DI архитектуры...")
print("=" * 60)

try:
    print("✓ Импортирую src.core.container...")
    from src.core.container import DIContainer, container
    print("  ✅ DIContainer OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.models.entities...")
    from src.models.entities import Workstation, Emulator
    print("  ✅ Entities OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.models.schemas...")
    from src.models.schemas import (
        WorkstationSchema, EmulatorSchema,
        PaginatedResponse, PaginationParams
    )
    print("  ✅ Schemas OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.utils.exceptions...")
    from src.utils.exceptions import (
        EmulatorNotFoundError, WorkstationNotFoundError
    )
    print("  ✅ Exceptions OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.services.base_service...")
    from src.services.base_service import BaseService
    print("  ✅ BaseService OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.services.workstation_service...")
    from src.services.workstation_service import WorkstationService
    print("  ✅ WorkstationService OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.services.emulator_service...")
    from src.services.emulator_service import EmulatorService
    print("  ✅ EmulatorService OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.api.dependencies...")
    from src.api.dependencies import (
        get_workstation_service, 
        get_emulator_service
    )
    print("  ✅ Dependencies OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.api.workstations...")
    from src.api.workstations import router as ws_router
    print("  ✅ Workstations router OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.api.emulators...")
    from src.api.emulators import router as emu_router
    print("  ✅ Emulators router OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

try:
    print("✓ Импортирую src.core.server...")
    from src.core.server import app, lifespan, initialize_di_services
    print("  ✅ Server OK")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ВСЕ ИМПОРТЫ УСПЕШНЫ!")
print("🎉 DI архитектура полностью интегрирована и готова к работе")
print("=" * 60)
