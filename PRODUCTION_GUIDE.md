# 🚀 PRODUCTION ИНСТРУКЦИЯ - Управление 8 рабочими станциями

## ⚡ ОБНОВЛЕНИЕ (2025-10-17)

### ✅ Новые улучшения системы:

1. **Retry Mechanism** - Автоматические повторные попытки при сбоях
   - 3 попытки с экспоненциальной задержкой (2-10 секунд)
   - Работает для ConnectionError, TimeoutError, OSError
   - Timeout: 30s для команд, 60s для ldconsole

2. **Input Validation** - Валидация всех входных данных
   - Проверка существования workstation_id
   - Проверка уникальности имён эмуляторов
   - HTTP коды: 404 (не найдено), 400 (некорректные данные), 500 (ошибка)

3. **Log Rotation** - Автоматическая ротация логов
   - Max размер: 10MB на файл
   - 5 архивных копий
   - UTF-8 encoding

4. **Code Quality** - Уменьшено дублирование кода
   - Декоратор `@handle_api_errors()` для унифицированной обработки ошибок
   - Utility функции для валидации
   - Чище и читабельнее код

---

## 📋 ЛОГИКА РАБОТЫ

### Архитектура:

```
┌─────────────────────────────┐
│    СЕРВЕРНЫЙ ПК (ТВОЙ)      │
│                             │
│  📂 app_production.py       │
│  📂 Server/config.json      │
│  📂 Server/logs/app.log     │
│  📂 Server/logs/errors.log  │
└──────────┬──────────────────┘
           │
           │ WinRM / PowerShell Remoting
           │
    ┌──────┴────────┬─────────┬─────────┬─────────┐
    ▼              ▼         ▼         ▼         ▼
┌─────────┐   ┌─────────┐  ...    ┌─────────┐
│ СТАНЦИЯ1│   │ СТАНЦИЯ2│         │ СТАНЦИЯ8│
│ 192.168.│   │ 192.168.│         │ 192.168.│
│ 0.51    │   │ 0.52    │         │ 0.58    │
├─────────┤   ├─────────┤         ├─────────┤
│LDPlayer9│   │LDPlayer9│         │LDPlayer9│
│         │   │         │         │         │
│ Эму 1   │   │ Эму 1   │         │ Эму 1   │
│ Эму 2   │   │ Эму 2   │         │ Эму 2   │
│ Эму 3   │   │ Эму 3   │         │ Эму 3   │
└─────────┘   └─────────┘         └─────────┘
```

---

## 🔍 ПРОЦЕСС СКАНИРОВАНИЯ РАБОЧИХ СТАНЦИЙ

### Шаг 1: Подготовка рабочих станций

На КАЖДОЙ из 8 рабочих станций нужно:

1. **Установить LDPlayer9**:
   - По умолчанию: `C:\LDPlayer\LDPlayer9`
   - Убедись, что есть файл: `C:\LDPlayer\LDPlayer9\dnconsole.exe`

2. **Включить WinRM** (PowerShell Remoting):
   ```powershell
   # На каждой станции выполни (от Администратора):
   Enable-PSRemoting -Force
   Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
   Restart-Service WinRM
   ```

3. **Настроить Firewall**:
   ```powershell
   # Разрешить WinRM
   New-NetFirewallRule -DisplayName "WinRM" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow
   ```

4. **Создать учётную запись** (если нужно):
   ```powershell
   # Или используй существующего пользователя Administrator
   net user ldplayer YourPassword123! /add
   net localgroup Administrators ldplayer /add
   ```

---

### Шаг 2: Настройка config.json

Отредактируй `Server/config.json` и добавь свои 8 станций:

```json
{
  "workstations": [
    {
      "id": "ws_001",
      "name": "Станция 1 - Основная",
      "ip_address": "192.168.0.51",
      "username": "Administrator",
      "password": "YourPassword123!",
      "ldplayer_path": "C:\\LDPlayer\\LDPlayer9\\dnconsole.exe",
      "emulators": []
    },
    {
      "id": "ws_002",
      "name": "Станция 2 - Резервная",
      "ip_address": "192.168.0.52",
      "username": "Administrator",
      "password": "YourPassword123!",
      "ldplayer_path": "C:\\LDPlayer\\LDPlayer9\\dnconsole.exe",
      "emulators": []
    }
    // ... добавь остальные 6 станций
  ]
}
```

---

## ⚙️ КАК РАБОТАЕТ СКАНИРОВАНИЕ

### Автоматическое сканирование:

1. **Запусти приложение**: `python app_production.py` или `RUN_PRODUCTION.bat`

2. **Перейди на вкладку "💻 Workstations"**

3. **Нажми "🔍 Scan All Workstations"**

4. **Что происходит**:
   ```
   ┌─────────────────────────────────────────┐
   │ ДЛЯ КАЖДОЙ СТАНЦИИ:                     │
   ├─────────────────────────────────────────┤
   │ 1. Подключение по WinRM                 │
   │    → Invoke-Command -ComputerName IP    │
   │                                         │
   │ 2. Выполнение команды удалённо:         │
   │    → cd C:\LDPlayer\LDPlayer9           │
   │    → .\dnconsole.exe list2              │
   │                                         │
   │ 3. Получение вывода (пример):           │
   │    0,Instagram-Bot-1,1,1234,720,1280,...│
   │    1,Facebook-Bot-2,0,0,1080,1920,...   │
   │    2,WhatsApp-Bot-3,1,5678,720,1280,... │
   │                                         │
   │ 4. Парсинг каждой строки:               │
   │    → index = 0                          │
   │    → name = "Instagram-Bot-1"           │
   │    → status = running (1) / stopped (0) │
   │    → pid = 1234                         │
   │    → resolution = 720x1280              │
   │                                         │
   │ 5. Сохранение в config.json:            │
   │    → workstations[0].emulators = [...]  │
   │                                         │
   │ 6. Обновление UI таблицы                │
   └─────────────────────────────────────────┘
   ```

5. **Результат**:
   - Все эмуляторы со всех 8 станций появятся в таблицах
   - config.json обновится автоматически
   - В логах увидишь детали: `Server/logs/app.log`

---

## 🎮 УПРАВЛЕНИЕ ЭМУЛЯТОРАМИ

### Создание:

1. Вкладка "📱 Emulators"
2. Выбери станцию из списка
3. Нажми "➕ Create"
4. Заполни форму:
   - **Name**: Instagram-Bot-4
   - **CPU Cores**: 4
   - **RAM**: 4096 MB
   - **Resolution**: 1080x1920

**Что происходит**:
```powershell
# На удалённой станции выполнится:
dnconsole.exe add --name "Instagram-Bot-4" --cpu 4 --memory 4096 --resolution 1080 1920
```

---

### Старт эмулятора:

1. Выбери эмулятор в таблице
2. Нажми "▶️ Start"

**Что происходит**:
```powershell
# На удалённой станции:
dnconsole.exe launch --index 0
```

---

### Стоп:

```powershell
dnconsole.exe quit --index 0
```

---

### Переименование:

```powershell
dnconsole.exe rename --index 0 --title "NewName"
```

---

### Удаление:

```powershell
dnconsole.exe remove --index 0
```

---

### Настройки (CPU/RAM/Resolution):

```powershell
dnconsole.exe modify --index 0 --cpu 8 --memory 8192 --resolution 1440 2560
```

---

## 📝 ЛОГИРОВАНИЕ

### Детальные логи:

**Основной лог** (`Server/logs/app.log`):
```
[2025-10-17 07:17:43.656] ℹ️ INFO: 🚀 STARTING LDPLAYER MANAGEMENT SYSTEM
[2025-10-17 07:17:43.678] ℹ️ INFO: 📂 Loading config from Server\config.json
[2025-10-17 07:17:43.679] ✅ SUCCESS: Config loaded: 8 workstations
[2025-10-17 07:18:05.123] ℹ️ INFO: 🔍 Starting scan of 192.168.0.51...
[2025-10-17 07:18:05.456] ℹ️ INFO: 🎮 Executing command 'launch' on ws_001
[2025-10-17 07:18:05.789] 🔍 DEBUG: Command: "C:\LDPlayer\LDPlayer9\dnconsole.exe" launch --index 0
[2025-10-17 07:18:06.123] ✅ SUCCESS: Command 'launch' executed successfully
```

**Лог ошибок** (`Server/logs/errors.log`):
- Только ошибки и предупреждения
- С полными traceback'ами
- Для отладки проблем

---

## 🔧 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Проблема 1: "Приложение крашится при нажатии кнопок"

**Решение**:
1. Проверь логи: `Server/logs/app.log` и `Server/logs/errors.log`
2. Там будет точная причина с traceback
3. Пришли мне последние 50 строк лога

---

### Проблема 2: "Scan не находит эмуляторы"

**Проверь**:
1. **На рабочей станции** выполни вручную:
   ```powershell
   cd C:\LDPlayer\LDPlayer9
   .\dnconsole.exe list2
   ```
   
2. Если вывод пустой → эмуляторов нет, создай их в LDPlayer GUI

3. Если ошибка → проверь путь `ldplayer_path` в config.json

---

### Проблема 3: "WinRM connection failed"

**Проверь**:
1. **На сервере** (твой ПК):
   ```powershell
   Test-WSMan -ComputerName 192.168.0.51
   ```
   
   Должно вернуть XML с версией WinRM

2. **На рабочей станции** проверь:
   ```powershell
   Get-Service WinRM
   # Должно быть: Status = Running
   ```

3. **Firewall**: порт 5985 TCP открыт?

---

### Проблема 4: "Access Denied"

**Решение**:
1. Проверь username/password в config.json
2. Убедись, что пользователь в группе Administrators
3. Попробуй вручную подключиться:
   ```powershell
   $cred = Get-Credential
   Invoke-Command -ComputerName 192.168.0.51 -Credential $cred -ScriptBlock { hostname }
   ```

---

## 📊 МОНИТОРИНГ

### Dashboard показывает:

- **Total Workstations**: Сколько станций в config.json
- **Total Emulators**: Сумма эмуляторов со всех станций
- **🟢 Running**: Сколько запущено
- **🔴 Stopped**: Сколько остановлено

### Auto-Refresh:

- Обновляется каждые 30 секунд автоматически
- Можно вручную нажать "🔄 Refresh Stats"

---

## 🚀 БЫСТРЫЙ СТАРТ

1. **Первый запуск**:
   ```bash
   RUN_PRODUCTION.bat
   ```

2. **Настрой config.json** с твоими 8 станциями

3. **Scan All** → получишь список всех эмуляторов

4. **Управляй** через кнопки Create/Start/Stop/Rename/Delete

5. **Смотри логи** на вкладке "📝 Logs"

---

## 📞 ПОДДЕРЖКА

Если вылетает или не работает:

1. **Проверь логи**:
   - `Server/logs/app.log` - основной
   - `Server/logs/errors.log` - ошибки

2. **Пришли мне**:
   - Последние 50 строк из `app.log`
   - Что именно делал (какую кнопку нажал)
   - Скриншот ошибки (если есть диалог)

3. **Я исправлю** в течение 10 минут! 😊

---

## ✅ CHECKLIST ПЕРЕД ИСПОЛЬЗОВАНИЕМ

- [ ] LDPlayer9 установлен на всех 8 станциях
- [ ] WinRM включен на всех станциях (`Enable-PSRemoting`)
- [ ] Firewall разрешает порт 5985 TCP
- [ ] config.json содержит все 8 станций с правильными IP/паролями
- [ ] Тестовое подключение работает (`Test-WSMan -ComputerName IP`)
- [ ] На станциях есть хотя бы 1 эмулятор (для теста)
- [ ] Приложение запускается без ошибок
- [ ] Логи пишутся в `Server/logs/app.log`

---

**ГОТОВО! ЗАПУСКАЙ!** 🚀
