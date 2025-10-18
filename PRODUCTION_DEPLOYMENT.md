# 🚀 PRODUCTION DEPLOYMENT GUIDE

**Версия**: 1.3.0  
**Дата**: 2025-10-17  
**Статус**: ✅ Production Ready 85%

---

## 📋 PREREQUISITES

### Системные требования

**Сервер (API Server)**:
- Windows Server 2019+ или Windows 10/11 Pro
- Python 3.10+
- 4GB RAM minimum, 8GB recommended
- 100GB+ свободного места на диске
- Сетевое подключение к рабочим станциям

**Рабочие станции (LDPlayer Hosts)**:
- Windows 10/11 Pro (Home не поддерживает WinRM)
- LDPlayer 9.0+ установлен
- PowerShell 5.1+
- 16GB+ RAM (зависит от количества эмуляторов)
- SSD для лучшей производительности

### Сетевые требования

**Порты**:
- `8001` - API Server (HTTP)
- `5985` - WinRM (HTTP)
- `5986` - WinRM (HTTPS, опционально)
- `445` - SMB (для доступа к файлам)

**Firewall Rules**:
```powershell
# На каждой рабочей станции:
New-NetFirewallRule -Name "WinRM-HTTP" -DisplayName "WinRM HTTP" -Protocol TCP -LocalPort 5985 -Action Allow
New-NetFirewallRule -Name "WinRM-HTTPS" -DisplayName "WinRM HTTPS" -Protocol TCP -LocalPort 5986 -Action Allow

# На сервере:
New-NetFirewallRule -Name "API-Server" -DisplayName "LDPlayer API" -Protocol TCP -LocalPort 8001 -Action Allow
```

---

## ⚙️ WINRM SETUP (КРИТИЧНО!)

### На каждой рабочей станции

**Шаг 1: Включить WinRM**
```powershell
# Запустить PowerShell от имени Administrator
winrm quickconfig -force
```

**Шаг 2: Включить PowerShell Remoting**
```powershell
Enable-PSRemoting -Force
```

**Шаг 3: Настроить TrustedHosts**
```powershell
# Вариант 1: Разрешить все хосты (для тестирования)
Set-Item WSMan:\localhost\Client\TrustedHosts * -Force

# Вариант 2: Разрешить только IP сервера (рекомендуется для production)
Set-Item WSMan:\localhost\Client\TrustedHosts "192.168.1.100" -Force

# Проверить
Get-Item WSMan:\localhost\Client\TrustedHosts
```

**Шаг 4: Настроить аутентификацию**
```powershell
# Включить Basic Auth (требуется для pywinrm)
Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true

# Включить Unencrypted (только для HTTP, не для production!)
Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true
```

**⚠️ ВАЖНО**: Для production используйте HTTPS (порт 5986) и сертификаты!

**Шаг 5: Перезапустить WinRM**
```powershell
Restart-Service WinRM
```

**Шаг 6: Проверить**
```powershell
# Локально
Test-WSMan

# С другого компьютера
Test-WSMan -ComputerName "192.168.1.101" -Authentication Basic -Credential (Get-Credential)
```

### На сервере (API Server)

**Шаг 1: Настроить WinRM Client**
```powershell
Set-Item WSMan:\localhost\Client\TrustedHosts "192.168.1.101,192.168.1.102,192.168.1.103" -Force
```

**Шаг 2: Протестировать подключение**
```powershell
$session = New-PSSession -ComputerName "192.168.1.101" -Credential (Get-Credential)
Invoke-Command -Session $session -ScriptBlock { Get-Process }
Remove-PSSession $session
```

---

## 🔐 HTTPS / SSL SETUP (PRODUCTION)

### Создание Self-Signed Certificate

```powershell
# На рабочей станции
$cert = New-SelfSignedCertificate -DnsName "workstation01.local" -CertStoreLocation Cert:\LocalMachine\My

# Экспортировать thumbprint
$cert.Thumbprint

# Настроить HTTPS Listener
winrm create winrm/config/Listener?Address=*+Transport=HTTPS "@{Hostname=`"workstation01.local`";CertificateThumbprint=`"$($cert.Thumbprint)`"}"

# Проверить
winrm enumerate winrm/config/Listener
```

### Настройка в коде

```python
# В config.json
{
  "workstations": [
    {
      "id": "ws_001",
      "name": "Workstation 01",
      "ip_address": "192.168.1.101",
      "username": "administrator",
      "password": "YourSecurePassword",
      "use_https": true,  # Использовать HTTPS
      "port": 5986        # HTTPS порт
    }
  ]
}
```

---

## 📦 INSTALLATION

### Шаг 1: Clone Repository

```powershell
cd C:\
git clone https://github.com/yourusername/LDPlayerManagementSystem.git
cd LDPlayerManagementSystem\Server
```

### Шаг 2: Установить Python Dependencies

```powershell
# Создать virtual environment (рекомендуется)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt
```

### Шаг 3: Создать .env файл

```ini
# Server/.env
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
LOG_LEVEL=INFO

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# Paths
LDPLAYER_PATH=C:\LDPlayer\LDPlayer9
CONFIG_FILE=configs/config.json
LOG_DIR=logs
```

**⚠️ ВАЖНО**: Измените `JWT_SECRET_KEY` и `ENCRYPTION_KEY`!

```powershell
# Генерация безопасных ключей:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Шаг 4: Создать config.json

```json
{
  "workstations": [
    {
      "id": "ws_001",
      "name": "Main Workstation",
      "ip_address": "192.168.1.101",
      "username": "administrator",
      "password": "YourPassword",
      "ldplayer_path": "C:\\LDPlayer\\LDPlayer9"
    }
  ],
  "backup": {
    "enabled": true,
    "interval_hours": 24,
    "retention_days": 7,
    "backup_path": "backups"
  }
}
```

### Шаг 5: Запустить тесты

```powershell
# Убедиться, что все работает
pytest tests/ -v

# Ожидаемый результат:
# ============================= 68 passed in 28.74s =============================
```

### Шаг 6: Запустить сервер

```powershell
# Development
python -m uvicorn src.core.server:app --host 127.0.0.1 --port 8001 --reload

# Production
python -m uvicorn src.core.server:app --host 0.0.0.0 --port 8001 --workers 4
```

### Шаг 7: Проверить работу

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8001/health"

# API docs
Start-Process "http://localhost:8001/docs"

# Login
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login" -Method Post -Body $body -ContentType "application/json"
$token = $response.access_token
```

---

## 🔄 SYSTEMD SERVICE (Linux) / WINDOWS SERVICE

### Windows Service (NSSM)

**Шаг 1: Установить NSSM**
```powershell
# Скачать с https://nssm.cc/download
# Или через Chocolatey:
choco install nssm
```

**Шаг 2: Создать service**
```powershell
nssm install LDPlayerAPI "C:\LDPlayerManagementSystem\Server\venv\Scripts\python.exe" "-m uvicorn src.core.server:app --host 0.0.0.0 --port 8001"
nssm set LDPlayerAPI AppDirectory "C:\LDPlayerManagementSystem\Server"
nssm set LDPlayerAPI DisplayName "LDPlayer Management API"
nssm set LDPlayerAPI Description "API Server for LDPlayer Management System"
nssm set LDPlayerAPI Start SERVICE_AUTO_START

# Запустить
nssm start LDPlayerAPI

# Проверить статус
nssm status LDPlayerAPI
```

### Task Scheduler (альтернатива)

```powershell
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "-m uvicorn src.core.server:app --host 0.0.0.0 --port 8001" -WorkingDirectory "C:\LDPlayerManagementSystem\Server"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "LDPlayerAPI" -Action $action -Trigger $trigger -Principal $principal
```

---

## 🌐 REVERSE PROXY (NGINX / CADDY)

### Nginx

```nginx
# C:\nginx\conf\nginx.conf
server {
    listen 80;
    server_name api.ldplayer.local;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Caddy (рекомендуется)

```caddyfile
# Caddyfile
api.ldplayer.local {
    reverse_proxy localhost:8001
}
```

---

## 💾 BACKUP STRATEGY

### Автоматический backup

Уже реализован в `backup_manager.py`:

```python
# В config.json
{
  "backup": {
    "enabled": true,
    "interval_hours": 24,
    "retention_days": 7,
    "backup_path": "backups"
  }
}
```

### Ручной backup

```powershell
# Backup конфигурации
Copy-Item "C:\LDPlayerManagementSystem\Server\configs\config.json" "C:\Backups\config_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# Backup базы пользователей (если используется файловая DB)
Copy-Item "C:\LDPlayerManagementSystem\Server\data\users.db" "C:\Backups\users_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"

# Backup логов
Compress-Archive -Path "C:\LDPlayerManagementSystem\Server\logs\*" -DestinationPath "C:\Backups\logs_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
```

---

## 📊 MONITORING

### Логи

```powershell
# Просмотр логов в реальном времени
Get-Content "C:\LDPlayerManagementSystem\Server\logs\server.log" -Wait -Tail 50

# Поиск ошибок
Get-Content "C:\LDPlayerManagementSystem\Server\logs\server.log" | Select-String "ERROR"

# Экспорт для анализа
Get-Content "C:\LDPlayerManagementSystem\Server\logs\server.log" | Select-Object -Last 1000 | Out-File "diagnostic.txt"
```

### Health Check Script

```powershell
# health_check.ps1
$response = Invoke-RestMethod -Uri "http://localhost:8001/health" -ErrorAction SilentlyContinue
if ($response.status -eq "healthy") {
    Write-Host "✅ Server is healthy"
    exit 0
} else {
    Write-Host "❌ Server is unhealthy"
    exit 1
}
```

### Task Scheduler для мониторинга

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\LDPlayerManagementSystem\Server\health_check.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "LDPlayerHealthCheck" -Action $action -Trigger $trigger
```

---

## 🔒 SECURITY BEST PRACTICES

### 1. Изменить default пароли

```python
# После первого запуска:
# 1. Зайти как admin (admin / admin123)
# 2. Изменить пароль через API:
POST /api/auth/users/{user_id}
{
  "password": "NewSecurePassword123!"
}
```

### 2. Ограничить доступ по IP

```python
# В server.py добавить middleware:
@app.middleware("http")
async def ip_whitelist(request: Request, call_next):
    allowed_ips = ["192.168.1.100", "192.168.1.101"]
    client_ip = request.client.host
    
    if client_ip not in allowed_ips:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await call_next(request)
```

### 3. Использовать HTTPS

```powershell
# Генерация сертификата
$cert = New-SelfSignedCertificate -DnsName "api.ldplayer.local" -CertStoreLocation Cert:\LocalMachine\My
```

### 4. Rate Limiting

```python
# Установить slowapi
pip install slowapi

# В server.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # 5 попыток в минуту
async def login():
    pass
```

---

## 🐛 TROUBLESHOOTING

### Проблема: "Access Denied" при WinRM подключении

**Решение**:
```powershell
# На рабочей станции:
Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true
Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true
Restart-Service WinRM

# Проверить TrustedHosts
Get-Item WSMan:\localhost\Client\TrustedHosts
```

### Проблема: "Connection timeout"

**Решение**:
```powershell
# Проверить firewall
Test-NetConnection -ComputerName "192.168.1.101" -Port 5985

# Добавить правило
New-NetFirewallRule -Name "WinRM-HTTP" -Protocol TCP -LocalPort 5985 -Action Allow
```

### Проблема: "Cannot import module"

**Решение**:
```powershell
# Убедиться, что venv активирован
.\venv\Scripts\Activate.ps1

# Переустановить зависимости
pip install -r requirements.txt --force-reinstall
```

### Проблема: "JWT token invalid"

**Решение**:
```python
# Проверить, что JWT_SECRET_KEY одинаковый в .env и коде
# Проверить время на сервере (токены имеют expiry)
```

---

## 📚 ПОЛЕЗНЫЕ ССЫЛКИ

- **WinRM Setup**: https://docs.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **PyWinRM**: https://github.com/diyan/pywinrm
- **NSSM**: https://nssm.cc/usage
- **Caddy**: https://caddyserver.com/docs/

---

## ✅ CHECKLIST

**Перед развертыванием**:
- [ ] Python 3.10+ установлен
- [ ] LDPlayer установлен на рабочих станциях
- [ ] WinRM настроен на всех рабочих станциях
- [ ] Firewall rules настроены
- [ ] .env файл создан с безопасными ключами
- [ ] config.json настроен
- [ ] Тесты проходят (68/68)
- [ ] Health check работает

**После развертывания**:
- [ ] Изменены default пароли
- [ ] Настроен reverse proxy (опционально)
- [ ] Настроен автозапуск (NSSM / Task Scheduler)
- [ ] Настроен мониторинг
- [ ] Настроен backup
- [ ] Документация обновлена

---

**Подготовлено**: GitHub Copilot  
**Дата**: 2025-10-17  
**Версия**: 1.0
