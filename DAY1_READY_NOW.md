# 🚀 WEEK 2 DAY 1 - ГОТОВ К ЗАПУСКУ!

> **Дата:** 18 октября 2025  
> **Статус:** ✅ **ВСЕ ИНСТРУМЕНТЫ ГОТОВЫ - МОЖНО НАЧИНАТЬ!**  
> **Время выполнения:** 4-6 часов

---

## 📦 ЧТО СОЗДАНО (4 новых файла)

### 1. `test_winrm_connection.py` ✅ (320+ lines)
**Назначение:** Комплексное тестирование WinRM соединения перед продакшн

**Что делает:**
- ✅ Test 1: Basic Connection (echo команда)
- ✅ Test 2: System Info (WMI запросы - OS, RAM, Hostname)
- ✅ Test 3: LDPlayer Detection (проверяет 4 пути, список эмуляторов)

**Как использовать:**
```bash
cd Server
# 1. Открой test_winrm_connection.py
# 2. Обнови строки 17-19:
#    HOST = "192.168.1.101"        # ТВОЙ IP
#    USERNAME = "admin"             # ТВОЙ username
#    PASSWORD = "your_password"     # ТВОЙ пароль
# 3. Запусти:
python test_winrm_connection.py
```

**Ожидаемый результат:**
```
✅ Test 1 - Basic Connection: PASSED
✅ Test 2 - System Info: PASSED
   Hostname: DESKTOP-ABC123
   OS: Microsoft Windows 10 Pro
   Memory: 16 GB
✅ Test 3 - LDPlayer Detection: PASSED
   Found LDPlayer at: C:\Program Files\LDPlayer\LDPlayer4.0
   Found 2 emulators:
     - leidian0: idle
     - leidian1: running (PID: 12345)

Summary: 3/3 tests PASSED ✅
```

---

### 2. `encrypt_password.py` ✅ (80+ lines)
**Назначение:** Интерактивное шифрование паролей для config.json

**Что делает:**
- Запрашивает пароль (не отображается при вводе)
- Подтверждение пароля
- Шифрует через SecurityManager (Fernet AES-128)
- Выдаёт готовую строку для config.json

**Как использовать:**
```bash
cd Server
python encrypt_password.py
# Введи пароль: ***********
# Подтверди:    ***********
# Получишь: gAAAAABm7k3L...
```

**Вывод:**
```
============================================================
Encrypted Password:
============================================================
gAAAAABm7k3L4xJ9K2pN8qR5tV7wXyZ1aB3cD5eF6gH8iJ0kL2mN4oP6

============================================================
Usage in config.json:
============================================================
{
  "auth": {
    "username": "admin",
    "password": "gAAAAABm7k3L4xJ9K2pN8qR5tV7wXyZ1aB3cD5eF6gH8iJ0kL2mN4oP6"
  }
}
```

---

### 3. `add_workstation.py` ✅ (180+ lines)
**Назначение:** Управляемый wizard добавления workstation в config.json

**Что делает:**
- Интерактивные промпты с дефолтными значениями
- **Автоматическое шифрование пароля** (SecurityManager)
- **Автоматический backup:** `config.backup.YYYYMMDD_HHMMSS.json`
- JSON валидация перед сохранением
- Превью перед commit

**Как использовать:**
```bash
cd Server
python add_workstation.py
```

**Интерактивный процесс:**
```
╔════════════════════════════════════════════════════════════╗
║       🖥️  Add Workstation to Config.json       ║
╚════════════════════════════════════════════════════════════╝

Workstation ID [ws-prod-1]: ws-prod-1
Workstation Name [Production Workstation 1]: Production Workstation 1
Workstation IP/Hostname [192.168.1.101]: 192.168.1.101
Protocol (winrm/ssh) [winrm]: winrm
LDPlayer Path [C:\Program Files\LDPlayer\LDPlayer4.0]: 
Username [admin]: admin
Password: ***********
Confirm Password: ***********

✅ Password encrypted successfully
✅ Backup created: config.backup.20251018_143022.json
✅ Workstation added to config.json

Next steps:
  1. python run_server_stable.py (production mode)
  2. Check logs for: "✅ Connected via WinRM"
```

**Создаваемая структура:**
```json
{
  "id": "ws-prod-1",
  "name": "Production Workstation 1",
  "host": "192.168.1.101",
  "protocol": "winrm",
  "ldplayer_path": "C:\\Program Files\\LDPlayer\\LDPlayer4.0",
  "auth": {
    "username": "admin",
    "password": "gAAAAABm7k3L..." 
  },
  "enabled": true,
  "added_at": "2025-10-18T14:30:22.123456Z"
}
```

---

### 4. `DAY1_QUICKSTART.md` ✅ (400+ lines)
**Назначение:** Полный пошаговый гайд по Day 1 (4-6 часов работы)

**Содержит:**
- 🎯 **Task 1:** Prepare test machine (30 min)
- 🎯 **Task 2:** Enable WinRM (30 min) - 7 PowerShell команд
- 🎯 **Task 3:** Test connection (60 min) - Запуск test_winrm_connection.py
- 🎯 **Task 4:** Add to config (30 min) - Wizard add_workstation.py
- 🎯 **Task 5:** Run production (60 min) - Запуск run_server_stable.py
- 🎯 **Task 6:** Verify in UI (30 min) - Проверка real emulators

**Troubleshooting (5 проблем):**
- Connection refused → WinRM not enabled
- 401 Unauthorized → Basic auth disabled
- LDPlayer not found → Wrong path
- No emulators → OK (можно создать позже)
- UI shows mock data → Check DEV_MODE

**Success Criteria (8 чекбоксов):**
- [ ] WinRM enabled and verified
- [ ] test_winrm_connection.py: 3/3 tests pass
- [ ] Workstation added to config.json
- [ ] Production server connects successfully
- [ ] UI displays real workstation count
- [ ] UI displays real emulators
- [ ] Start button controls real emulator
- [ ] Stop button controls real emulator

---

## 🎯 QUICK START (4 ШАГА)

### Шаг 1: Читай гайд
```bash
# Открой и прочитай:
DAY1_QUICKSTART.md
```

### Шаг 2: Обнови тестовый скрипт
```bash
cd Server
# Открой test_winrm_connection.py
# Измени строки 17-19 на ТВОИ данные:
HOST = "192.168.1.101"      # IP твоей Windows машины
USERNAME = "admin"           # Твой username
PASSWORD = "твой_пароль"     # Твой пароль
```

### Шаг 3: Включи WinRM на remote машине
```powershell
# НА REMOTE МАШИНЕ (Administrator PowerShell):
winrm quickconfig
Enable-PSRemoting -Force
Set-Item WSMan:\localhost\Client\TrustedHosts "*" -Force
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm get winrm/config  # Verify
Test-WSMan -ComputerName localhost  # Test
```

### Шаг 4: Запусти тестирование
```bash
cd Server
python test_winrm_connection.py
# Ожидай: 3/3 tests PASSED

# Если OK:
python add_workstation.py  # Добавь workstation в config
# Останови DEV server (Ctrl+C)
python run_server_stable.py  # Запусти production
```

---

## 📋 DAY 1 TASKS (6 задач, ~4 часа)

### ⏱️ Task 1: Prepare Test Machine (30 min)
**Что нужно:**
- [ ] Windows 10/11 машина с LDPlayer
- [ ] IP address записан
- [ ] Username/Password записаны
- [ ] LDPlayer установлен (любая версия 4.0+)

### ⏱️ Task 2: Enable WinRM (30 min)
**Что делать:**
- [ ] Запустить PowerShell as Administrator
- [ ] Выполнить 7 команд (см. Quick Start Шаг 3)
- [ ] Проверить: `winrm get winrm/config`
- [ ] Тест: `Test-WSMan -ComputerName localhost`

### ⏱️ Task 3: Test Connection (60 min)
**Что делать:**
- [ ] Обновить `test_winrm_connection.py` (строки 17-19)
- [ ] Запустить: `python test_winrm_connection.py`
- [ ] Проверить: 3/3 tests PASSED
- [ ] Записать найденные emulators

### ⏱️ Task 4: Add to Config (30 min)
**Что делать:**
- [ ] Запустить: `python add_workstation.py`
- [ ] Ввести данные (IP, username, password)
- [ ] Проверить backup создан: `config.backup.*.json`
- [ ] Проверить `config.json` обновлён

### ⏱️ Task 5: Run Production (60 min)
**Что делать:**
- [ ] Остановить DEV server (Ctrl+C)
- [ ] Запустить: `python run_server_stable.py` (БЕЗ DEV_MODE)
- [ ] Проверить логи: "✅ Connected via WinRM"
- [ ] Проверить: "✅ Found X emulators"

### ⏱️ Task 6: Verify in UI (30 min)
**Что делать:**
- [ ] Открыть: http://localhost:3000
- [ ] Login: admin/admin123
- [ ] Проверить: Workstation count изменился (не 3)
- [ ] Проверить: Emulator count изменился (не 6)
- [ ] Тест: Нажать Start на эмуляторе → проверить remote машину
- [ ] Тест: Нажать Stop → проверить remote машину

---

## ✅ SUCCESS CRITERIA (8 чекбоксов)

### Технические критерии:
- [ ] **WinRM enabled** and verified on remote machine
- [ ] **test_winrm_connection.py:** 3/3 tests pass
- [ ] **Workstation added** to config.json (encrypted password)
- [ ] **Production server** connects successfully (no errors in logs)

### Функциональные критерии:
- [ ] **UI displays real workstation** count (not mock "3 Workstations")
- [ ] **UI displays real emulators** (not mock 6 emulators)
- [ ] **Start button** actually starts emulator on remote machine
- [ ] **Stop button** actually stops emulator on remote machine

---

## 🐛 TROUBLESHOOTING (5 проблем)

### 1️⃣ Connection Refused
**Проблема:** `ConnectionRefusedError` или `timeout`
**Причина:** WinRM не включён
**Решение:**
```powershell
# На remote машине:
winrm quickconfig
Enable-PSRemoting -Force
# Проверь:
Test-WSMan -ComputerName localhost
```

### 2️⃣ 401 Unauthorized
**Проблема:** `401 Unauthorized`
**Причина:** Basic auth выключен
**Решение:**
```powershell
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
```

### 3️⃣ LDPlayer Not Found
**Проблема:** `Test 3 FAILED - LDPlayer not found`
**Причина:** Неправильный путь
**Решение:**
- Найди путь: `C:\Program Files\LDPlayer\LDPlayer4.0`
- Проверь есть ли `dnconsole.exe`
- Обнови `ldplayer_path` в config.json

### 4️⃣ No Emulators Found
**Проблема:** `Found 0 emulators`
**Причина:** Эмуляторы не созданы
**Решение:** Это **OK!** Можно создать позже через LDPlayer UI или API

### 5️⃣ UI Shows Mock Data
**Проблема:** UI показывает "3 Workstations", "6 emulators"
**Причина:** DEV_MODE всё ещё включён
**Решение:**
- Останови: `Ctrl+C` в терминале backend
- Запусти: `python run_server_stable.py` (БЕЗ `DEV_MODE=true`)

---

## 📊 PROGRESS TRACKING

### Time Log:
| Task | Estimated | Actual | Status |
|------|-----------|--------|--------|
| Task 1: Prepare | 30 min | _____ | [ ] |
| Task 2: WinRM | 30 min | _____ | [ ] |
| Task 3: Test | 60 min | _____ | [ ] |
| Task 4: Config | 30 min | _____ | [ ] |
| Task 5: Production | 60 min | _____ | [ ] |
| Task 6: Verify | 30 min | _____ | [ ] |
| **TOTAL** | **4 hours** | **_____** | **[ ]** |

### Notes:
```
[14:30] Started Day 1
[____] _______________________________
[____] _______________________________
[____] _______________________________
```

---

## 🔄 NEXT STEPS (После Day 1)

### Day 2: Stability (19 октября)
- Error handling with retry logic
- Timeout management (30s timeout)
- Structured logging
- Stress test: 10 Start/Stop operations

### Day 3-4: Tests (20-21 октября)
- 20+ pytest tests
- 75%+ code coverage
- Test all API endpoints
- Integration tests

### Day 5: Monitoring (22 октября)
- System metrics (CPU/RAM/Disk)
- Health status tracking
- Metrics history
- Prometheus integration

---

## 📁 FILE LOCATIONS

```
Server/
├── test_winrm_connection.py .... ✅ UPDATE IP/PASSWORD THEN RUN
├── encrypt_password.py ......... ✅ RUN IMMEDIATELY
├── add_workstation.py .......... ✅ RUN IMMEDIATELY
└── config.json ................. ⏳ WILL BE UPDATED BY WIZARD

Root/
├── DAY1_QUICKSTART.md .......... ✅ READ NOW (400-line guide)
└── DAY1_READY_NOW.md ........... ✅ THIS FILE (summary)

Week 2 Docs/
├── WEEK2_PLAN.md ............... 📋 Full week plan (800+ lines)
├── WEEK2_CHECKLIST.md .......... ☑️  Task checklist (50+ tasks)
├── CURRENT_STATE.md ............ 📊 Technical status (600+ lines)
└── SUMMARY.md .................. 📝 Brief overview
```

---

## 🎯 CURRENT SYSTEM STATE

### Backend:
- ✅ **Running:** FastAPI server on port 8000
- ✅ **Mode:** DEV_MODE (mock data)
- ✅ **Logs:** `logs/server.log`
- ⏳ **Next:** Stop DEV, start production mode

### Frontend:
- ✅ **Running:** React + Vite on port 3000
- ✅ **Browser:** http://localhost:3000
- ✅ **Login:** admin/admin123
- ✅ **Status:** No changes needed

### Week 1 Infrastructure:
- ✅ **Security:** JWT auth + Fernet encryption (SecurityManager)
- ✅ **UI:** React 18.2 + Vite 5.0 + Tailwind CSS
- ✅ **Mock Data:** 6 emulators, 4 workstations
- ✅ **PyWinRM:** 0.5.0 installed and ready

### Week 2 Day 1 Tools:
- ✅ **test_winrm_connection.py:** Created (320+ lines)
- ✅ **encrypt_password.py:** Created (80+ lines)
- ✅ **add_workstation.py:** Created (180+ lines)
- ✅ **DAY1_QUICKSTART.md:** Created (400+ lines)
- ⏳ **User Action:** Execute Day 1 tasks (~4 hours)

---

## 🚨 IMPORTANT REMINDERS

### 1. Security:
- ✅ Используй `encrypt_password.py` или `add_workstation.py`
- ❌ **НЕ храни plaintext пароли** в config.json
- ✅ Backup файлы создаются автоматически

### 2. WinRM:
- ✅ WinRM работает только на Windows
- ✅ Порт 5985 (HTTP) или 5986 (HTTPS)
- ✅ Basic auth должен быть включён

### 3. LDPlayer:
- ✅ Проверяется 4 стандартных пути
- ✅ Требуется `dnconsole.exe` для управления
- ✅ Команды: `list`, `launch`, `quit`, `reboot`

### 4. Production Mode:
- ❌ **Останови DEV server** перед запуском production
- ✅ Убедись что `DEV_MODE` не установлен
- ✅ Проверь логи на "✅ Connected via WinRM"

---

## 🎉 YOU ARE READY!

### Статус Day 1:
```
✅ Все инструменты созданы (4 файла, ~980 строк)
✅ Полный гайд готов (DAY1_QUICKSTART.md)
✅ Troubleshooting guide включён (5 проблем)
✅ Success criteria определены (8 чекбоксов)
⏳ Ждём твоего запуска!
```

### Первые 3 команды:
```bash
# 1. Читай гайд
cat DAY1_QUICKSTART.md

# 2. Обнови тестовый скрипт
code Server/test_winrm_connection.py  # Строки 17-19

# 3. Начинай!
python Server/test_winrm_connection.py
```

---

**🚀 Успехов в Week 2! Все инструменты готовы - просто следуй гайду! 🚀**

**Последнее обновление:** 18 октября 2025, 14:30  
**Создано файлов:** 4 (test_winrm_connection.py, encrypt_password.py, add_workstation.py, DAY1_QUICKSTART.md)  
**Статус:** ✅ **READY TO START!**
