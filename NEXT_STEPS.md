# 📋 ACTIONABLE TODO - Следующие шаги для реальной интеграции

**Статус:** Ready to implement | **Priority:** CRITICAL 🔴

---

## ✅ Завершено сегодня (Session 4)

- [x] Полный анализ кодовой базы (CODEBASE_ANALYSIS.md создан)
- [x] Идентифицирована причина: DEV_MODE возвращал mock данные
- [x] Удалены DEV_MODE проверки из 3 файлов API
- [x] API теперь использует реальные данные через Service слой
- [x] Сервер запущен и работает без ошибок

---

## 🔴 КРИТИЧЕСКИЕ ЗАДАЧИ (Must do next)

### Task 1: Исправить 422 ошибку при логине
**Файл:** `src/api/auth.py` и `src/utils/jwt_auth.py`

**Проблема:** POST /api/auth/login возвращает 422 Unprocessable Content

**Действие:**
1. Проверить что фронтенд отправляет правильный JSON
2. Проверить что UserLogin Pydantic модель соответствует
3. Запросить логи ошибок валидации
4. Возможно нужна дополнительная обработка ошибок

**Код для отладки:**
```bash
# Тест логина через curl
curl -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

---

### Task 2: Реализовать операции эмуляторов в API
**Файл:** `src/api/emulators.py` (строки 148+)

**Что нужно сделать:**
Заменить stub-коды на реальные вызовы EmulatorService

**Методы для реализации:**

#### 2.1 start_emulator()
```python
@router.post("/{emulator_id}/start", ...)
async def start_emulator(emulator_id: str, 
                         service: EmulatorService = Depends(...),
                         current_user: str = Depends(verify_token)):
    """Запустить эмулятор."""
    try:
        emulator = await service.get(emulator_id)
        if not emulator:
            raise HTTPException(404, "Emulator not found")
        
        # ⭐ ГЛАВНОЕ: Вызвать реальный метод
        result = await service.start(emulator_id)
        
        return APIResponse(
            success=True,
            message=f"Emulator '{emulator.name}' started",
            data=result
        )
    except Exception as e:
        logger.log_error(f"Error starting emulator: {e}")
        raise HTTPException(500, detail=str(e))
```

#### 2.2 stop_emulator()
```python
# Аналогично start_emulator() но вызвать service.stop(emulator_id)
```

#### 2.3 delete_emulator()
```python
# Аналогично но вызвать service.delete(emulator_id)
```

#### 2.4 rename_emulator()
```python
# Вызвать service.update(emulator_id, {"name": new_name})
```

---

### Task 3: Интегрировать LDPlayerManager в EmulatorService
**Файл:** `src/services/emulator_service.py`

**Что имеется:**
- ✅ LDPlayerManager существует и готов
- ✅ Имеет методы: start_emulator(), stop_emulator(), delete_emulator(), rename_emulator()
- ✅ Использует WorkstationManager.get_emulators_list() для сканирования

**Что нужно добавить в EmulatorService:**

```python
class EmulatorService(BaseService[Emulator]):
    def __init__(self, repository, ldplayer_manager):
        super().__init__(repository)
        self.ldplayer_manager = ldplayer_manager  # ← ADD THIS
    
    async def start(self, emulator_id: str):
        """Запустить эмулятор через LDPlayerManager."""
        emulator = await self.get(emulator_id)
        if not emulator:
            raise EntityNotFoundError(f"Emulator {emulator_id} not found")
        
        # Вызвать LDPlayerManager
        operation = self.ldplayer_manager.start_emulator(emulator.name)
        
        # Дождаться выполнения
        timeout = 30  # сек
        start_time = time.time()
        while operation.status == OperationStatus.PENDING:
            if time.time() - start_time > timeout:
                raise OperationTimeoutError("Start operation timeout")
            await asyncio.sleep(0.5)
        
        # Обновить статус эмулятора
        if operation.status == OperationStatus.COMPLETED:
            await self.update(emulator_id, {"status": EmulatorStatus.RUNNING})
            return {"status": "started", "operation_id": operation.id}
        else:
            return {"status": "failed", "error": operation.error}
    
    async def stop(self, emulator_id: str):
        # Аналогично start() но с stop_emulator()
        pass
    
    async def delete(self, emulator_id: str):
        # Аналогично start() но с delete_emulator()
        pass
```

---

### Task 4: Интегрировать LDPlayerManager в WorkstationService
**Файл:** `src/services/workstation_service.py`

**Что нужно добавить:**

```python
class WorkstationService(BaseService[Workstation]):
    def __init__(self, repository, workstation_managers):
        super().__init__(repository)
        self.workstation_managers = workstation_managers  # Dict[ws_id -> WorkstationManager]
    
    async def get_emulators(self, workstation_id: str) -> List[Emulator]:
        """Получить список эмуляторов рабочей станции."""
        if workstation_id not in self.workstation_managers:
            raise EntityNotFoundError(f"Workstation {workstation_id} not found")
        
        workstation_manager = self.workstation_managers[workstation_id]
        
        # ⭐ ГЛАВНОЕ: Вызвать реальный скан эмуляторов
        emulators = workstation_manager.get_emulators_list()
        
        return emulators  # Возвращает List[Emulator]
```

---

## 🚀 ПОРЯДОК РЕАЛИЗАЦИИ

```
1. Исправить 422 ошибку логина (Task 1)
   └─ Тестировать логин работает
   
2. Реализовать операции в API (Task 2)
   └─ start, stop, delete, rename работают
   
3. Интегрировать LDPlayerManager в Services (Task 3 & 4)
   └─ Services вызывают реальные методы
   
4. Финальное тестирование (Task 5)
   └─ Реальное сканирование эмуляторов
   └─ Реальные операции старта/остановки
```

---

## 📊 Expected Result After Implementation

### ДО (сейчас):
```
Frontend → API → Mock data
            ↓
       NO LDPlayer scanning
       NO real operations
```

### ПОСЛЕ (когда закончим):
```
Frontend → API → Service → LDPlayerManager → WorkstationManager → ldconsole.exe
            ↓
       Real emulator list from LDPlayer
       Real start/stop/delete/rename operations
       Real status updates
```

---

## 🧪 Validation Checklist

### Для каждого завершенного task:

- [ ] Код компилируется без ошибок
- [ ] Unit тесты остаются passing (32/32)
- [ ] Нет новых логируемых ошибок
- [ ] Документация обновлена (PROJECT_STATE.md)
- [ ] CHANGELOG.md обновлен

---

## 📝 Git Commits Example

```bash
# Task 1
git commit -m "fix: resolve 422 validation error in login endpoint"

# Task 2
git commit -m "feat: implement real emulator operations (start/stop/delete/rename)"

# Task 3
git commit -m "feat: integrate LDPlayerManager into EmulatorService"

# Task 4
git commit -m "feat: integrate WorkstationManager emulator scanning into Service layer"
```

---

## 🎯 Definition of Done

ALL Tasks completed when:

1. ✅ Login returns 200 with valid token
2. ✅ GET /api/emulators returns REAL data (not mock)
3. ✅ GET /api/workstations returns REAL data (not mock)
4. ✅ POST /api/emulators/{id}/start executes real command
5. ✅ POST /api/emulators/{id}/stop executes real command
6. ✅ DELETE /api/emulators/{id} executes real command
7. ✅ POST /api/emulators/rename executes real command
8. ✅ All 32 unit tests still passing
9. ✅ Web UI shows real emulators and their status
10. ✅ Operations work on real machine with LDPlayer

---

**Estimated Time:** 3-4 hours for all tasks

**Started:** 2025-10-18 01:20 UTC

**Status:** Ready for next session 🚀
