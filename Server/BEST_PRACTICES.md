# 📚 Best Practices - LDPlayer Management System

**Версия:** 1.0  
**Дата:** 2025-10-19  
**Статус:** Production-Ready

---

## 📑 Содержание

1. [Code Organization](#code-organization)
2. [Input Validation](#input-validation)
3. [Error Handling](#error-handling)
4. [Logging](#logging)
5. [Security](#security)
6. [Performance](#performance)
7. [Testing](#testing)
8. [API Design](#api-design)

---

## Code Organization

### ✅ DO: Структурируйте код правильно

```
src/
├── api/              # API маршруты (endpoint'ы)
├── core/             # Ядро (models, config, server)
├── services/         # Бизнес-логика
├── remote/           # Удалённое управление (managers)
└── utils/            # Утилиты (validators, constants, logger)
```

### ✅ DO: Один endpoint - один файл модуля

```python
# ✅ ПРАВИЛЬНО - каждый модуль отвечает за один ресурс
src/api/
├── workstations.py   # Все endpoints для рабочих станций
├── emulators.py      # Все endpoints для эмуляторов
├── operations.py     # Все endpoints для операций
├── auth_routes.py    # Все endpoints для аутентификации
└── health.py         # Endpoints для здоровья

# ❌ НЕПРАВИЛЬНО - смешали всё в одном файле
src/api/
└── all_routes.py     # 1000+ строк кода - невозможно искать!
```

### ✅ DO: Используйте Dependency Injection

```python
# ✅ ПРАВИЛЬНО - зависимости через DI
@router.get("")
async def get_emulators(
    service: EmulatorService = Depends(get_emulator_service),
    config: SystemConfig = Depends(get_system_config)
):
    emulators = await service.get_all()
    return {"data": emulators}

# ❌ НЕПРАВИЛЬНО - жёсткие зависимости
service = EmulatorService()  # Hard dependency!
config = load_config()        # Hard dependency!
```

### ✅ DO: Отделяйте бизнес-логику от API

```python
# ✅ ПРАВИЛЬНО - логика в services
# src/services/emulator_service.py
class EmulatorService:
    async def create(self, data: Dict) -> Emulator:
        # Валидация
        # Обработка ошибок
        # Создание объекта
        # Сохранение
        pass

# src/api/emulators.py
@router.post("")
async def create_emulator(data: EmulatorCreateRequest):
    return await service.create(data.dict())

# ❌ НЕПРАВИЛЬНО - логика в endpoint'е
@router.post("")
async def create_emulator(data: EmulatorCreateRequest):
    # Валидация
    # Обработка ошибок
    # Создание объекта
    # Сохранение
    # ← 50+ строк в одном endpoint'е!
```

---

## Input Validation

### ✅ DO: Валидируйте на входе

```python
from src.utils.validators import validate_pagination_params, validate_workstation_name

# ✅ ПРАВИЛЬНО - валидируем сразу
@router.get("")
async def get_workstations(skip: int = 0, limit: int = 100):
    skip, limit = validate_pagination_params(skip, limit)
    
    ws = await service.get_all(limit=skip+limit)
    return {"data": ws[skip:skip+limit]}

# ❌ НЕПРАВИЛЬНО - валидируем слишком поздно
@router.get("")
async def get_workstations(skip: int = 0, limit: int = 100):
    ws = await service.get_all(limit=skip+limit)  # skip может быть -5!
    return {"data": ws[skip:skip+limit]}
```

### ✅ DO: Используйте Pydantic models

```python
from pydantic import BaseModel, Field

# ✅ ПРАВИЛЬНО - используем Pydantic
class WorkstationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: str = Field(..., pattern=r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    port: int = Field(default=5555, ge=1, le=65535)

@router.post("")
async def create_workstation(data: WorkstationCreate):
    # data уже валидирован FastAPI/Pydantic!
    await service.create(data.dict())

# ❌ НЕПРАВИЛЬНО - какой тип данных? Что может быть невалидным?
@router.post("")
async def create_workstation(name, ip_address, port):
    await service.create({"name": name, "ip_address": ip_address, "port": port})
```

### ✅ DO: Валидируйте бизнес-логику

```python
# ✅ ПРАВИЛЬНО - комбинируем Pydantic + custom validators
from src.utils.validators import validate_emulator_config

class EmulatorCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    config: Dict[str, Any]

@router.post("")
async def create_emulator(request: EmulatorCreateRequest):
    # Pydantic уже проверил типы
    
    # Теперь проверим бизнес-логику
    is_valid, error = validate_emulator_config(request.config)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Теперь можно безопасно создавать
    await service.create(request.dict())
```

### ❌ DON'T: Не пропускайте валидацию

```python
# ❌ НЕПРАВИЛЬНО - пропущена валидация
@router.post("")
async def create_workstation(request: WorkstationCreate):
    # Что если config невалидна? Что если name содержит спецсимволы?
    return await service.create(request.dict())
```

### ❌ DON'T: Не используйте try-except для валидации

```python
# ❌ НЕПРАВИЛЬНО - слишком общее
try:
    ws = await service.create(data.dict())
except:
    return {"error": "Something went wrong"}

# ✅ ПРАВИЛЬНО - специфичная валидация
is_valid, error = validate_workstation_name(data.name)
if not is_valid:
    raise HTTPException(status_code=400, detail=error)

# И обработка конкретных исключений
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except ConnectionError as e:
    raise HTTPException(status_code=503, detail="Service unavailable")
```

---

## Error Handling

### ✅ DO: Используйте Constants для сообщений об ошибках

```python
from src.utils.constants import ErrorMessage
from fastapi import HTTPException, status

# ✅ ПРАВИЛЬНО - стандартные сообщения
if not token:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ErrorMessage.TOKEN_EXPIRED
    )

if not workstation:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorMessage.NOT_FOUND.format(resource="Workstation")
    )

# ❌ НЕПРАВИЛЬНО - случайные строки
raise HTTPException(status_code=401, detail="Bad token")
raise HTTPException(status_code=404, detail="WS not found")
```

### ✅ DO: Используйте правильные HTTP статус коды

```python
from fastapi import status

# ✅ ПРАВИЛЬНО - правильные коды
200 OK                      # Успешно
201 CREATED                 # Создано
202 ACCEPTED                # Принято (async operation)
204 NO CONTENT              # Успешно, но нет содержимого
400 BAD_REQUEST             # Невалидные входные данные
401 UNAUTHORIZED            # Нет аутентификации
403 FORBIDDEN               # Нет разрешения
404 NOT_FOUND               # Ресурс не найден
409 CONFLICT                # Конфликт (уже существует)
422 UNPROCESSABLE_ENTITY    # Невалидная сущность (Pydantic)
429 TOO_MANY_REQUESTS       # Rate limit
500 INTERNAL_SERVER_ERROR   # Внутренняя ошибка сервера
503 SERVICE_UNAVAILABLE     # Сервис недоступен

# ❌ НЕПРАВИЛЬНО - неправильные коды
raise HTTPException(status_code=500, detail="Invalid input")  # Should be 400
raise HTTPException(status_code=200, detail="Not found")      # Should be 404
raise HTTPException(status_code=403, detail="Database error") # Should be 500
```

### ✅ DO: Логируйте ошибки

```python
from src.utils.logger import get_logger, LogCategory

logger = get_logger(LogCategory.API)

# ✅ ПРАВИЛЬНО - логируем ошибки
try:
    result = await service.create(data.dict())
except ValueError as e:
    logger.log_error(f"Invalid data: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except ConnectionError as e:
    logger.log_error(f"Connection failed: {e}")
    raise HTTPException(status_code=503, detail="Service unavailable")

# ❌ НЕПРАВИЛЬНО - молчим при ошибках
try:
    result = await service.create(data.dict())
except:
    raise HTTPException(status_code=500, detail="Error")  # Что произошло?
```

### ✅ DO: Структурируйте response

```python
from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

# ✅ ПРАВИЛЬНО - структурированный ответ
return APIResponse(
    success=True,
    message="Workstation created",
    data={"workstation_id": ws.id}
)

return APIResponse(
    success=False,
    message="Invalid data",
    error="Name cannot be empty"
)
```

---

## Logging

### ✅ DO: Логируйте важные события

```python
from src.utils.logger import get_logger, LogCategory

logger = get_logger(LogCategory.API)

# ✅ ПРАВИЛЬНО - логируем события
@router.post("")
async def create_workstation(data: WorkstationCreate):
    logger.log_system_event(
        "Creating workstation",
        {"name": data.name, "ip": data.ip_address}
    )
    
    try:
        ws = await service.create(data.dict())
        logger.log_system_event(
            "Workstation created successfully",
            {"workstation_id": ws.id}
        )
        return APIResponse(success=True, data={"workstation_id": ws.id})
    except Exception as e:
        logger.log_error(f"Failed to create workstation: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

### ✅ DO: Используйте правильный log level

```python
logger = get_logger(LogCategory.API)

# ✅ ПРАВИЛЬНО - правильные уровни
logger.log_operation("Starting operation", {})       # INFO
logger.log_system_event("System event", {})          # INFO
logger.log_error("Something went wrong", error)      # ERROR
logger.log_debug("Debug info: " + str(var))          # DEBUG (if LOG_LEVEL=DEBUG)

# ❌ НЕПРАВИЛЬНО
print(f"Starting operation")  # Не видно в логах!
console.log("Debug info")     # Смешиваем с stdout!
```

### ❌ DON'T: Не логируйте чувствительные данные

```python
# ❌ НЕПРАВИЛЬНО - логируем пароли!
logger.log_operation("Login", {"username": user, "password": password})

# ✅ ПРАВИЛЬНО - логируем только нужное
logger.log_operation("Login", {"username": user, "success": True})
```

---

## Security

### ✅ DO: Требуйте аутентификацию

```python
from src.api.dependencies import verify_token

# ✅ ПРАВИЛЬНО - требуем токен
@router.post("")
async def create_workstation(
    data: WorkstationCreate,
    current_user: str = Depends(verify_token)  # ← ОБЯЗАТЕЛЬНО!
):
    return await service.create(data.dict())

# ❌ НЕПРАВИЛЬНО - нет аутентификации
@router.post("")
async def create_workstation(data: WorkstationCreate):
    return await service.create(data.dict())  # Кто угодно может создавать!
```

### ✅ DO: Проверяйте разрешения

```python
from src.utils.auth import require_role
from src.core.models import UserRole

# ✅ ПРАВИЛЬНО - требуем роль
@router.post("")
async def create_workstation(
    data: WorkstationCreate,
    current_user: str = Depends(verify_token),
    role: UserRole = Depends(require_role([UserRole.ADMIN]))
):
    return await service.create(data.dict())

# ❌ НЕПРАВИЛЬНО - не проверяем роль
@router.post("")
async def create_workstation(
    data: WorkstationCreate,
    current_user: str = Depends(verify_token)  # Viewer может создавать!
):
    return await service.create(data.dict())
```

### ✅ DO: Используйте HTTPS в production

```python
# ✅ ПРАВИЛЬНО - SSL в production
if ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    ssl_keyfile = "/etc/ssl/private/key.pem"
    ssl_certfile = "/etc/ssl/certs/cert.pem"
    # Запуск с SSL

# ❌ НЕПРАВИЛЬНО - HTTP в production
# Python не позволит, но требует явного решения!
```

### ✅ DO: Не логируйте чувствительные данные

```python
# ✅ ПРАВИЛЬНО
logger.log_operation("User login", {"username": username})

# ❌ НЕПРАВИЛЬНО
logger.log_operation("User login", {"username": username, "password": password})
logger.log_operation("Config loaded", config)  # Может содержать secrets!
```

### ✅ DO: Валидируйте все входные данные

```python
# ✅ ПРАВИЛЬНО - всё валидировано
skip, limit = validate_pagination_params(skip, limit)
is_valid, error = validate_workstation_name(name)

# ❌ НЕПРАВИЛЬНО - пропущена валидация
name = request.name  # Может быть SQL injection!
config = request.config  # Может быть слишком большим!
```

---

## Performance

### ✅ DO: Используйте async/await везде

```python
# ✅ ПРАВИЛЬНО - асинхронно
async def get_emulators(service: EmulatorService = Depends(get_emulator_service)):
    emulators = await service.get_all()  # async operation
    return {"data": emulators}

# ❌ НЕПРАВИЛЬНО - синхронно (блокирует)
def get_emulators(service: EmulatorService = Depends(get_emulator_service)):
    emulators = service.get_all()  # Блокирует весь сервер!
    return {"data": emulators}
```

### ✅ DO: Используйте пагинацию для больших списков

```python
# ✅ ПРАВИЛЬНО - пагинация
@router.get("")
async def get_emulators(skip: int = 0, limit: int = 50):
    skip, limit = validate_pagination_params(skip, limit)
    emulators = await service.get_all(limit=10000)  # Получи все
    return {"data": emulators[skip:skip+limit]}     # Верни часть

# ❌ НЕПРАВИЛЬНО - без пагинации
@router.get("")
async def get_emulators():
    return {"data": await service.get_all()}  # 10000 объектов! 10MB!
```

### ✅ DO: Кэшируйте часто запрашиваемые данные

```python
from src.utils.cache import get_cache_stats, invalidate_cache

# ✅ ПРАВИЛЬНО - используем кэш
@router.get("/config")
async def get_config(service=Depends(get_config_service)):
    # service внутри использует кэш на 5 минут
    return await service.get_config()

# При обновлении
@router.put("/config")
async def update_config(new_config):
    result = await service.update_config(new_config)
    invalidate_cache()  # Очищаем кэш
    return result
```

---

## Testing

### ✅ DO: Пишите unit тесты

```python
import pytest
from unittest.mock import AsyncMock, patch

# ✅ ПРАВИЛЬНО - модульное тестирование
@pytest.mark.asyncio
async def test_get_emulators(test_client):
    response = await test_client.get("/api/emulators")
    assert response.status_code == 200
    assert "data" in response.json()

@pytest.mark.asyncio
async def test_create_emulator_validation(test_client):
    # Тест с невалидными данными
    response = await test_client.post("/api/emulators", json={
        "name": "",  # ← пусто
        "config": {"width": 100}  # ← невалидно
    })
    assert response.status_code == 400
```

### ✅ DO: Тестируйте обработку ошибок

```python
# ✅ ПРАВИЛЬНО - тестируем ошибки
@pytest.mark.asyncio
async def test_create_workstation_invalid_ip(test_client):
    response = await test_client.post("/api/workstations", json={
        "name": "ws",
        "ip_address": "999.999.999.999",  # ← невалидный IP
    })
    assert response.status_code == 400
    assert "Invalid IP" in response.json()["detail"]
```

### ❌ DON'T: Не пишите только happy path тесты

```python
# ❌ НЕПРАВИЛЬНО - только успешные случаи
@pytest.mark.asyncio
async def test_create_workstation(test_client):
    response = await test_client.post("/api/workstations", json={
        "name": "ws",
        "ip_address": "192.168.1.1"
    })
    assert response.status_code == 201

# ✅ ПРАВИЛЬНО - тестируем всё
@pytest.mark.asyncio
async def test_create_workstation_success(test_client):
    # Happy path
    response = await test_client.post(...)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_workstation_invalid_name(test_client):
    # Invalid input
    response = await test_client.post(..., json={"name": ""})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_workstation_unauthorized(test_client):
    # Missing auth
    response = await test_client.post(..., headers={})
    assert response.status_code == 401
```

---

## API Design

### ✅ DO: Используйте правильные HTTP методы

```python
# ✅ ПРАВИЛЬНО - правильные методы
GET    /api/emulators              # Получить список
GET    /api/emulators/{id}         # Получить один
POST   /api/emulators              # Создать
PUT    /api/emulators/{id}         # Обновить полностью
PATCH  /api/emulators/{id}         # Обновить частично
DELETE /api/emulators/{id}         # Удалить

# ❌ НЕПРАВИЛЬНО - неправильные методы
GET    /api/emulators/create       # POST!
POST   /api/emulators/get          # GET!
GET    /api/emulators/delete       # DELETE!
```

### ✅ DO: Используйте правильные paths

```python
# ✅ ПРАВИЛЬНО - иерархические пути
GET    /api/workstations                    # Список рабочих станций
GET    /api/workstations/{ws_id}            # Одна рабочая станция
GET    /api/workstations/{ws_id}/emulators  # Эмуляторы на станции
POST   /api/workstations/{ws_id}/emulators  # Создать эмулятор на станции

# ❌ НЕПРАВИЛЬНО - плоские пути
GET    /api/all_workstations
GET    /api/workstation_by_id?id=123
GET    /api/emulators_on_workstation?ws_id=123
POST   /api/create_emulator_on_workstation?ws_id=123
```

### ✅ DO: Версионируйте API

```python
# ✅ ПРАВИЛЬНО - версионирование
GET    /api/v1/emulators
GET    /api/v2/emulators  # Новая версия с изменениями

# Поддерживайте старую версию для совместимости
```

### ✅ DO: Документируйте API

```python
# ✅ ПРАВИЛЬНО - документируем endpoint
@router.get("")
async def get_emulators(skip: int = 0, limit: int = 100):
    """
    Получить список эмуляторов с пагинацией.
    
    **Параметры:**
    - skip: Сколько пропустить (default: 0)
    - limit: Максимум результатов (default: 100, max: 1000)
    
    **Возвращает:**
    ```json
    {
        "data": [...],
        "pagination": {
            "total": 100,
            "skip": 0,
            "limit": 50,
            "returned": 50,
            "has_more": true
        }
    }
    ```
    
    **Примеры:**
    - GET /api/emulators
    - GET /api/emulators?skip=50&limit=25
    """
    skip, limit = validate_pagination_params(skip, limit)
    # ...
```

---

## Чек-лист перед production

- [ ] Все inputs валидируются
- [ ] Все errors обрабатываются
- [ ] Все sensitive data защищена
- [ ] Все endpoints требуют аутентификацию
- [ ] Все endpoints проверяют разрешения (roles)
- [ ] Все логирование на месте
- [ ] Все тесты passing (100%)
- [ ] Используется HTTPS
- [ ] CORS правильно настроен
- [ ] Rate limiting включен
- [ ] Мониторинг включен
- [ ] Backup стратегия есть

---

**Версия документации:** 1.0  
**Дата обновления:** 2025-10-19  
**Статус:** ✅ Production Ready
