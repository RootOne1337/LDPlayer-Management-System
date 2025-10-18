# 🚀 Быстрый запуск сервера

## Требования

- **Python 3.8+**
- **Windows 10/11** (для центрального сервера)
- **LDPlayer 9** на рабочих станциях
- **Сетевой доступ** к рабочим станциям

## Установка

### 1. Клонировать проект
```bash
git clone <repository_url>
cd LDPlayerManagementSystem/Server
```

### 2. Установить зависимости
```bash
# Вариант 1: Через setup.py (рекомендуется)
python setup.py

# Вариант 2: Вручную
pip install -r requirements.txt
```

### 3. Настроить конфигурацию
```bash
# Создать файл конфигурации по умолчанию
python run.py --create-config

# Или отредактировать существующий config.json
notepad config.json
```

## Настройка рабочих станций

В файле `config.json` измените:

```json
{
  "workstations": [
    {
      "id": "ws_001",
      "name": "Рабочая станция 1",
      "ip_address": "192.168.1.101",
      "username": "administrator",
      "password": "ваш_пароль"
    }
    // ... остальные станции
  ]
}
```

## Запуск сервера

### Режим разработки
```bash
python run.py --debug --reload
```

### Продакшн режим
```bash
python run.py --host 0.0.0.0 --port 8000
```

### С параметрами
```bash
# Проверка подключений
python run.py --test-connections

# Список рабочих станций
python run.py --list-workstations

# Создание резервных копий
python run.py --backup-configs
```

## Доступ к API

После запуска сервер доступен по адресам:

- **API документация:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8001/ws
- **Здоровье сервера:** http://localhost:8000/api/health

## Тестирование

```bash
# Запустить все тесты
python test_server.py

# Тестирование конкретных компонентов
python -c "from src.core.config import get_config; print('Конфигурация загружена')"
```

## Рабочие станции

На каждой рабочей станции должны быть:

1. **LDPlayer 9** установлен в `C:\LDPlayer\LDPlayer9.0\`
2. **WinRM** включен для удаленного управления
3. **SMB** доступен для файловых операций
4. **PowerShell Remoting** разрешен

### Включение WinRM на рабочих станциях
```powershell
# Запустить на каждой рабочей станции от имени администратора
winrm quickconfig
Enable-PSRemoting -Force
```

## Мониторинг

Сервер автоматически логирует все операции в:
- `logs/server.log` - основной лог сервера
- `logs/workstations.log` - логи рабочих станций
- `logs/emulators.log` - логи эмуляторов

## Команды LDPlayer

Основные команды для управления эмуляторами:

```bash
# Создание эмулятора
POST /api/emulators
{
  "name": "Test Emulator",
  "workstation_id": "ws_001",
  "config": {
    "android_version": "9.0",
    "screen_size": "1280x720",
    "cpu_cores": 2,
    "memory_mb": 2048
  }
}

# Запуск эмулятора
POST /api/emulators/{emulator_id}/start

# Остановка эмулятора
POST /api/emulators/{emulator_id}/stop

# Удаление эмулятора
DELETE /api/emulators/{emulator_id}
```

## Поддержка

При возникновении проблем:

1. Проверьте логи в папке `logs/`
2. Запустите `python test_server.py` для диагностики
3. Убедитесь в доступности рабочих станций
4. Проверьте настройки в `config.json`

## Структура проекта

```
Server/
├── src/                    # Исходный код
│   ├── core/              # Ядро системы
│   ├── remote/            # Удаленное управление
│   └── utils/             # Утилиты
├── config.json            # Конфигурация
├── requirements.txt       # Зависимости
├── run.py                 # Запуск сервера
├── test_server.py         # Тестирование
└── setup.py               # Установка
```

## Следующие шаги

После успешного запуска сервера:

1. ✅ Сервер работает на порту 8000
2. 🔄 Настроить WPF клиент (следующая фаза)
3. 🎨 Создать красивый интерфейс управления
4. 📊 Добавить мониторинг и уведомления

---

*Дата последнего обновления: 16 октября 2024 г.*
*Версия: 1.0*