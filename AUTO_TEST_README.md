# 🧪 AUTO TEST - Автоматический тест всех функций

## 📋 Что тестируется

Скрипт `test_all_features.py` автоматически проверяет **ВСЕ** функции системы:

### ✅ Тесты (10 штук):

1. **Config Validation** - Валидация config.json
2. **Find LDPlayer Console** - Поиск dnconsole.exe
3. **List Emulators** - Получение списка эмуляторов (`dnconsole.exe list2`)
4. **Create Emulator** - Создание тестового эмулятора (`add --name AutoTest-XXX`)
5. **Start Emulator** - Запуск эмулятора (`launch --index X`)
6. **Rename Emulator** - Переименование (`rename --index X --title NewName`)
7. **Stop Emulator** - Остановка (`quit --index X`)
8. **Delete Emulator** - ❌ **ОТКЛЮЧЕНО** для безопасности
9. **Check Logs** - Проверка логов (app.log + errors.log)
10. **Update Config** - Обновление config.json с актуальными данными

---

## 🚀 Запуск

### Вариант 1: Быстрый запуск
```bash
RUN_AUTO_TEST.bat
```

### Вариант 2: Из командной строки
```bash
python test_all_features.py
```

### Вариант 3: Из PowerShell
```powershell
.\venv\Scripts\Activate.ps1
python test_all_features.py
```

---

## 📊 Пример вывода

```
╔════════════════════════════════════════════════════════════════════╗
║          🧪 LDPLAYER MANAGEMENT SYSTEM - AUTO TEST SUITE           ║
╚════════════════════════════════════════════════════════════════════╝

[08:03:16] ℹ️ Starting test suite at 2025-10-17 08:03:16
[08:03:16] ℹ️ Config: Server\config.json
[08:03:16] ℹ️ Test Workstation: ws_001

================================================================================
                           TEST 1: Config Validation
================================================================================

▶ Загрузка config.json...
✅ Config Load: PASS - Loaded 8 workstations
✅ Workstation Check: PASS - Found LOCAL - Development
✅ Required Fields: PASS - All required fields present

================================================================================
                             TEST 3: List Emulators
================================================================================

▶ Выполнение: dnconsole.exe list2...
✅ Execute Command: PASS
[08:03:18] ℹ️ Raw output:
0,Test-Emulator-1,0,0,720,1280,240,-1,-1
1,Instagram-Bot,1,1234,1080,1920,320,-1,-1

✅ Parse Output: PASS - Found 2 emulator(s)
[08:03:18] ℹ️   [0] Test-Emulator-1 🔴 stopped
[08:03:18] ℹ️   [1] Instagram-Bot 🟢 running

================================================================================
                                  TEST RESULTS
================================================================================

✅ PASSED:  5/10
❌ FAILED:  1/10
⏭️  SKIPPED: 4/10

⏱️  Time: 10.66s
```

---

## ⚙️ Конфигурация теста

В начале файла `test_all_features.py`:

```python
class AutoTest:
    def __init__(self):
        self.config_path = Path("Server/config.json")
        self.test_workstation = "ws_001"  # ← Меняй если нужна другая станция
        self.test_emulator_name = f"AutoTest-{int(time.time())}"
```

---

## 🔧 Если тесты падают

### Проблема 1: "WinError 740 - Требует повышения"

**Причина**: LDPlayer требует прав администратора  
**Решение**:
1. Запусти PowerShell/CMD **от администратора**
2. Или измени настройки UAC для LDPlayer

### Проблема 2: "dnconsole.exe not found"

**Причина**: LDPlayer не установлен или установлен в другую папку  
**Решение**: Добавь свой путь в `find_ldplayer_console()`:

```python
def find_ldplayer_console(self) -> str:
    paths = [
        r"C:\LDPlayer\LDPlayer9\dnconsole.exe",
        r"D:\Games\LDPlayer\dnconsole.exe",  # ← Добавь свой путь
    ]
```

### Проблема 3: "Create Emulator FAIL"

**Причина**: LDPlayer не может создать эмулятор (нет прав/места/лицензии)  
**Решение**: Это нормально! Остальные тесты всё равно пройдут

### Проблема 4: "No emulators found"

**Причина**: В LDPlayer нет эмуляторов  
**Решение**: Создай хотя бы 1 эмулятор вручную через LDPlayer GUI

---

## 🎯 Что проверяется в каждом тесте

### TEST 1: Config Validation ✅
- Файл config.json существует и валидный JSON
- Есть workstation с ID `ws_001`
- У workstation есть все обязательные поля: `id`, `name`, `ip_address`, `ldplayer_path`

### TEST 2: Find LDPlayer Console ✅
- dnconsole.exe найден в одном из стандартных путей
- Файл существует и доступен для чтения
- Размер файла > 0 байт

### TEST 3: List Emulators ✅
- Команда `dnconsole.exe list2` выполняется
- Вывод парсится корректно (формат CSV)
- Для каждого эмулятора извлекается: index, name, status, pid, resolution

### TEST 4: Create Emulator ⚠️
- Команда `dnconsole.exe add --name "AutoTest-XXX"` выполняется
- Эмулятор появляется в списке после создания
- Сохраняется index для дальнейших тестов

### TEST 5: Start Emulator ▶️
- Команда `dnconsole.exe launch --index X` выполняется
- Статус меняется на `running` через 10 секунд
- PID процесса не равен 0

### TEST 6: Rename Emulator ✏️
- Команда `dnconsole.exe rename --index X --title "NewName"` выполняется
- Имя меняется в списке эмуляторов

### TEST 7: Stop Emulator ⏹️
- Команда `dnconsole.exe quit --index X` выполняется
- Статус меняется на `stopped` через 5 секунд
- PID становится 0

### TEST 8: Delete Emulator ❌
- **ОТКЛЮЧЕН** для безопасности
- Не хотим удалять реальные эмуляторы автоматически
- Для включения раскомментируй код в `test_all_features.py`

### TEST 9: Check Logs 📝
- Файлы `Server/logs/app.log` и `errors.log` существуют
- Показывает последние 10 строк из app.log
- Показывает последние 5 ошибок если есть

### TEST 10: Update Config 💾
- Получает актуальный список эмуляторов
- Обновляет config.json с реальными данными
- Сохраняет файл в правильном формате (UTF-8, indent=2)

---

## 🔒 Безопасность

### ❌ Что НЕ делает тест:
- **НЕ удаляет** существующие эмуляторы (Test 8 отключен)
- **НЕ перезаписывает** config.json если нет изменений
- **НЕ запускает** эмуляторы если они уже запущены
- **НЕ трогает** эмуляторы не созданные тестом

### ✅ Что делает тест:
- Создаёт **ВРЕМЕННЫЙ** эмулятор с именем `AutoTest-{timestamp}`
- Запускает/останавливает **ТОЛЬКО** созданный эмулятор
- Переименовывает **ТОЛЬКО** созданный эмулятор
- В конце **ОСТАВЛЯЕТ** созданный эмулятор (не удаляет)

### 🗑️ Очистка после теста:
После теста у тебя останется эмулятор `AutoTest-XXXXXXXXXX-RENAMED`.  
Удали его вручную:
```bash
dnconsole.exe list2  # Узнай index
dnconsole.exe remove --index X  # Удали
```

Или через LDPlayer GUI.

---

## 📈 Интерпретация результатов

### ✅ Идеальный результат:
```
✅ PASSED:  10/10
❌ FAILED:  0/10
⏭️  SKIPPED: 0/10

🎉 ALL TESTS PASSED! 🎉
```

### ⚠️ Хороший результат (без LDPlayer):
```
✅ PASSED:  3/10    ← Config, Find Console, Logs
❌ FAILED:  1/10    ← Create (нет прав админа)
⏭️  SKIPPED: 6/10   ← Start/Stop/Rename/Delete (не было создания)
```
**Это нормально!** Значит config валидный, LDPlayer найден.

### ❌ Плохой результат:
```
✅ PASSED:  0/10
❌ FAILED:  5/10
⏭️  SKIPPED: 5/10
```
**Проблема!** Config невалидный или LDPlayer не найден.

---

## 🛠️ Кастомизация

### Изменить workstation для теста:
```python
self.test_workstation = "ws_002"  # Вместо ws_001
```

### Добавить свой путь к LDPlayer:
```python
LDPLAYER_PATHS = [
    r"C:\LDPlayer\LDPlayer9\dnconsole.exe",
    r"D:\MyGames\LDPlayer9\dnconsole.exe",  # ← Твой путь
]
```

### Увеличить timeout для медленных машин:
```python
success, stdout, stderr = self.execute_command(cmd, timeout=120)  # 2 минуты
```

### Включить удаление эмулятора:
В `test_08_delete_emulator()` раскомментируй весь код после `# ЗАКОММЕНТИРОВАНО ДЛЯ БЕЗОПАСНОСТИ:`

---

## 📊 Логи теста

Тест пишет детальные логи в консоль:

- 🔵 `[HH:MM:SS] ℹ️` - Информация
- 🟢 `[HH:MM:SS] ✅` - Успех
- 🟡 `[HH:MM:SS] ⚠️` - Предупреждение
- 🔴 `[HH:MM:SS] ❌` - Ошибка

Также показывает:
- Выполняемые команды полностью
- Вывод команд (stdout/stderr)
- Время выполнения каждого теста
- Общее время теста

---

## 🎯 Использование в CI/CD

Тест возвращает exit code:
- `0` - Все тесты прошли
- `1` - Есть упавшие тесты

Пример в GitHub Actions:
```yaml
- name: Run Auto Test
  run: |
    python test_all_features.py
  continue-on-error: false
```

---

## 💡 Tips & Tricks

### 1. Быстрая проверка только config:
Закомментируй все тесты кроме `test_01_config_validation`

### 2. Тест без создания эмулятора:
Закомментируй `test_04_create_emulator` и все последующие

### 3. Только список эмуляторов:
Оставь только `test_01`, `test_02`, `test_03`

### 4. Цветной вывод не работает:
Установи: `pip install colorama` и добавь в начало:
```python
from colorama import init
init()
```

### 5. Сохранить лог в файл:
```bash
python test_all_features.py > test_results.txt 2>&1
```

---

## 🔗 Связанные файлы

- `test_all_features.py` - Основной скрипт теста
- `RUN_AUTO_TEST.bat` - Быстрый запуск
- `Server/config.json` - Конфигурация (проверяется тестом)
- `Server/logs/app.log` - Логи приложения (проверяются тестом)
- `Server/logs/errors.log` - Логи ошибок (проверяются тестом)

---

## ✅ Checklist перед запуском

- [ ] LDPlayer установлен (не обязательно, но лучше)
- [ ] config.json существует и валидный
- [ ] Python venv активирован
- [ ] У тебя есть права админа (для создания эмулятора)
- [ ] Достаточно места на диске (для нового эмулятора ~500MB)

---

**ГОТОВО!** Запускай и смотри красивые логи! 🎉
