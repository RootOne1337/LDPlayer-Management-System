# ✅ WEEK 2 CHECKLIST

**Период:** 18-22 октября 2025  
**Цель:** Real connections + Tests + Monitoring

---

## 📋 DAY 1 - WinRM Setup (18.10)

### Подготовка (30 мин)
- [x] ✅ Создан test_winrm_connection.py (320+ lines)
- [x] ✅ Создан encrypt_password.py (80+ lines)
- [x] ✅ Создан add_workstation.py (180+ lines)
- [x] ✅ Создан DAY1_QUICKSTART.md (400+ lines)
- [ ] Выбрать тестовую машину для WinRM
- [ ] Записать IP address: `_________________`
- [ ] Проверить LDPlayer установлен
- [ ] Записать credentials: `admin / ________`

### Настройка WinRM (1 час)
**На remote машине:**
- [ ] Запустить `winrm quickconfig`
- [ ] Выполнить `Enable-PSRemoting -Force`
- [ ] Добавить trusted hosts: `Set-Item WSMan:\localhost\Client\TrustedHosts "*" -Force`
- [ ] Включить Basic auth: `winrm set winrm/config/service/auth '@{Basic="true"}'`
- [ ] Проверить статус: `winrm get winrm/config`

**На server машине:**
- [ ] Создать файл `Server/test_winrm_connection.py`
- [ ] Указать IP и credentials в скрипте
- [ ] Запустить тест: `python test_winrm_connection.py`
- [ ] Убедиться: "✅ All tests passed!"

### Integration (2 часа)
- [ ] Зашифровать password: `security.encrypt_password("...")`
- [ ] Обновить `config.json` с real workstation
- [ ] Запустить server БЕЗ DEV_MODE: `python run_server_stable.py`
- [ ] Проверить logs: "✅ Connected via WinRM"
- [ ] Проверить logs: "✅ Found X emulators"

### UI Testing (1 час)
- [ ] Открыть http://localhost:3000
- [ ] Login: admin / admin123
- [ ] Dashboard показывает real workstation count
- [ ] Emulators показывает real эмуляторы
- [ ] Попробовать Start на реальном эмуляторе
- [ ] Эмулятор реально запустился? ✅

### ✅ Day 1 Success Criteria:
- [ ] WinRM работает
- [ ] Server подключается к workstation
- [ ] Real emulators видны в UI
- [ ] Start/Stop работает на реальном эмуляторе

---

## 📋 DAY 2 - Stability (19.10)

### Error Handling (1.5 часа)
- [ ] Добавить retry logic в `src/remote/workstation.py`
- [ ] Импортировать tenacity
- [ ] Декоратор `@retry(stop_after_attempt=3)`
- [ ] Тест: отключить машину → должно retry → fallback

### Timeout Management (1 час)
- [ ] Добавить asyncio в `src/api/emulators.py`
- [ ] ThreadPoolExecutor для blocking operations
- [ ] `asyncio.wait_for(..., timeout=30)`
- [ ] Тест: длительная операция → timeout после 30s

### Logging (1 час)
- [ ] Добавить structured logging для operations
- [ ] Log начало операции с timestamp
- [ ] Log окончание с duration
- [ ] Log ошибки с details

### Stress Test (30 мин)
- [ ] Создать `Server/test_stress.py`
- [ ] 10 Start/Stop операций подряд
- [ ] Запустить: `python test_stress.py`
- [ ] Все 10 операций успешны?

### ✅ Day 2 Success Criteria:
- [ ] Retry logic работает
- [ ] Timeouts предотвращают зависание
- [ ] Логи информативные
- [ ] Система стабильна (10 операций без сбоев)

---

## 📋 DAY 3 - Tests Part 1 (20.10)

### Pytest Setup (1 час)
- [ ] Создать `tests/conftest.py`
- [ ] Fixture: `test_client`
- [ ] Fixture: `auth_token`
- [ ] Fixture: `auth_headers`
- [ ] Fixture: `setup_dev_mode` (force DEV_MODE=true)

### Mock Data Tests (1 час)
- [ ] Создать `tests/test_mock_data.py`
- [ ] Test: `test_mock_emulators_structure`
- [ ] Test: `test_mock_workstations_structure`
- [ ] Test: `test_mock_system_status`
- [ ] Запустить: `pytest tests/test_mock_data.py -v`

### Health Tests (1 час)
- [ ] Создать `tests/test_api_health.py`
- [ ] Test: `test_health_endpoint`
- [ ] Test: `test_server_status`
- [ ] Test: `test_version_endpoint`
- [ ] Запустить: `pytest tests/test_api_health.py -v`

### Auth Tests (1.5 часа)
- [ ] Создать `tests/test_api_auth.py`
- [ ] Test: `test_login_success`
- [ ] Test: `test_login_invalid_credentials`
- [ ] Test: `test_protected_endpoint_without_token`
- [ ] Test: `test_protected_endpoint_with_invalid_token`
- [ ] Запустить: `pytest tests/test_api_auth.py -v`

### Coverage Report (30 мин)
- [ ] Install: `pip install pytest pytest-cov`
- [ ] Запустить: `pytest tests/ -v --cov=src --cov-report=html`
- [ ] Открыть: `start htmlcov/index.html`
- [ ] Current coverage: _______%

### ✅ Day 3 Success Criteria:
- [ ] 10+ тестов написано
- [ ] Все тесты passing
- [ ] Coverage report сгенерирован
- [ ] Mock data 100% покрыт

---

## 📋 DAY 4 - Tests Part 2 (21.10)

### Emulator API Tests (2 часа)
- [ ] Создать `tests/test_api_emulators.py`
- [ ] Test: `test_get_all_emulators`
- [ ] Test: `test_get_emulator_by_id`
- [ ] Test: `test_start_emulator`
- [ ] Test: `test_stop_emulator`
- [ ] Test: `test_delete_emulator`
- [ ] Запустить: `pytest tests/test_api_emulators.py -v`

### Workstation API Tests (1.5 часа)
- [ ] Создать `tests/test_api_workstations.py`
- [ ] Test: `test_get_workstations`
- [ ] Test: `test_get_workstation_emulators`
- [ ] Test: `test_workstation_status`
- [ ] Запустить: `pytest tests/test_api_workstations.py -v`

### Integration Tests (1 час)
- [ ] Создать `tests/test_integration.py`
- [ ] Test: `test_full_login_to_emulator_flow`
- [ ] Test: `test_error_handling_invalid_emulator_id`
- [ ] Запустить: `pytest tests/test_integration.py -v`

### Final Coverage (30 мин)
- [ ] Запустить: `pytest tests/ -v --cov=src --cov-report=html --cov-report=term`
- [ ] Final coverage: _______%
- [ ] Target achieved? (75%+) ✅ / ❌

### ✅ Day 4 Success Criteria:
- [ ] 20+ total tests
- [ ] All tests passing
- [ ] 75%+ code coverage
- [ ] Integration flows validated

---

## 📋 DAY 5 - Monitoring (22.10)

### Dependencies (15 мин)
- [ ] Install: `pip install psutil prometheus-client`
- [ ] Добавить в `requirements.txt`

### Monitoring Module (2 часа)
- [ ] Создать `src/utils/monitoring.py`
- [ ] Class: `SystemMonitor`
- [ ] Method: `get_current_metrics()` - CPU/RAM/Disk/Network
- [ ] Method: `get_history()` - last 60 samples
- [ ] Test: создать monitor → call methods

### API Endpoints (1 час)
- [ ] Создать `src/api/monitoring.py`
- [ ] Endpoint: `GET /api/monitoring/metrics`
- [ ] Endpoint: `GET /api/monitoring/history`
- [ ] Endpoint: `GET /api/monitoring/health`
- [ ] Add to router in `server_modular.py`

### Testing (1 час)
- [ ] Создать `Server/test_monitoring.py`
- [ ] Test: Get metrics → validate structure
- [ ] Test: Get health status → check warnings
- [ ] Test: Get history → check samples count
- [ ] Запустить: `python test_monitoring.py`

### Verification (30 мин)
- [ ] Запустить server
- [ ] Swagger: http://localhost:8000/docs
- [ ] Найти `/api/monitoring/metrics`
- [ ] Execute → получить metrics
- [ ] Данные корректны? CPU/RAM/Disk видны?

### ✅ Day 5 Success Criteria:
- [ ] Monitoring module работает
- [ ] 3 API endpoints работают
- [ ] Metrics обновляются в real-time
- [ ] Health status вычисляется

---

## 🎯 WEEK 2 FINAL CHECKLIST

### Must Have (P0):
- [ ] ✅ WinRM настроен на 1+ workstation
- [ ] ✅ Server подключается к real workstation
- [ ] ✅ Real emulators отображаются в UI
- [ ] ✅ Start/Stop работает на реальном железе

### Should Have (P1):
- [ ] ✅ 20+ automated tests написано
- [ ] ✅ 75%+ code coverage достигнуто
- [ ] ✅ Monitoring endpoints работают
- [ ] ✅ Health status tracking функционирует

### Could Have (P2):
- [ ] ⚠️ Retry logic with exponential backoff
- [ ] ⚠️ Timeout management везде
- [ ] ⚠️ Circuit breakers (optional)

---

## 📊 PROGRESS TRACKING

**Daily Progress:**
```
Day 1: [_________________] 0% → WinRM Setup
Day 2: [_________________] 0% → Stability
Day 3: [_________________] 0% → Tests Part 1
Day 4: [_________________] 0% → Tests Part 2
Day 5: [_________________] 0% → Monitoring
```

**Overall Week 2:**
```
Week 2: [__________] 0% → 75% (target)
```

---

## 🎉 COMPLETION CEREMONY

**После Week 2 у вас будет:**
- ✅ Production-ready connections
- ✅ 75%+ test coverage
- ✅ Real-time monitoring
- ✅ 75% system complete

**Print this checklist and mark it as you go!** 📄✏️

---

**Created:** 17 октября 2025  
**Start Date:** 18 октября 2025  
**End Date:** 22 октября 2025  
**Status:** 📋 Ready to Execute
