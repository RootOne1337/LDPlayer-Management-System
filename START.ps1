# 🚀 Автоматический запуск LDPlayer Management System
# Этот скрипт запускает оба сервера (backend + frontend) в отдельных окнах

Write-Host "`n" -NoNewline
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host "  🎮 LDPlayer Management System - AUTO START  " -ForegroundColor Yellow -BackgroundColor DarkBlue
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Пути
$ServerPath = "C:\Users\dimas\Documents\Remote\LDPlayerManagementSystem\Server"
$FrontendPath = "C:\Users\dimas\Documents\Remote\LDPlayerManagementSystem\frontend"

# Проверка путей
if (-not (Test-Path $ServerPath)) {
    Write-Host "❌ ERROR: Server directory not found!" -ForegroundColor Red
    Write-Host "   Path: $ServerPath" -ForegroundColor Yellow
    pause
    exit 1
}

if (-not (Test-Path $FrontendPath)) {
    Write-Host "❌ ERROR: Frontend directory not found!" -ForegroundColor Red
    Write-Host "   Path: $FrontendPath" -ForegroundColor Yellow
    pause
    exit 1
}

# Проверка Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python not found!" -ForegroundColor Red
    Write-Host "   Install Python 3.13+ from python.org" -ForegroundColor Yellow
    pause
    exit 1
}

# Проверка Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "   Install Node.js from nodejs.org" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "📦 Starting Backend Server..." -ForegroundColor Yellow
Write-Host "   Location: $ServerPath" -ForegroundColor DarkGray
Write-Host "   Command: python run_dev_ui.py" -ForegroundColor DarkGray

# Запуск backend в новом окне
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ServerPath'; `$host.UI.RawUI.WindowTitle = '🔧 Backend Server (Port 8000)'; Write-Host '🚀 Backend Server Starting...' -ForegroundColor Cyan; python run_dev_ui.py"
)

Write-Host "✅ Backend window opened" -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "   Location: $FrontendPath" -ForegroundColor DarkGray
Write-Host "   Command: npm run dev" -ForegroundColor DarkGray

# Запуск frontend в новом окне
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$FrontendPath'; `$host.UI.RawUI.WindowTitle = '🎨 Frontend Server (Port 3000)'; Write-Host '🚀 Frontend Server Starting...' -ForegroundColor Cyan; npm run dev"
)

Write-Host "✅ Frontend window opened" -ForegroundColor Green
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🌐 Opening Web Browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Открыть браузер
try {
    Start-Process "http://localhost:3000"
    Write-Host "✅ Browser opened" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not open browser automatically" -ForegroundColor Yellow
    Write-Host "   Please open manually: http://localhost:3000" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host "  ✅ SYSTEM STARTED SUCCESSFULLY!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor Yellow
Write-Host "   🎯 Web UI:      " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "   📡 Backend API: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "   📚 Swagger Docs:" -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Default Credentials:" -ForegroundColor Yellow
Write-Host "   Username: " -NoNewline -ForegroundColor White
Write-Host "admin" -ForegroundColor Green
Write-Host "   Password: " -NoNewline -ForegroundColor White
Write-Host "admin123" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Backend and Frontend are running in separate windows" -ForegroundColor Gray
Write-Host "   • Close those windows to stop the servers" -ForegroundColor Gray
Write-Host "   • Check backend window for server logs" -ForegroundColor Gray
Write-Host "   • Frontend has hot-reload enabled (auto-refresh on code changes)" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
