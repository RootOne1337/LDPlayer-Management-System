# 🔍 СВЕРХ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ - Руководство

## Обзор

Система теперь логирует **АБСОЛЮТНО ВСЁ** с максимальной детализацией для удалённой диагностики:

- ⏱️ **Точное время** (с миллисекундами)
- 📍 **Точное место** (файл:строка:функция)
- 👤 **Кто** (пользователь, IP, User-Agent)
- 📊 **Что** (входные данные, результаты)
- ⚡ **Сколько** (время выполнения в мс)
- 🚨 **Ошибки** (полный stack trace)
- 🔐 **Безопасность** (без паролей в логах!)

---

## 📂 Где находятся логи?

### Основной файл логов
```
Server/logs/server.log
```

### Ротация логов
- **Максимальный размер:** 10 MB
- **Количество бэкапов:** 5
- **Старые логи:** server.log.1, server.log.2, ..., server.log.5

---

## 🎨 Формат логов

### Новый детальный формат
```
ДАТА ВРЕМЯ.миллисекунды | УРОВЕНЬ  | КАТЕГОРИЯ      | файл.py:строка:функция() | СООБЩЕНИЕ
2025-10-17 15:30:45.123 | INFO     | api            | server.py:234:create_emulator() | 🚀 CALL create_emulator() | args=['Test'] | kwargs={'config': {...}}
```

### Компоненты
1. **Timestamp:** `2025-10-17 15:30:45.123` - точное время с миллисекундами
2. **Level:** `INFO`, `WARNING`, `ERROR` - уровень важности
3. **Category:** `api`, `workstation`, `emulator`, `security` - категория события
4. **Location:** `server.py:234:create_emulator()` - где произошло
5. **Message:** подробное описание события

---

## 📋 Примеры логов

### 1. Вход в систему (SUCCESS)

```log
2025-10-17 15:30:45.123 | WARNING  | security       | auth_routes.py:120:login() | 🔓 AUTH SUCCESS | user=admin | ip=192.168.1.100 | user_agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)... | reason=N/A

2025-10-17 15:30:45.125 | INFO     | api            | auth_routes.py:142:login() | ✅ Login SUCCESS: admin (role: UserRole.ADMIN) from 192.168.1.100
```

### 2. Вход в систему (FAILED)

```log
2025-10-17 15:31:12.456 | WARNING  | security       | auth_routes.py:108:login() | 🔒 AUTH FAILED | user=hacker | ip=10.0.0.50 | user_agent=curl/7.68.0 | reason=Invalid username or password

2025-10-17 15:31:12.458 | WARNING  | api            | auth_routes.py:114:login() | ❌ Login FAILED: hacker from 10.0.0.50
```

### 3. HTTP запрос

```log
2025-10-17 15:32:01.789 | INFO     | api            | detailed_logging.py:185:log_http_request() | 🌐 HTTP POST /api/emulators | client=192.168.1.100 | user=authenticated | headers={'authorization': '***HIDDEN***', 'content-type': 'application/json'} | body={'name': 'Test Emulator', 'workstation_id': 'ws_001', 'config': {'cpu_cores': 2, 'memory_mb': 2048}}
```

### 4. HTTP ответ

```log
2025-10-17 15:32:02.123 | INFO     | api            | detailed_logging.py:207:log_http_response() | ✅ HTTP RESPONSE 200 | duration=334.56ms | body={'success': True, 'message': 'Emulator created', 'data': {...}}
```

### 5. Вызов функции (SUCCESS)

```log
2025-10-17 15:32:01.800 | INFO     | api            | detailed_logging.py:48:async_wrapper() | 🚀 CALL src.core.server.create_emulator() | args=[] | kwargs={'emulator_data': {'name': 'Test Emulator', 'workstation_id': 'ws_001'}, 'current_user': <UserInDB object>}

2025-10-17 15:32:02.110 | INFO     | api            | detailed_logging.py:62:async_wrapper() | ✅ SUCCESS src.core.server.create_emulator() | duration=310.45ms | result={'success': True, 'message': '...', 'data': {...}}
```

### 6. Вызов функции (ERROR)

```log
2025-10-17 15:33:15.234 | INFO     | workstation    | detailed_logging.py:48:async_wrapper() | 🚀 CALL src.remote.workstation.connect_to_workstation() | args=['ws_999'] | kwargs={}

2025-10-17 15:33:20.567 | ERROR    | workstation    | detailed_logging.py:71:async_wrapper() | ❌ ERROR src.remote.workstation.connect_to_workstation() | duration=5333.12ms | error=ConnectionError: Connection timeout
Stack trace:
Traceback (most recent call last):
  File "C:\...\workstation.py", line 123, in connect_to_workstation
    connection = await asyncio.wait_for(...)
  File "C:\...\asyncio\tasks.py", line 456, in wait_for
    raise asyncio.TimeoutError()
asyncio.TimeoutError

During handling of the above exception, another exception occurred:
...
ConnectionError: Connection timeout
```

### 7. Операция с эмулятором

```log
2025-10-17 15:34:00.123 | INFO     | emulator       | detailed_logging.py:379:log_emulator_operation() | ▶️ EMULATOR START SUCCESS | name=Test Emulator | id=emu_001 | ws=ws_001 | duration=2345.67ms | error=N/A

2025-10-17 15:34:05.456 | INFO     | emulator       | detailed_logging.py:379:log_emulator_operation() | ⏸️ EMULATOR STOP SUCCESS | name=Test Emulator | id=emu_001 | ws=ws_001 | duration=1234.56ms | error=N/A

2025-10-17 15:34:10.789 | INFO     | emulator       | detailed_logging.py:379:log_emulator_operation() | 🗑️ EMULATOR DELETE SUCCESS | name=Test Emulator | id=emu_001 | ws=ws_001 | duration=987.65ms | error=N/A
```

### 8. Подключение к workstation

```log
2025-10-17 15:35:00.111 | INFO     | workstation    | detailed_logging.py:348:log_workstation_connection() | 🔌 CONNECT SUCCESS | ws=ws_001 | ip=192.168.1.101 | error=N/A

2025-10-17 15:35:30.222 | INFO     | workstation    | detailed_logging.py:348:log_workstation_connection() | 🔌 DISCONNECT SUCCESS | ws=ws_001 | ip=192.168.1.101 | error=N/A
```

### 9. Проверка прав доступа (DENIED)

```log
2025-10-17 15:36:00.333 | WARNING  | security       | detailed_logging.py:321:log_permission_check() | ❌ PERMISSION DENIED | user=viewer | role=VIEWER | required=OPERATOR | resource=/api/emulators
```

### 10. Проверка прав доступа (ALLOWED)

```log
2025-10-17 15:36:05.444 | WARNING  | security       | detailed_logging.py:321:log_permission_check() | ✅ PERMISSION ALLOWED | user=admin | role=ADMIN | required=OPERATOR | resource=/api/emulators
```

### 11. Вызов внешнего API (LDPlayer)

```log
2025-10-17 15:37:00.555 | INFO     | workstation    | detailed_logging.py:255:log_external_api_call() | 🔌 EXTERNAL API LDPlayer | command=dnconsole.exe list2 | target=ws_001 | duration=456.78ms | result=[{'id': 0, 'name': 'Test', 'status': 'running'}, ...]
```

---

## 🎯 Как использовать для диагностики

### Найти ошибку
```powershell
# Найти все ошибки за последний час
Get-Content Server/logs/server.log | Select-String "ERROR" | Select-Object -Last 50

# Найти конкретную ошибку
Get-Content Server/logs/server.log | Select-String "ConnectionError"
```

### Найти действия пользователя
```powershell
# Все действия пользователя admin
Get-Content Server/logs/server.log | Select-String "user=admin"

# Все попытки входа
Get-Content Server/logs/server.log | Select-String "AUTH"
```

### Найти медленные запросы
```powershell
# Запросы длительнее 1000ms
Get-Content Server/logs/server.log | Select-String "duration=[1-9][0-9]{3,}\."
```

### Найти действия с конкретным эмулятором
```powershell
# Все операции с эмулятором emu_001
Get-Content Server/logs/server.log | Select-String "id=emu_001"
```

### Найти проблемы с workstation
```powershell
# Все события workstation ws_001
Get-Content Server/logs/server.log | Select-String "ws=ws_001"

# Ошибки подключения
Get-Content Server/logs/server.log | Select-String "CONNECT FAILED"
```

---

## 🔐 Безопасность логов

### Что НЕ логируется (скрывается)
- ❌ Пароли (`password`, `hashed_password`)
- ❌ JWT токены (`token`, `access_token`, `refresh_token`)
- ❌ API ключи (`api_key`, `secret_key`)
- ❌ Authorization headers (показывается как `***HIDDEN***`)

### Пример безопасного логирования
```log
# Вместо:
kwargs={'password': 'admin123', 'username': 'admin'}

# Логируется:
kwargs={'password': '***HIDDEN***', 'username': 'admin'}
```

---

## 📊 Категории логов

| Категория | Описание | Примеры событий |
|-----------|----------|----------------|
| `api` | API запросы/ответы | HTTP POST /api/emulators |
| `security` | Безопасность | Вход, проверка прав |
| `workstation` | Workstation операции | Подключение, команды |
| `emulator` | Эмулятор операции | Старт, стоп, создание |
| `system` | Системные события | Запуск сервера, shutdown |
| `operation` | Длительные операции | Клонирование, бэкап |
| `monitoring` | Мониторинг | Проверки здоровья |

---

## ⚡ Производительность

### Overhead логирования
- **Минимальный:** ~0.1-0.5 мс на запись
- **Файловый I/O:** Асинхронный, не блокирует
- **Ротация:** Автоматическая при 10 MB

### Рекомендации
1. **Development:** Уровень `DEBUG` - всё логируется
2. **Production:** Уровень `INFO` - только важные события
3. **Troubleshooting:** Временно `DEBUG` для детальной диагностики

---

## 🛠️ Настройка уровня логирования

### В .env файле
```ini
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Уровни детализации

#### DEBUG (максимум деталей)
```log
- Все вызовы функций
- Все параметры
- Все результаты
- Все SQL запросы
- Все внешние API вызовы
```

#### INFO (стандарт для production)
```log
- HTTP запросы/ответы
- Успешные операции
- Аутентификация
- Важные события
```

#### WARNING (только проблемы)
```log
- Неудачные попытки входа
- Отказы в доступе
- Медленные запросы
```

#### ERROR (только ошибки)
```log
- Исключения
- Ошибки подключения
- Неудачные операции
```

---

## 📖 Типовые сценарии

### Сценарий 1: "Не могу войти в систему"

**Что смотреть:**
1. Найти попытки входа: `Select-String "AUTH"`
2. Проверить IP адрес
3. Проверить причину отказа
4. Проверить существование пользователя

**Пример:**
```log
2025-10-17 15:30:00.000 | WARNING | security | 🔒 AUTH FAILED | user=admin | reason=Invalid password
```

### Сценарий 2: "Эмулятор не запускается"

**Что смотреть:**
1. Найти операции эмулятора: `Select-String "EMULATOR START"`
2. Проверить workstation подключение
3. Проверить команду LDPlayer
4. Проверить stack trace

**Пример:**
```log
2025-10-17 15:31:00.000 | ERROR | emulator | ❌ EMULATOR START FAILED | id=emu_001 | error=LDPlayer not responding
```

### Сценарий 3: "Медленная работа"

**Что смотреть:**
1. Найти медленные запросы: `Select-String "duration=[1-9][0-9]{3}"`
2. Проверить время выполнения операций
3. Проверить внешние API вызовы

**Пример:**
```log
2025-10-17 15:32:00.000 | INFO | api | ✅ SUCCESS | duration=5678.90ms
```

### Сценарий 4: "Ошибка подключения к workstation"

**Что смотреть:**
1. Найти подключения: `Select-String "CONNECT"`
2. Проверить IP и доступность
3. Проверить timeout

**Пример:**
```log
2025-10-17 15:33:00.000 | INFO | workstation | 🔌 CONNECT FAILED | ws=ws_999 | ip=192.168.1.999 | error=Connection timeout
```

---

## 🚀 Быстрая диагностика

### PowerShell команды для удалённого анализа

```powershell
# 1. Последние 50 ошибок
Get-Content Server/logs/server.log | Select-String "ERROR" | Select-Object -Last 50

# 2. Все события за последние 5 минут (примерно)
Get-Content Server/logs/server.log | Select-Object -Last 1000

# 3. Статистика по категориям
Get-Content Server/logs/server.log | Select-String -Pattern "\| (\w+) \|" | Group-Object {$_.Matches[0].Groups[1].Value} | Sort-Object Count -Descending

# 4. Топ-10 самых медленных запросов
Get-Content Server/logs/server.log | Select-String "duration=(\d+\.\d+)ms" | ForEach-Object { [PSCustomObject]@{Line=$_.Line; Duration=[double]$_.Matches[0].Groups[1].Value} } | Sort-Object Duration -Descending | Select-Object -First 10

# 5. Все неудачные попытки входа
Get-Content Server/logs/server.log | Select-String "AUTH FAILED"

# 6. Проверить здоровье всех workstations
Get-Content Server/logs/server.log | Select-String "workstation" | Select-Object -Last 20
```

---

## 💡 Советы

1. **Регулярно проверяйте логи** - даже если всё работает
2. **Архивируйте старые логи** - они могут понадобиться позже
3. **Используйте grep/Select-String** - быстрый поиск
4. **Обращайте внимание на duration** - выявляйте узкие места
5. **Мониторьте AUTH FAILED** - возможные атаки
6. **Проверяйте stack trace** - точная причина ошибок

---

## 📞 Поддержка

При возникновении проблем **всегда присылайте логи**:

```powershell
# Скопировать последние 1000 строк логов
Get-Content Server/logs/server.log | Select-Object -Last 1000 | Out-File diagnostic_logs.txt
```

---

**Версия:** 1.0.0  
**Обновлено:** 2025-10-17  
**Статус:** ✅ Активно
