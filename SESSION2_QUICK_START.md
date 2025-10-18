# ⚡ QUICK START - Session 2 Updates

**Обновлено**: 2025-10-17  
**Статус**: 🟢 Production Ready

---

## 🎉 ЧТО НОВОГО

### ✅ 4 Major Improvements:
1. **Retry Mechanism** - Автоматические повторы при сбоях (3×, 2-10s delay)
2. **Input Validation** - Проверка данных с правильными HTTP кодами
3. **Log Rotation** - Автоматическая ротация логов (10MB, 5 backups)
4. **Clean Code** - Убрано дублирование, добавлены декораторы

---

## 🚀 КАК ИСПОЛЬЗОВАТЬ

### 1. Retry Mechanism (автоматически работает)

**В коде workstation.py**:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def run_command(self, command: str, timeout: int = 30):
    # Автоматически повторит 3 раза при сбое
    pass
```

**Что делает**:
- 1-я попытка → сразу
- 2-я попытка → через 2 секунды
- 3-я попытка → через 4-10 секунд
- Retry только на: ConnectionError, TimeoutError, OSError

**Тестирование**:
```powershell
# Отключи сеть
netsh interface set interface "Ethernet" disabled

# Попробуй выполнить команду (должно быть 3 попытки)
python test_retry.py

# Включи сеть
netsh interface set interface "Ethernet" enabled
```

---

### 2. Input Validation (автоматически работает)

**В API endpoints**:
```python
# Проверяет существование workstation
validate_workstation_exists(config, "ws_001")

# Проверяет корректность имени
validate_emulator_name("Test-Emulator")
```

**HTTP коды**:
- ✅ 200 → Success
- ⚠️ 400 → Bad Request (некорректные данные)
- ⚠️ 403 → Forbidden (нет прав)
- ❌ 404 → Not Found (не найдено)
- ⚠️ 503 → Service Unavailable (сеть)
- ⏱️ 504 → Gateway Timeout (таймаут)
- ❌ 500 → Internal Server Error

**Тестирование через Swagger**:
1. Открой http://localhost:8000/docs
2. Попробуй:
   - Создать эмулятор с пустым именем → 400
   - Получить несуществующую станцию → 404
   - Создать дубликат эмулятора → 400

---

### 3. Log Rotation (автоматически работает)

**Конфигурация** (уже настроена):
- Max размер файла: **10 MB**
- Количество архивов: **5**
- Формат: UTF-8

**Файлы логов**:
```
Server/logs/
├── app.log         # Текущий лог
├── app.log.1       # Архив 1 (самый свежий)
├── app.log.2       # Архив 2
├── app.log.3       # Архив 3
├── app.log.4       # Архив 4
└── app.log.5       # Архив 5 (самый старый)
```

**Проверка**:
```powershell
Get-ChildItem Server/logs/*.log | Select-Object Name, Length
```

---

### 4. Clean Code - Декораторы

**Использование в endpoints**:

**До** (старый код):
```python
@router.get("/example")
async def example():
    try:
        # your code
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.log_error(f"Error: {e}")
        raise HTTPException(500, str(e))
```

**После** (новый код):
```python
@router.get("/example")
@handle_api_errors(LogCategory.API)  # ← Добавь эту строку!
async def example():
    # your code
    return result
    # Ошибки обрабатываются автоматически!
```

**Сокращение**: ~10 строк на endpoint!

---

## 🔧 UTILITY FUNCTIONS

### validate_workstation_exists()
```python
from ..api.dependencies import validate_workstation_exists

validate_workstation_exists(config, "ws_001")
# Raises HTTPException 404 if not found
```

### validate_emulator_name()
```python
from ..api.dependencies import validate_emulator_name

validate_emulator_name("Test-Emulator-1")  # ✅ OK
validate_emulator_name("")                  # ❌ ValueError: empty
validate_emulator_name("X" * 101)          # ❌ ValueError: too long
validate_emulator_name("Test<>Name")       # ❌ ValueError: invalid chars
```

**Недопустимые символы**: `< > : " / \ | ? *`

---

## 📊 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Создать endpoint с валидацией

```python
from fastapi import APIRouter, HTTPException
from ..api.dependencies import (
    handle_api_errors,
    validate_workstation_exists,
    validate_emulator_name
)
from ..utils.logger import LogCategory

router = APIRouter()

@router.post("/emulators")
@handle_api_errors(LogCategory.EMULATOR)  # ← Автоматическая обработка ошибок
async def create_emulator(ws_id: str, name: str):
    # Валидация
    validate_workstation_exists(config, ws_id)
    validate_emulator_name(name)
    
    # Ваш код
    result = create_emulator_logic(ws_id, name)
    return result
    
    # Не нужен try-catch! Декоратор всё обработает!
```

### Пример 2: Выполнить команду с retry

```python
from ..remote.workstation import WorkstationManager

manager = WorkstationManager(config)

# Выполнится с автоматическим retry (3 попытки)
code, stdout, stderr = manager.run_command(
    command="dnconsole.exe",
    args=["list2"],
    timeout=30  # 30 секунд
)
```

### Пример 3: Проверить логи

```powershell
# Последние 50 строк
Get-Content Server/logs/app.log -Tail 50

# Только ошибки
Get-Content Server/logs/errors.log -Tail 20

# Размер логов
Get-ChildItem Server/logs/*.log | Measure-Object -Property Length -Sum
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Test 1: Retry Mechanism
```powershell
# Создай файл test_retry.py:
python -c "
from Server.src.remote.workstation import WorkstationManager
from Server.src.core.config import WorkstationConfig

config = WorkstationConfig(
    id='ws_test',
    ip_address='192.168.0.999',  # Несуществующий IP
    # ...
)
manager = WorkstationManager(config)
try:
    manager.run_command('test')  # Должно быть 3 попытки
except Exception as e:
    print(f'Expected: {e}')
"
```

### Test 2: Input Validation
```powershell
# Запусти сервер
cd Server
uvicorn src.api.main:app --reload

# В браузере открой:
# http://localhost:8000/docs

# Попробуй API calls:
# POST /api/emulators с name=""  → 400
# GET /api/workstations/xxx      → 404
```

### Test 3: Log Rotation
```powershell
# Создай большой лог (>10MB)
1..1000000 | ForEach-Object { 
    Add-Content Server/logs/app.log "Test line $_" 
}

# Проверь ротацию
Get-ChildItem Server/logs/*.log
```

---

## 📚 ДОКУМЕНТАЦИЯ

**Основные файлы**:
- `SESSION2_FINAL_SUMMARY.md` - Полное резюме сессии
- `CHANGELOG.md` - История всех изменений
- `PRODUCTION_GUIDE.md` - Production инструкции (обновлён!)
- `AUTO_TEST_README.md` - Автоматическое тестирование

**Код**:
- `Server/src/api/dependencies.py` - Utility декораторы
- `Server/src/remote/workstation.py` - Retry mechanism
- `Server/src/api/*.py` - API endpoints с валидацией

---

## ⚙️ КОНФИГУРАЦИЯ

### Настройка Retry:
```python
# В workstation.py можно изменить:
@retry(
    stop=stop_after_attempt(5),           # ← 5 попыток вместо 3
    wait=wait_exponential(min=1, max=30)  # ← 1-30s вместо 2-10s
)
```

### Настройка Log Rotation:
```python
# В logger.py можно изменить:
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=20*1024*1024,  # ← 20MB вместо 10MB
    backupCount=10          # ← 10 архивов вместо 5
)
```

### Настройка Timeouts:
```python
# При вызове команд:
manager.run_command(cmd, args, timeout=60)      # ← 60s timeout
manager.run_ldconsole_command(action, timeout=120)  # ← 120s timeout
```

---

## 🎯 NEXT STEPS

### Immediate:
1. ✅ Протестируй retry механизм
2. ✅ Проверь валидацию через Swagger
3. ✅ Убедись что логи ротируются

### Short Term:
4. Примени `@handle_api_errors` к своим endpoints
5. Используй `validate_*` функции где нужно
6. Запусти LDPlayer и протестируй create emulator

### Long Term:
7. Настрой WinRM на ws_002-008
8. Создай monitoring dashboard
9. Добавь JWT authentication

---

## 💡 BEST PRACTICES

### ✅ DO:
- Используй `@handle_api_errors` на всех endpoints
- Валидируй входные данные через `validate_*` функции
- Используй timeout параметры при удалённых командах
- Проверяй логи регулярно

### ❌ DON'T:
- Не пиши свои try-catch блоки (используй декоратор)
- Не забывай про timeout (может зависнуть)
- Не создавай файлы >10MB в logs (ротируются автоматически)
- Не игнорируй validation errors

---

## 🔗 QUICK LINKS

**Swagger UI**: http://localhost:8000/docs  
**Health Check**: http://localhost:8000/api/health  
**Server Status**: http://localhost:8000/api/status

**Команды**:
```powershell
# Тесты
python test_all_features.py

# Desktop App
python app_production.py

# Server
cd Server
uvicorn src.api.main:app --reload

# Логи
Get-Content Server/logs/app.log -Tail 50 -Wait
```

---

**Status**: ✅ READY TO USE  
**Quality**: ⬆️⬆️ IMPROVED  
**Stability**: 🛡️ PRODUCTION READY

🎉 **Всё готово! Используй новые features!** 🎉
