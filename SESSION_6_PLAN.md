# 🚀 SESSION 6 PLAN - Реализация операций (start/stop/delete/rename)

**Статус:** Ожидание начала  
**Целевой прогресс:** 75% → 86% (+11%)  
**Примерное время:** 4-5 часов  

---

## 📋 TODO для Session 6

### ✅ Завершено в Session 5
- ✅ Найдена и исправлена критическая ошибка в EmulatorService
- ✅ Все mock fixtures обновлены
- ✅ 125/125 тестов PASSING
- ✅ API реально сканирует эмуляторы
- ✅ Документация обновлена

### 🔴 Требуется в Session 6
- [ ] **Task 1:** Реализовать операции (start, stop, delete, rename)
- [ ] **Task 2:** Интегрировать async operation queue
- [ ] **Task 3:** Тестировать с реальной машиной LDPlayer
- [ ] **Task 4:** Финальное интеграционное тестирование

---

## 🎯 TASK 1: Реализовать операции (2-3 часа)

### Что нужно сделать

В файле `src/api/emulators.py` есть stub-функции:

```python
@router.post("/{emulator_id}/start", response_model=APIResponse)
async def start_emulator(emulator_id: str, ...):
    """Запустить эмулятор."""
    return APIResponse(success=True, message="Emulator started")  # ← STUB!

@router.post("/{emulator_id}/stop", response_model=APIResponse)
async def stop_emulator(emulator_id: str, ...):
    """Остановить эмулятор."""
    return APIResponse(success=True, message="Emulator stopped")  # ← STUB!

@router.delete("/{emulator_id}", response_model=APIResponse)
async def delete_emulator(emulator_id: str, ...):
    """Удалить эмулятор."""
    return APIResponse(success=True, message="Emulator deleted")  # ← STUB!

@router.put("/{emulator_id}", response_model=APIResponse)
async def rename_emulator(emulator_id: str, data: dict, ...):
    """Переименовать эмулятор."""
    return APIResponse(success=True, message="Emulator renamed")  # ← STUB!
```

### Правильная реализация

```python
@router.post("/{emulator_id}/start", response_model=APIResponse)
async def start_emulator(
    emulator_id: str,
    service: EmulatorService = Depends(get_emulator_service),
    current_user: str = Depends(verify_token)
):
    """Запустить эмулятор."""
    try:
        # 1. Получить эмулятор
        emulator = await service.get_by_id(emulator_id)
        if not emulator:
            raise HTTPException(status_code=404, detail="Emulator not found")
        
        # 2. Вызвать LDPlayerManager через Service
        success = await service.start(emulator_id)
        
        # 3. Вернуть результат
        return APIResponse(
            success=success,
            message=f"Emulator {emulator.name} started successfully"
        )
    except Exception as e:
        logger.log_error(f"Error starting emulator: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Все 4 операции

| Операция | Метод | Эндпойнт | Service метод |
|----------|-------|----------|----------------|
| Start | POST | `/{id}/start` | `await service.start(id)` |
| Stop | POST | `/{id}/stop` | `await service.stop(id)` |
| Delete | DELETE | `/{id}` | `await service.delete(id)` |
| Rename | PUT | `/{id}` | `await service.update(id, {"name": ...})` |

---

## 🎯 TASK 2: Интегрировать async operation queue (1 час)

### Что нужно сделать

В Service методах нужно:

```python
async def start(self, emulator_id: str) -> bool:
    """Запустить эмулятор."""
    em = await self.get_or_fail(emulator_id)
    
    # 1. Создать операцию через LDPlayerManager
    operation = self.manager.start_emulator(em.name)
    
    # 2. Ждать результата (макс 5 минут)
    result = await self.manager.wait_for_operation(operation.id, timeout=300)
    
    # 3. Обновить статус
    if result.status == OperationStatus.COMPLETED:
        em.status = EmulatorStatus.RUNNING
        return True
    else:
        raise Exception(f"Operation failed: {result.message}")
```

### Операция queue уже существует!

В `src/remote/ldplayer_manager.py`:
- ✅ `queue_operation()` - добавить в очередь
- ✅ `wait_for_operation()` - ждать результата
- ✅ `get_operation()` - получить статус
- ✅ `_execute_operation()` - выполнить операцию

Нужно только использовать!

---

## 🎯 TASK 3: Тестировать с реальной машиной (1 час)

### Что проверить

```bash
# 1. Проверить сканирование
curl http://127.0.0.1:8001/api/emulators -H "Authorization: Bearer <token>"
# Должен вернуть реальные эмуляторы с корректными статусами

# 2. Проверить start
curl -X POST http://127.0.0.1:8001/api/emulators/emu-001/start \
  -H "Authorization: Bearer <token>"
# Должен запустить реальный эмулятор (видно в LDPlayer)

# 3. Проверить stop
curl -X POST http://127.0.0.1:8001/api/emulators/emu-001/stop \
  -H "Authorization: Bearer <token>"
# Должен остановить реальный эмулятор

# 4. Проверить delete
curl -X DELETE http://127.0.0.1:8001/api/emulators/emu-001 \
  -H "Authorization: Bearer <token>"
# Должен удалить эмулятор (проверить в LDPlayer)
```

### Ожидаемый результат
- ✅ API commands выполняются на реальных эмуляторах LDPlayer
- ✅ Статусы обновляются в реальном времени
- ✅ Нет ошибок в логах
- ✅ Операции откатываются если нужно

---

## 🎯 TASK 4: Финальное интеграционное тестирование (1 час)

### Что проверить

1. **Web UI** - Все работает через браузер
   - ✅ Показывает реальные эмуляторы
   - ✅ Можно запустить/остановить эмулятор
   - ✅ Можно удалить эмулятор
   - ✅ Можно переименовать эмулятор

2. **API** - Все 23 эндпойнта работают
   - ✅ Workstations (7 эндпойнтов)
   - ✅ Emulators (9 эндпойнтов) - ВСЕ 4 операции
   - ✅ Operations (2 эндпойнта)
   - ✅ Health (2 эндпойнта)
   - ✅ Auth (3 эндпойнта)

3. **Тесты** - Все тесты проходят
   - ✅ 125/125 unit тестов
   - ✅ Интеграционные тесты для операций
   - ✅ Performance тесты

---

## 📝 Файлы для изменения

### Основные файлы

1. **src/api/emulators.py** - ГЛАВНЫЙ ФАЙЛ
   - Добавить реальную логику в 4 operations
   - Вызывать service методы вместо stub'ов
   - Обработать ошибки

2. **src/services/emulator_service.py** - Обновить
   - Методы `start()`, `stop()`, `delete()` сейчас STUB
   - Нужно интегрировать с LDPlayerManager
   - Нужно вызывать `wait_for_operation()`

3. **tests/test_emulator_service.py** - Добавить тесты
   - Тесты для `start()`, `stop()`, `delete()`
   - Проверить что вызываются правильные методы
   - Проверить операцию queue

---

## 🧪 Как запустить сервер для тестирования

```bash
# 1. Перейти в папку
cd C:\Users\dimas\Documents\Remote\LDPlayerManagementSystem\Server

# 2. Установить env переменные
$env:PYTHONPATH="C:\Users\dimas\Documents\Remote\LDPlayerManagementSystem\Server"
$env:JWT_SECRET_KEY="xK8mP2vQ9sL4wN7jR5tY1uH3bF6cE0aD9gZ2iX5oM8nV4kW7pS1qT3rU6yA0hJ4e"

# 3. Запустить сервер
python -m uvicorn src.core.server:app --host 127.0.0.1 --port 8001 --reload

# 4. Запустить тесты (в другом терминале)
python -m pytest tests/ -v

# 5. Открыть в браузере
# http://127.0.0.1:8001/
# http://127.0.0.1:8001/docs (Swagger UI)
```

---

## 🔐 Как получить токен для curl

```bash
# 1. Логин
curl -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 2. Скопировать токен из ответа
# { "access_token": "eyJhbGc...", "token_type": "bearer" }

# 3. Использовать в других запросах
curl http://127.0.0.1:8001/api/emulators \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## 📊 Ожидаемый прогресс после Session 6

| Компонент | Было | Станет | Статус |
|-----------|------|--------|--------|
| **Проект готовности** | 75% | 86% | ⬆️ +11% |
| **Unit Тесты** | 125/125 | 135+/135+ | ✅ |
| **API Операции** | 🟡 50% | ✅ 100% | FIXED |
| **LDPlayer Интеграция** | ✅ Сканирование | ✅ Все операции | READY |
| **Web UI Функционал** | 🟡 50% | ✅ 100% | READY |

---

## 🎓 Примечания

### Важно помнить
- `LDPlayerManager` СИНХРОННЫЙ (использует subprocess)
- Service методы - АСИНХРОННЫЕ (но могут вызывать sync код)
- API обязан быть АСИНХРОННЫМ (FastAPI требует)

### Паттерн
```python
# API - АСИНХРОННЫЙ
async def start_emulator(...):
    # Service - АСИНХРОННЫЙ
    success = await service.start(id)  # await нужен!
    # Service.start() вызывает
    # LDPlayerManager.start_emulator() - СИНХРОННЫЙ
    # и LDPlayerManager.wait_for_operation() - АСИНХРОННЫЙ
```

### Если возникнут ошибки
1. Проверь что метод существует: `dir(manager)`
2. Проверь типы параметров: `help(manager.start_emulator)`
3. Посмотри в тесты как это использовать: `tests/test_emulator_service.py`
4. Запусти с `--reload` флагом чтобы видеть ошибки сразу

---

## 📚 Справочные документы

- ✅ `EMULATOR_SCANNER_FIX.md` - Как исправили сканер
- ✅ `SESSION_5_SUMMARY.md` - Итоги Session 5
- ✅ `PROJECT_STATE.md` - Текущее состояние проекта
- ✅ `NEXT_STEPS.md` - План разработки (создан в Session 4)

---

## ✅ Чеклист перед Session 6

- [ ] Прочитал все документы выше
- [ ] Понял архитектуру (API → Service → Manager)
- [ ] Знаю где хранятся stub'ы
- [ ] Подготовил тестовую среду
- [ ] Знаю как запустить сервер и тесты
- [ ] Готов к кодированию!

---

**ГОТОВО К SESSION 6! 🚀**
