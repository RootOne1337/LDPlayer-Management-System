# 📊 Monitoring Dashboard - Quick Guide

## 🎯 Обзор

Real-time мониторинг всех рабочих станций LDPlayer Management System.

**Возможности:**
- ✅ Live статус всех workstations (online/offline)
- ✅ Количество запущенных эмуляторов
- ✅ Latency (время отклика) в миллисекундах
- ✅ Auto-refresh каждые 5 секунд
- ✅ Alert при 3+ consecutive failures
- ✅ Event log с историей событий
- ✅ Dark theme для удобства

---

## 🚀 Быстрый Старт

### Вариант 1: Через BAT файл (рекомендуется)
```bash
# Double-click:
RUN_DASHBOARD.bat
```

### Вариант 2: Через командную строку
```bash
# Activate venv
venv\Scripts\activate

# Run dashboard
python dashboard_monitoring.py
```

---

## 📋 Интерфейс

### Верхняя Панель (Header)
**Статистика:**
- **Total:** Общее количество workstations
- **🟢 Online:** Доступные станции
- **🔴 Offline:** Недоступные станции
- **📱 Emulators:** Общее количество эмуляторов

**Кнопки управления:**
- **🔄 Refresh Now** - Принудительное обновление
- **⏸️ Pause / ▶️ Resume** - Приостановить/возобновить мониторинг
- **🗑️ Clear Log** - Очистить event log

### Таблица Статусов

| Колонка | Описание |
|---------|----------|
| **Workstation ID** | Уникальный ID (ws_001, ws_002, ...) |
| **Name** | Имя станции (WS-FARM-001, ...) |
| **IP Address** | IP адрес (192.168.1.101, ...) |
| **Status** | ONLINE (зелёный) / OFFLINE (красный) |
| **Emulators** | Количество запущенных эмуляторов |
| **Latency (ms)** | Время отклика в миллисекундах |
| **Last Check** | Время последней проверки (HH:MM:SS) |

**Цвета статусов:**
- 🟢 **ONLINE** (зелёный) - Станция доступна
- 🔴 **OFFLINE** (красный) - Станция недоступна
- 🟡 **WARNING** (жёлтый) - Проблемы (не используется пока)
- ⚪ **UNKNOWN** (серый) - Неизвестный статус

### Event Log
Лог событий с timestamp:
- `[HH:MM:SS] 🚀 Monitoring started` - Старт мониторинга
- `[HH:MM:SS] ❌ ws_002: Connection failed` - Ошибка подключения
- `[HH:MM:SS] ⚠️ ALERT #1: ws_003 - timeout` - Критическая ошибка

**Максимум:** 100 строк (автоматическая очистка старых)

---

## ⚙️ Настройки

### Файл: `dashboard_monitoring.py`

**Параметры мониторинга:**
```python
REFRESH_INTERVAL = 5000        # Интервал обновления (мс)
MAX_LOG_LINES = 100            # Макс. строк в логе
ALERT_THRESHOLD = 3            # Alert после N ошибок подряд
```

**Изменение интервала:**
```python
# Для более частых проверок (каждые 3 секунды):
REFRESH_INTERVAL = 3000

# Для менее частых (каждые 10 секунд):
REFRESH_INTERVAL = 10000
```

---

## 🔍 Как Работает Мониторинг

### 1. Background Worker Thread
```python
class MonitoringWorker(QThread):
    - Запускается в фоне (не блокирует UI)
    - Проверяет каждую workstation каждые 5 секунд
    - Измеряет latency
    - Получает список эмуляторов (ldconsole list2)
    - Emit сигналы в main thread
```

### 2. Connection Test
Для каждой workstation:
1. `manager.test_connection()` - проверка доступности
2. Измерение времени отклика (latency)
3. Если online → получить список эмуляторов
4. Если offline → записать ошибку

### 3. Alert System
```python
failure_counts[ws_id] += 1  # Increment on failure
if failure_counts[ws_id] == ALERT_THRESHOLD:
    emit alert  # Показать критическую ошибку
```

**Сброс счётчика:** При успешном подключении

---

## 📊 Примеры Использования

### Ежедневный Мониторинг
```
1. Запустить dashboard утром: RUN_DASHBOARD.bat
2. Оставить работать в фоне
3. Проверять alerts в event log
4. При offline - проверить физическую станцию
```

### Диагностика Проблем
```
1. Найти offline станцию в таблице
2. Посмотреть error в event log
3. Проверить:
   - Сеть: ping IP_ADDRESS
   - LDPlayer: запущен ли на станции
   - WinRM: Enable-PSRemoting на станции
```

### Нагрузка Системы
```
1. Посмотреть колонку "Emulators"
2. Если станция перегружена (>10 эмуляторов):
   - Перераспределить нагрузку
   - Добавить новую станцию
```

---

## 🐛 Troubleshooting

### Проблема: Dashboard не запускается
**Решение:**
```bash
# Проверить зависимости
pip install PyQt6

# Проверить config.json
python -c "from Server.src.core.config import get_config; print(len(get_config().workstations))"
```

### Проблема: Все станции OFFLINE
**Причины:**
1. **Неправильные IP адреса** - проверить Server/config.json
2. **WinRM не настроен** - запустить Enable-PSRemoting на станциях
3. **Firewall блокирует** - открыть порт 5985 (WinRM)

**Проверка:**
```powershell
# Тест WinRM подключения
Test-WSMan -ComputerName 192.168.1.101
```

### Проблема: Latency очень высокий (>1000ms)
**Причины:**
1. Перегруженная сеть
2. Слабая станция (перегружен CPU)
3. Проблемы с DNS

**Решение:**
- Проверить сетевую нагрузку
- Уменьшить количество эмуляторов
- Перезагрузить станцию

### Проблема: Emulators count = 0, но станция ONLINE
**Причины:**
1. LDPlayer не запущен на станции
2. Неправильный путь к dnconsole.exe в config.json
3. Нет прав доступа к LDPlayer

**Решение:**
```bash
# Проверить путь в config.json
"ldconsole_path": "C:\\LDPlayer\\LDPlayer9\\dnconsole.exe"

# Запустить LDPlayer вручную на станции
```

---

## 📈 Метрики Performance

**Нормальные Значения:**
- **Latency:** 50-200 ms (локальная сеть)
- **Refresh time:** < 5 секунд для 8 станций
- **Memory usage:** ~100 MB

**Alert Conditions:**
- Latency > 1000 ms → Проблемы с сетью
- 3+ consecutive failures → Станция недоступна
- Emulators = 0 (long time) → LDPlayer не запущен

---

## 🔐 Security Notes

**Внимание:**
- Dashboard использует те же credentials, что и server (config.json)
- WinRM подключение не шифруется по умолчанию
- Для production: настроить HTTPS WinRM

**Рекомендации:**
- Запускать dashboard в защищённой сети
- Использовать firewall rules
- Регулярно обновлять пароли

---

## 📚 API Reference

### MonitoringWorker Class

**Сигналы:**
```python
status_updated = pyqtSignal(dict)
# Emit: {ws_id: {status, emulators, latency, error, last_check}}

error_occurred = pyqtSignal(str, str)
# Emit: (ws_id, error_message)
```

**Методы:**
```python
run()           # Main monitoring loop
stop()          # Stop monitoring gracefully
```

### MonitoringDashboard Class

**Публичные Методы:**
```python
start_monitoring()    # Start background worker
stop_monitoring()     # Stop background worker
manual_refresh()      # Force immediate refresh
add_log(message)      # Add entry to event log
update_status(dict)   # Update table with results
```

---

## 🎨 Customization

### Изменение Цветов Статусов
```python
STATUS_COLORS = {
    "online": QColor(46, 204, 113),      # Green
    "offline": QColor(231, 76, 60),      # Red
    "warning": QColor(241, 196, 15),     # Yellow
    "unknown": QColor(149, 165, 166),    # Gray
}
```

### Добавление Новых Колонок
```python
# В create_status_table():
table.setColumnCount(8)  # +1 column
table.setHorizontalHeaderLabels([
    ..., "CPU %", "Memory %"  # New columns
])
```

### Кастомные Alerts
```python
# В update_status():
if emulators > 15:
    self.show_alert(ws_id, f"Overload: {emulators} emulators")
```

---

## 📞 Support

**Проблемы?**
1. Проверить logs: `Server/logs/app.log`
2. Event log в dashboard
3. Документация: `PRODUCTION_GUIDE.md`

**Контакты:**
- GitHub: [Repository Issues]
- Logs: `Server/logs/`

---

## 🚀 Roadmap

### Планируемые Функции:
- [ ] **Charts** - Графики latency/emulators за время
- [ ] **Export** - Экспорт статусов в CSV/JSON
- [ ] **Notifications** - Desktop notifications для alerts
- [ ] **Remote Control** - Старт/стоп эмуляторов из dashboard
- [ ] **History** - История статусов за день/неделю

---

**Версия:** 1.0  
**Дата:** 2025-10-17  
**Автор:** LDPlayer Management System Team
