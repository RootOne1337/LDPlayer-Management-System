# 🚀 БЫСТРЫЙ СТАРТ - 3 МИНУТЫ

## Шаг 1: Запустить сервер

### Вариант A: Через BAT файл (рекомендуется)
```
Дважды кликнуть: Server\start_server.bat
```

### Вариант B: Через командную строку
```bash
cd Server
python run_production.py
```

---

## Шаг 2: Открыть Swagger UI
```
Браузер: http://localhost:8000/docs
```

---

## Шаг 3: Протестировать API

### В Swagger UI:

1. **GET /api/health** - Проверить работу сервера
2. **GET /api/workstations** - Список рабочих станций (8 шт.)
3. **GET /api/workstations/localhost/emulators** - Эмуляторы (2 шт.)

---

## 📋 Быстрые команды

### Получить список эмуляторов (PowerShell):
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health"
```

### Создать эмулятор (curl):
```bash
curl -X POST "http://localhost:8000/api/workstations/localhost/emulators" \
  -H "Content-Type: application/json" \
  -d '{"name":"test","config":{"cpu":2,"memory":4096}}'
```

### Запустить эмулятор nifilim:
```bash
curl -X POST "http://localhost:8000/api/workstations/localhost/emulators/1/start"
```

---

## ✅ Что должно работать

- ✅ Сервер запущен на порту 8000
- ✅ Swagger UI доступен
- ✅ Health check возвращает 200 OK
- ✅ 2 эмулятора: LDPlayer (0), nifilim (1)
- ✅ 8 workstations настроены

---

## ⚠️ Если что-то не работает

### Проблема: Сервер не запускается
**Решение:**
```bash
cd Server
pip install -r requirements.txt
python run_production.py
```

### Проблема: Эмуляторы не найдены
**Решение:** Проверить config.json:
```json
{
  "ldplayer_path": "C:\\LDPlayer\\LDPlayer9"
}
```

### Проблема: Timeout на эндпоинтах
**Решение:** Увеличить timeout в браузере или подождать 30 секунд

---

## 📚 Дополнительная информация

- 📖 Полная документация: [TEST_RESULTS.md](../TEST_RESULTS.md)
- 📊 Отчёт о прогрессе: [PROGRESS_REPORT.md](../PROGRESS_REPORT.md)
- 🎯 Production summary: [PRODUCTION_SUMMARY.md](../PRODUCTION_SUMMARY.md)

---

**Готово! Система работает! 🎉**
