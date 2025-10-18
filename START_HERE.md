# ⚡ БЫСТРЫЙ СТАРТ - DEV MODE

**Самый простой способ запустить систему для разработки UI!**

---

## 🎯 ОДИН КЛИК - АВТОЗАПУСК

```powershell
.\START.ps1
```

**Всё!** Система запустится сама:
- ✅ Backend на http://localhost:8000
- ✅ Frontend на http://localhost:3000  
- ✅ Браузер откроется автоматически

---

## 🔐 ВХОД

```
Логин:  admin
Пароль: admin123
```

---

## 📱 ЧТО УВИДИТЕ

- **Dashboard** - статистика системы (mock данные)
- **Emulators** - список из 6 тестовых эмуляторов
- **Кнопки** Start/Stop/Delete (имитация в DEV режиме)

---

## 🛠️ РУЧНОЙ ЗАПУСК

### Terminal 1 - Backend:
```powershell
cd Server
python run_dev_ui.py
```

### Terminal 2 - Frontend:
```powershell
cd frontend
npm run dev
```

---

## 💡 ПОЛЕЗНО

- **Swagger API:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **Остановить:** Закрыть окна терминалов

---

## 📚 ДОКУМЕНТАЦИЯ

**Quick Start (5 минут):**
- `SUMMARY.md` - краткая сводка проекта
- `START_HERE.md` - этот файл

**Week 1 (что сделано):**
- `WEEK1_COMPLETE.md` - отчет Week 1
- `WEEK1_100_COMPLETE.md` - финальный репорт
- `READY_TO_TEST.md` - полный гайд

**Week 2 (что делать дальше):**
- `WEEK2_PLAN.md` - детальный план (5 дней)
- `WEEK2_CHECKLIST.md` - чек-лист задач
- `CURRENT_STATE.md` - технический статус

**Architecture:**
- `ARCHITECTURE.md` - архитектура
- `IMPROVEMENT_ROADMAP.md` - roadmap (4 недели)

---

**🎉 Enjoy your system!**
