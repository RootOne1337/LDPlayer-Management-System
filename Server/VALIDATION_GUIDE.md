# 📘 Validation Guide - LDPlayer Management System

**Версия:** 1.0  
**Дата:** 2025-10-19  
**Статус:** Production-Ready

---

## 📑 Содержание

1. [Введение](#введение)
2. [Архитектура валидации](#архитектура-валидации)
3. [Использование Validators](#использование-validators)
4. [Использование Constants](#использование-constants)
5. [Примеры API запросов](#примеры-api-запросов)
6. [Обработка ошибок](#обработка-ошибок)
7. [Best Practices](#best-practices)

---

## Введение

Этот гайд объясняет как использовать систему валидации входных данных в LDPlayer Management System. Валидация применяется ко **всем API endpoints** для обеспечения безопасности и консистентности данных.

### Ключевые компоненты

- **`validators.py`** - 15+ функций для валидации входных данных
- **`constants.py`** - 9 классов с константами (statuses, types, error messages)
- **API Endpoints** - все используют валидацию перед обработкой

---

## Архитектура валидации

### Flow диаграмма

```
Client Request
     ↓
API Endpoint
     ↓
Pydantic Validation (BaseModel)
     ↓
Custom Validators (validators.py functions)
     ↓
Constants Checking (constants.py classes)
     ↓
Business Logic
     ↓
ErrorMessage Response (constants.ErrorMessage)
     ↓
Client Response
```

### Уровни валидации

1. **Pydantic Level** - типы данных (FastAPI автоматически)
2. **Custom Level** - бизнес-логика (validators.py функции)
3. **Constants Level** - перечисления (constants.py enums)
4. **Response Level** - стандартные сообщения об ошибках

---

## Использование Validators

### 1. Валидация пагинации

**Проблема:** Клиент может отправить negative или очень большие значения

```python
from src.utils.validators import validate_pagination_params

# ❌ НЕБЕЗОПАСНО - может быть DoS атака
skip = -5
limit = 1000000

# ✅ БЕЗОПАСНО - используем валидатор
skip, limit = validate_pagination_params(skip, limit)
# Результат: skip=0, limit=1000 (максимум)
```

**Примеры:**

```python
# Пример 1: Отрицательные значения
validate_pagination_params(-10, 50)
# → (0, 50)

# Пример 2: Очень большой лимит
validate_pagination_params(0, 5000)
# → (0, 1000) ← лимит обрезан до 1000

# Пример 3: None значения
validate_pagination_params(None, None)
# → (0, 100) ← значения по умолчанию
```

**Использование в API:**

```python
@router.get("")
async def get_workstations(
    skip: int = 0,
    limit: int = 100,
    service: WorkstationService = Depends(get_workstation_service)
) -> Dict[str, Any]:
    # Валидируем пагинацию
    skip, limit = validate_pagination_params(skip, limit)
    
    # Получаем данные
    workstations = await service.get_all(limit=1000, offset=0)
    
    # Применяем пагинацию
    total = len(workstations)
    paginated = workstations[skip : skip + limit]
    
    return {
        "data": paginated,
        "pagination": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "returned": len(paginated),
            "has_more": (skip + limit) < total
        }
    }
```

### 2. Валидация имён

**Проблема:** Имя может содержать недопустимые символы или быть слишком длинным

```python
from src.utils.validators import validate_workstation_name, validate_emulator_name

# ✅ ВАЛИДНО
valid, error = validate_workstation_name("my-workstation-1")
# → (True, None)

# ❌ НЕВАЛИДНО - спецсимволы
valid, error = validate_workstation_name("my@workstation!")
# → (False, "Name can only contain letters, numbers, underscores, and hyphens")

# ❌ НЕВАЛИДНО - пусто
valid, error = validate_workstation_name("")
# → (False, "Workstation name cannot be empty")

# ❌ НЕВАЛИДНО - слишком длинно
valid, error = validate_workstation_name("a" * 300)
# → (False, "Name cannot exceed 255 characters")
```

**Использование в API:**

```python
@router.post("/workstations")
async def create_workstation(
    name: str = Field(..., min_length=1),
    service: WorkstationService = Depends(get_workstation_service),
    current_user: str = Depends(verify_token)
):
    # Валидируем имя
    is_valid, error_msg = validate_workstation_name(name)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Создаём рабочую станцию
    ws = await service.create({"name": name})
    return APIResponse(success=True, data={"workstation_id": ws.id})
```

### 3. Валидация конфигурации

**Проблема:** Конфигурация может быть невалидна (неправильные типы, диапазоны)

```python
from src.utils.validators import validate_emulator_config

# ✅ ВАЛИДНО
config = {"width": 1280, "height": 720, "dpi": 240}
valid, error = validate_emulator_config(config)
# → (True, None)

# ❌ НЕВАЛИДНО - отрицательное разрешение
config = {"width": -1280, "height": 720, "dpi": 240}
valid, error = validate_emulator_config(config)
# → (False, "Width, height, and DPI must be positive numbers")

# ❌ НЕВАЛИДНО - слишком малое разрешение
config = {"width": 100, "height": 50, "dpi": 240}
valid, error = validate_emulator_config(config)
# → (False, "Minimum resolution is 320x240")

# ❌ НЕВАЛИДНО - DPI вне диапазона
config = {"width": 1280, "height": 720, "dpi": 1000}
valid, error = validate_emulator_config(config)
# → (False, "DPI must be between 72 and 600")
```

### 4. Валидация IP адреса

**Проблема:** IP адрес может быть невалидным

```python
from src.utils.validators import validate_ip_address

# ✅ ВАЛИДНО
valid, error = validate_ip_address("192.168.1.100")
# → (True, None)

# ❌ НЕВАЛИДНО - октет > 255
valid, error = validate_ip_address("192.168.1.300")
# → (False, "Invalid IP address: octets must be 0-255")

# ❌ НЕВАЛИДНО - неправильный формат
valid, error = validate_ip_address("192.168.1")
# → (False, "Invalid IP address format")
```

### 5. Валидация порта

**Проблема:** Порт может быть вне диапазона (1-65535)

```python
from src.utils.validators import validate_port

# ✅ ВАЛИДНО
valid, error = validate_port(5555)
# → (True, None)

# ❌ НЕВАЛИДНО - порт 0
valid, error = validate_port(0)
# → (False, "Port must be between 1 and 65535")

# ❌ НЕВАЛИДНО - порт > 65535
valid, error = validate_port(70000)
# → (False, "Port must be between 1 and 65535")
```

---

## Использование Constants

### 1. Statuses (Перечисления статусов)

```python
from src.utils.constants import EmulatorStatus, WorkstationStatus, OperationStatus

# ✅ ВМЕСТО MAGIC STRINGS
emulator_status = EmulatorStatus.RUNNING
# → "RUNNING"

workstation_status = WorkstationStatus.ONLINE
# → "ONLINE"

operation_status = OperationStatus.SUCCESS
# → "SUCCESS"

# ❌ НЕПРАВИЛЬНО - magic string
status = "running"  # Может быть опечатка!
```

### 2. Error Messages (Стандартные сообщения об ошибках)

```python
from src.utils.constants import ErrorMessage
from fastapi import HTTPException, status

# ✅ ПРАВИЛЬНО - используем constants
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ErrorMessage.INVALID_CREDENTIALS
    )

# ✅ ПРАВИЛЬНО - с форматированием
if not workstation:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorMessage.NOT_FOUND.format(resource="Workstation")
    )

# ✅ ПРАВИЛЬНО - с причиной
if operation_failed:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorMessage.OPERATION_FAILED.format(reason="Network timeout")
    )
```

### 3. API Defaults (Значения по умолчанию)

```python
from src.utils.constants import APIDefaults

# ✅ ПРАВИЛЬНО - используем constants
DEFAULT_LIMIT = APIDefaults.DEFAULT_LIMIT  # 100
MAX_LIMIT = APIDefaults.MAX_LIMIT  # 1000
TIMEOUT = APIDefaults.OPERATION_TIMEOUT_SECONDS  # 300 сек

# Использование в коде
@router.get("/items")
async def get_items(limit: int = APIDefaults.DEFAULT_LIMIT):
    if limit > APIDefaults.MAX_LIMIT:
        limit = APIDefaults.MAX_LIMIT
    # ...
```

### 4. Validation Rules (Правила валидации)

```python
from src.utils.constants import ValidationRules

# ✅ ПРАВИЛЬНО - используем constants
MIN_NAME = ValidationRules.MIN_NAME_LENGTH  # 1
MAX_NAME = ValidationRules.MAX_NAME_LENGTH  # 255
NAME_PATTERN = ValidationRules.NAME_PATTERN  # regex

# Использование в коде
if len(name) < ValidationRules.MIN_NAME_LENGTH:
    raise ValueError("Name too short")

if not re.match(ValidationRules.NAME_PATTERN, name):
    raise ValueError("Invalid name format")
```

---

## Примеры API запросов

### 1. Login (Аутентификация)

**cURL:**
```bash
curl -X POST http://127.0.0.1:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:8001/auth/login",
    json={"username": "admin", "password": "admin"}
)
token = response.json()["data"]["access_token"]
```

**JavaScript:**
```javascript
const response = await fetch("http://127.0.0.1:8001/auth/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username: "admin", password: "admin"})
});
const data = await response.json();
const token = data.data.access_token;
```

### 2. Get Emulators (Пагинация)

**cURL:**
```bash
# Безопасный запрос с пагинацией
curl -X GET "http://127.0.0.1:8001/api/emulators?skip=0&limit=50" \
  -H "Authorization: Bearer TOKEN"

# Попытка DoS атаки (будет исправлена валидатором)
curl -X GET "http://127.0.0.1:8001/api/emulators?skip=-5&limit=1000000" \
  -H "Authorization: Bearer TOKEN"
# → Будет нормализовано до skip=0, limit=1000
```

**Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# ✅ БЕЗОПАСНО
response = requests.get(
    "http://127.0.0.1:8001/api/emulators",
    params={"skip": 0, "limit": 50},
    headers=headers
)
emulators = response.json()["data"]

# ✅ ДАЖЕ С БОЛЬШИМИ ЗНАЧЕНИЯМИ БЕЗОПАСНО
response = requests.get(
    "http://127.0.0.1:8001/api/emulators",
    params={"skip": -5, "limit": 1000000},
    headers=headers
)
# → Будет нормализовано, атака блокирована
```

**JavaScript:**
```javascript
const token = "YOUR_ACCESS_TOKEN";
const response = await fetch(
    "http://127.0.0.1:8001/api/emulators?skip=0&limit=50",
    {headers: {"Authorization": `Bearer ${token}`}}
);
const data = await response.json();
const emulators = data.data;
```

### 3. Create Workstation (Валидация имени)

**cURL:**
```bash
curl -X POST http://127.0.0.1:8001/api/workstations \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "ws-1",
    "name": "my-workstation",
    "ip_address": "192.168.1.100",
    "username": "administrator",
    "password": "password123",
    "ldplayer_path": "C:\\LDPlayer\\LDPlayer9.0"
  }'
```

**Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# ✅ ВАЛИДНЫЕ ДАННЫЕ
data = {
    "id": "ws-1",
    "name": "my-workstation",
    "ip_address": "192.168.1.100",
    "username": "administrator",
    "password": "password123",
    "ldplayer_path": "C:\\LDPlayer\\LDPlayer9.0"
}

response = requests.post(
    "http://127.0.0.1:8001/api/workstations",
    json=data,
    headers=headers
)

if response.status_code == 201:
    workstation = response.json()["data"]
    print(f"Created: {workstation['workstation_id']}")
else:
    error = response.json()["detail"]
    print(f"Error: {error}")
```

### 4. Create Emulator (Валидация конфигурации)

**cURL:**
```bash
curl -X POST http://127.0.0.1:8001/api/emulators \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workstation_id": "ws-1",
    "name": "my-emulator",
    "config": {
      "width": 1280,
      "height": 720,
      "dpi": 240
    }
  }'
```

**Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# ✅ ВАЛИДНАЯ КОНФИГУРАЦИЯ
data = {
    "workstation_id": "ws-1",
    "name": "my-emulator",
    "config": {
        "width": 1280,
        "height": 720,
        "dpi": 240
    }
}

response = requests.post(
    "http://127.0.0.1:8001/api/emulators",
    json=data,
    headers=headers
)

if response.status_code == 202:  # Accepted for async operation
    operation = response.json()["data"]
    print(f"Operation started: {operation['operation_id']}")
else:
    error = response.json()["detail"]
    print(f"Error: {error}")

# ❌ НЕВАЛИДНАЯ КОНФИГУРАЦИЯ
invalid_data = {
    "workstation_id": "ws-1",
    "name": "my-emulator",
    "config": {
        "width": 100,  # ← Слишком мало (минимум 320)
        "height": 50,  # ← Слишком мало (минимум 240)
        "dpi": 1000    # ← Слишком много (максимум 600)
    }
}

response = requests.post(
    "http://127.0.0.1:8001/api/emulators",
    json=invalid_data,
    headers=headers
)
# → 400 Bad Request: "Invalid configuration"
```

---

## Обработка ошибок

### Response Format

**✅ Успешный ответ:**
```json
{
    "success": true,
    "message": "Operation successful",
    "data": {
        "workstation_id": "ws-1"
    }
}
```

**❌ Ошибка валидации:**
```json
{
    "success": false,
    "detail": "Name can only contain letters, numbers, underscores, and hyphens"
}
```

**❌ Ошибка аутентификации:**
```json
{
    "detail": "Invalid username or password"
}
```

**❌ Ошибка авторизации:**
```json
{
    "detail": "Permission denied - insufficient privileges"
}
```

**❌ Resource not found:**
```json
{
    "detail": "Workstation not found"
}
```

### Обработка в коде

**Python:**
```python
import requests
from requests.exceptions import RequestException

token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(
        "http://127.0.0.1:8001/api/emulators",
        params={"skip": 0, "limit": 50},
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        emulators = data["data"]
        print(f"Got {len(emulators)} emulators")
    
    elif response.status_code == 400:
        error = response.json()["detail"]
        print(f"Invalid request: {error}")
    
    elif response.status_code == 401:
        error = response.json()["detail"]
        print(f"Auth failed: {error}")
    
    elif response.status_code == 404:
        error = response.json()["detail"]
        print(f"Not found: {error}")
    
    else:
        print(f"HTTP {response.status_code}: {response.text}")

except RequestException as e:
    print(f"Network error: {e}")
```

**JavaScript:**
```javascript
async function getEmulators(token) {
    try {
        const response = await fetch(
            "http://127.0.0.1:8001/api/emulators?skip=0&limit=50",
            {headers: {"Authorization": `Bearer ${token}`}}
        );
        
        if (response.ok) {
            const data = await response.json();
            console.log(`Got ${data.data.length} emulators`);
        } else if (response.status === 401) {
            const error = await response.json();
            console.error(`Auth failed: ${error.detail}`);
        } else if (response.status === 404) {
            const error = await response.json();
            console.error(`Not found: ${error.detail}`);
        } else {
            console.error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error(`Network error: ${error}`);
    }
}
```

---

## Best Practices

### 1. ✅ ВСЕГДА валидируйте входные данные

```python
# ✅ ПРАВИЛЬНО
is_valid, error = validate_workstation_name(name)
if not is_valid:
    raise HTTPException(status_code=400, detail=error)

# ❌ НЕПРАВИЛЬНО - пропустили валидацию
ws = service.create({"name": name})  # Может быть опасно!
```

### 2. ✅ Используйте Constants вместо magic strings

```python
# ✅ ПРАВИЛЬНО
if status == OperationStatus.SUCCESS:
    print("Operation completed")

# ❌ НЕПРАВИЛЬНО - magic string
if status == "success":
    print("Operation completed")
```

### 3. ✅ Используйте правильные HTTP статус коды

```python
# ✅ ПРАВИЛЬНО
raise HTTPException(status_code=400, detail="Invalid input")  # Bad Request
raise HTTPException(status_code=401, detail="Unauthorized")   # Unauthorized
raise HTTPException(status_code=403, detail="Forbidden")      # Forbidden
raise HTTPException(status_code=404, detail="Not found")      # Not Found
raise HTTPException(status_code=409, detail="Conflict")       # Conflict

# ❌ НЕПРАВИЛЬНО - неправильный статус код
raise HTTPException(status_code=500, detail="Invalid input")  # Should be 400
```

### 4. ✅ Используйте стандартные error messages

```python
# ✅ ПРАВИЛЬНО
detail=ErrorMessage.INVALID_CREDENTIALS
detail=ErrorMessage.NOT_FOUND.format(resource="Emulator")
detail=ErrorMessage.OPERATION_FAILED.format(reason="Network timeout")

# ❌ НЕПРАВИЛЬНО - случайные строки
detail="Something went wrong"  # Неинформативно
detail="Bad input"             # Не стандартизировано
```

### 5. ✅ Валидируйте перед обработкой

```python
# ✅ ПРАВИЛЬНО
skip, limit = validate_pagination_params(skip, limit)
items = db.query(Item).offset(skip).limit(limit).all()

# ❌ НЕПРАВИЛЬНО - валидация после обработки
items = db.query(Item).offset(skip).limit(limit).all()
skip, limit = validate_pagination_params(skip, limit)
```

### 6. ✅ Логируйте ошибки валидации

```python
# ✅ ПРАВИЛЬНО
is_valid, error = validate_workstation_name(name)
if not is_valid:
    logger.log_error(f"Invalid workstation name: {name} - {error}")
    raise HTTPException(status_code=400, detail=error)

# ❌ НЕПРАВИЛЬНО - молчаливо игнорируем
if not is_valid:
    raise HTTPException(status_code=400, detail=error)
```

---

## Полезные ссылки

- **Validators:** `src/utils/validators.py` (15+ функций)
- **Constants:** `src/utils/constants.py` (9 классов)
- **API Routes:** `src/api/` (5 модулей с примерами)
- **Tests:** `tests/` (89 passing tests)

---

## Контакт

Вопросы или проблемы? Проверьте:
1. PROJECT_STATE.md - текущий статус
2. SESSION_6_SUMMARY.txt - что было сделано
3. QUICK_START.md - быстрый старт

---

**Версия документации:** 1.0  
**Дата обновления:** 2025-10-19  
**Статус:** ✅ Production Ready
