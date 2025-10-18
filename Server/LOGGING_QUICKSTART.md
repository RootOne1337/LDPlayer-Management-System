# 🔍 ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ - Быстрый старт

## ✅ Всё готово к работе!

Система автоматически логирует **ВСЁ** с максимальной детализацией.

---

## 📂 Где логи?

```
Server/logs/server.log
```

---

## 🎯 Быстрая диагностика (PowerShell)

### 1. Последние ошибки
```powershell
Get-Content Server/logs/server.log | Select-String "ERROR" | Select-Object -Last 20
```

### 2. Последние события
```powershell
Get-Content Server/logs/server.log | Select-Object -Last 50
```

### 3. Найти действия пользователя
```powershell
Get-Content Server/logs/server.log | Select-String "user=admin"
```

### 4. Неудачные попытки входа
```powershell
Get-Content Server/logs/server.log | Select-String "AUTH FAILED"
```

### 5. Медленные запросы (>1 сек)
```powershell
Get-Content Server/logs/server.log | Select-String "duration=[1-9][0-9]{3,}\."
```

### 6. Операции с эмулятором
```powershell
Get-Content Server/logs/server.log | Select-String "EMULATOR"
```

### 7. Проблемы с подключением
```powershell
Get-Content Server/logs/server.log | Select-String "CONNECT FAILED"
```

---

## 📊 Формат логов

```
ВРЕМЯ.мс | УРОВЕНЬ | КАТЕГОРИЯ | файл:строка:функция | СООБЩЕНИЕ
```

**Пример:**
```
2025-10-17 15:30:45.123 | INFO | api | server.py:234:create_emulator() | ✅ SUCCESS | duration=310ms
```

---

## 🎨 Эмодзи в логах

| Эмодзи | Значение |
|--------|----------|
| 🚀 | Вызов функции |
| ✅ | Успех |
| ❌ | Ошибка |
| 🌐 | HTTP запрос |
| 🔓 | Успешный вход |
| 🔒 | Неудачный вход |
| 🔌 | Подключение к workstation |
| ▶️ | Запуск эмулятора |
| ⏸️ | Остановка эмулятора |
| 🗑️ | Удаление эмулятора |
| ➕ | Создание |
| ✏️ | Изменение |

---

## 🔍 Что логируется?

### Автоматически логируется:
- ✅ Все HTTP запросы (метод, URL, параметры, IP, пользователь)
- ✅ Все HTTP ответы (статус, время, результат)
- ✅ Все попытки входа (успешные и неудачные)
- ✅ Все проверки прав доступа
- ✅ Все операции с эмуляторами (старт, стоп, создание, удаление)
- ✅ Все подключения к workstation
- ✅ Все внешние API вызовы (LDPlayer, WinRM)
- ✅ Все ошибки (с полным stack trace!)
- ✅ Время выполнения каждой операции

### Безопасность:
- ❌ Пароли НЕ логируются (показывается `***HIDDEN***`)
- ❌ JWT токены НЕ логируются
- ❌ API ключи НЕ логируются

---

## 🚨 Типичные проблемы

### "Не могу войти"
```powershell
# Смотрим последние попытки входа
Get-Content Server/logs/server.log | Select-String "AUTH" | Select-Object -Last 10
```

**Ищем:**
- `🔒 AUTH FAILED` - неправильный пароль
- `user=admin` - правильное ли имя пользователя

---

### "Эмулятор не запускается"
```powershell
# Смотрим операции с эмуляторами
Get-Content Server/logs/server.log | Select-String "EMULATOR START" | Select-Object -Last 5
```

**Ищем:**
- `❌ EMULATOR START FAILED`
- `error=...` - причина ошибки
- `duration=...` - долго ли выполнялось

---

### "Не подключается к workstation"
```powershell
# Смотрим подключения
Get-Content Server/logs/server.log | Select-String "CONNECT" | Select-Object -Last 10
```

**Ищем:**
- `🔌 CONNECT FAILED`
- `error=Connection timeout` - не доступна
- `ip=192.168.1.xxx` - правильный ли IP

---

## 📞 При обращении за помощью

**Всегда присылайте последние 1000 строк логов:**

```powershell
# Экспорт логов для диагностики
Get-Content Server/logs/server.log | Select-Object -Last 1000 | Out-File diagnostic.txt

# Отправь файл diagnostic.txt
```

---

## 🛠️ Настройка

### Уровень детализации (.env)
```ini
LOG_LEVEL=INFO  # DEBUG для максимума деталей
```

- **DEBUG** - максимум информации (для диагностики)
- **INFO** - стандарт (для production)
- **WARNING** - только проблемы
- **ERROR** - только ошибки

---

## 💡 Совет

**Перед запуском на удалённом ПК:**
1. Проверь что `Server/logs/` папка существует
2. Установи `LOG_LEVEL=DEBUG` в `.env`
3. Запусти сервер
4. Сделай несколько тестовых операций
5. Проверь `server.log` - должны быть детальные логи

---

## 📖 Полная документация

Смотри: `Server/DETAILED_LOGGING_GUIDE.md` (полное руководство с примерами)

---

**Версия:** 1.0.0  
**Готово к production:** ✅  
**Status:** АКТИВНО
