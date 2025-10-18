# 🎮 LDPlayer Management System - Desktop App

## Quick Start

### Windows (Easiest)
```bash
# Just double-click this file:
RUN_APP.bat
```

### Manual
```bash
# 1. Activate venv
cd LDPlayerManagementSystem
venv\Scripts\activate.bat

# 2. Run app
python app_desktop.py
```

### macOS/Linux
```bash
source venv/bin/activate
python app_desktop.py
```

## Features

✅ **Modern PyQt6 Interface**
- Dark theme with cyan accents (2025 style)
- Professional color-coded tables
- Real-time updates
- Responsive design

✅ **4 Main Tabs**
1. **📊 Dashboard** - System overview and statistics
2. **🖥️ Workstations** - Add/Delete/Monitor machines
3. **🕹️ Emulators** - Start/Stop LDPlayer instances
4. **📝 Logs** - Real-time logging with export/clear

✅ **Local Operation**
- No browser needed
- All data from config.json
- UTF-8 logging with emoji
- Fully self-contained

## Architecture

```
LDPlayerManagementSystem/
├── app_desktop.py          ← Main PyQt6 application
├── Server/
│   ├── config.json         ← Workstation config
│   ├── run_server_stable.py ← Backend API (optional)
│   └── logs/
│       └── app.log         ← Application logs
└── venv/                   ← Virtual environment
```

## Commands in App

### Dashboard
- View total workstations
- View total emulators
- Check online status

### Workstations
- ➕ **Add Workstation** - Create new connection
- 🔄 **Refresh** - Update list
- ❌ **Delete** - Remove workstation

### Emulators
- ▶️ **Start** - Launch emulator
- ⏹️ **Stop** - Terminate emulator
- 🔄 **Refresh** - Update status

### Logs
- 🗑️ **Clear** - Clear all logs
- 💾 **Export** - Save logs to file

## Logs Location

`Server/logs/app.log` - All application events with timestamps

## Troubleshooting

### App doesn't start
```bash
# Make sure dependencies are installed
pip install PyQt6
```

### Config not loading
```bash
# Check if config.json exists in Server/ folder
python -c "import json; print(json.load(open('Server/config.json')))"
```

### Logs not showing
```bash
# Check log file exists
cat Server/logs/app.log
```

## Version
**1.0.0** - Desktop Edition (Week 2)

---
**Created:** October 17, 2025  
**Author:** Copilot  
**Project:** LDPlayer Management System
