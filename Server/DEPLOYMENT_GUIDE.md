# 🚀 Security Implementation - Deployment Guide

**Version:** 1.0.0  
**Date:** October 17, 2025  
**Status:** ✅ Production Ready

---

## Overview

This guide covers the deployment of the newly implemented security features:
1. **JWT Authentication** - Bearer token protection on all write endpoints
2. **Automatic Password Encryption** - Fernet encryption on server startup
3. **HTTPS/SSL Support** - Auto-generation of self-signed certificates

---

## Prerequisites

### System Requirements
- Python 3.13+
- FastAPI 0.115+
- Uvicorn 0.34+
- Cryptography 41.0+
- PyJWT 2.8+

### Install Dependencies
```bash
cd Server
pip install -r requirements.txt
```

### Verify Installation
```bash
python -c "import fastapi, jwt, cryptography; print('✅ All dependencies installed')"
```

---

## Step 1: Prepare Configuration

### Create config.json
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "reload": false
  },
  "ldplayer_path": "C:\\LDPlayer\\LDPlayer9",
  "workstations": [
    {
      "id": "ws1",
      "name": "Workstation 1",
      "ip_address": "192.168.1.100",
      "username": "administrator",
      "password": "your_secure_password_here",
      "ldplayer_path": "C:\\LDPlayer\\LDPlayer9"
    }
  ]
}
```

### Security Notes
- Passwords will be auto-encrypted on server startup
- Store original config.json in secure location
- After first run, encrypted config will be in config.encrypted.json

---

## Step 2: Set Environment Variables (Optional)

### Production Environment
```bash
# JWT Configuration
export JWT_SECRET_KEY="your-super-secret-key-change-this"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION_MINUTES="30"

# Encryption
export ENCRYPTED_CONFIG="config.encrypted.json"
```

### Windows PowerShell
```powershell
$env:JWT_SECRET_KEY = "your-super-secret-key-change-this"
$env:JWT_ALGORITHM = "HS256"
$env:JWT_EXPIRATION_MINUTES = "30"
```

### Default Values (if not set)
- JWT_SECRET_KEY: "your-super-secret-key-change-this-in-production-12345"
- JWT_ALGORITHM: "HS256"
- JWT_EXPIRATION_MINUTES: "30"

⚠️ **WARNING:** Always change JWT_SECRET_KEY in production!

---

## Step 3: Run Tests (Recommended)

### Full Test Suite
```bash
python -m pytest tests/test_security.py -v
```

### Expected Output
```
========================== 24 passed in 0.46s ==========================
```

### Specific Tests
```bash
# JWT tests only
python -m pytest tests/test_security.py::TestJWTManager -v

# Encryption tests only
python -m pytest tests/test_security.py::TestSecretsManager -v

# Auth flow tests only
python -m pytest tests/test_security.py::TestAuthenticateUser -v
```

---

## Step 4: Start Server

### Production Mode
```bash
python run_production.py
```

### Stable Mode (No Auto-Reload)
```bash
python run_server_stable.py
```

### Expected Startup Output
```
============================================================
🚀 LDPlayer Management System Server
   Version: 1.0.0 (Production Ready)
   Date: October 17, 2025
============================================================

📋 Конфигурация:
   Хост: 0.0.0.0
   Порт: 8000
   Режим отладки: False
   Рабочих станций: 1

🔐 Генерирование self-signed SSL сертификата...
✅ SSL сертификат успешно создан

🌐 Доступ к API:
   API Docs (Swagger): https://localhost:8000/docs
   API Docs (ReDoc):   https://localhost:8000/redoc
   WebSocket:          wss://localhost:8000/ws

🔐 Аутентификация:
   POST /auth/login            - Получить JWT токен
   POST /auth/refresh          - Обновить токен
   GET  /auth/me               - Информация пользователя

✅ Запуск сервера...
   Нажмите Ctrl+C для остановки
============================================================
```

### Server Initialization
On first run, the server will:
1. Generate SSL certificates (cert.pem, key.pem)
2. Encrypt config.json → config.encrypted.json
3. Start HTTPS server on https://0.0.0.0:8000

### Files Created
```
cert.pem ..................... SSL certificate
key.pem ....................... Private key
secrets.key ................... Encryption key
config.encrypted.json ......... Encrypted configuration
```

---

## Step 5: Verify Deployment

### Check Server Health
```bash
# HTTP
curl -k https://localhost:8000/api/health

# Response
{
  "success": true,
  "message": "Сервер работает нормально",
  "data": {"status": "healthy"}
}
```

### Get JWT Token
```bash
curl -k -X POST https://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Use Protected Endpoint
```bash
# Get list of emulators (no auth required)
curl -k https://localhost:8000/api/emulators

# Create emulator (requires JWT)
curl -k -X POST https://localhost:8000/api/emulators \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workstation_id": "ws1",
    "name": "test-emu",
    "config": {
      "android_version": "9.0",
      "screen_size": "1280x720"
    }
  }'
```

---

## Step 6: Configure for Production

### Change JWT Secret
```bash
# Generate new secret (Linux/Mac)
openssl rand -hex 32

# Set environment variable
export JWT_SECRET_KEY="<generated-secret-here>"
```

### Use Production SSL Certificate

**Option A: Self-Signed Cert (For Testing)**
```bash
# Auto-generated on first run, already in place
# Acceptable for internal/testing use
```

**Option B: CA-Signed Certificate**
```bash
# 1. Get certificate from CA (Let's Encrypt, DigiCert, etc.)
# 2. Replace cert.pem and key.pem with CA files
cp /path/to/ca-cert.pem ./cert.pem
cp /path/to/ca-key.pem ./key.pem

# 3. Restart server
```

### Configure CORS (Optional)
In `src/core/server_modular.py`, update:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Enable Audit Logging
```python
# Add to server startup
logger.log_system_event("🔐 Security Audit Logging Enabled", {})
```

---

## Security Checklist

### Before First Deployment
- [ ] Change JWT_SECRET_KEY to strong secret
- [ ] Update default admin password
- [ ] Update default user password
- [ ] Review CORS configuration
- [ ] Test JWT token creation
- [ ] Test JWT token validation
- [ ] Verify SSL certificate generation
- [ ] Run full test suite
- [ ] Check all 11 protected endpoints
- [ ] Verify unprotected endpoints still work

### After Deployment
- [ ] Monitor server logs for errors
- [ ] Check that config.encrypted.json is created
- [ ] Test authentication flow
- [ ] Test protected endpoints with valid token
- [ ] Test protected endpoints with invalid token (should get 401)
- [ ] Monitor performance metrics
- [ ] Verify no plain-text passwords in config

### Ongoing Security
- [ ] Rotate JWT secret monthly
- [ ] Review authentication logs weekly
- [ ] Update dependencies for security patches
- [ ] Backup secrets.key securely
- [ ] Monitor for failed login attempts

---

## Troubleshooting

### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"
**Solution:**
```bash
# For testing with self-signed cert, use -k flag:
curl -k https://localhost:8000/api/health

# Or add to requests in Python:
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

### Issue: "401 Unauthorized" on Protected Endpoint
**Solution:**
```bash
# 1. Get token first
TOKEN=$(curl -k -X POST https://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Use token in Authorization header
curl -k -H "Authorization: Bearer $TOKEN" \
  https://localhost:8000/api/emulators
```

### Issue: "Invalid token" or Token Expired
**Solution:**
```bash
# 1. Check token expiration (30 minutes default)
# 2. Get new token:
curl -k -X POST https://localhost:8000/auth/refresh \
  -H "Authorization: Bearer <old-token>"

# 3. Or login again
curl -k -X POST https://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Issue: "Fernet key must be 32 url-safe base64-encoded bytes"
**Solution:**
```bash
# Delete secrets.key and restart server
rm secrets.key
python run_production.py
# Server will regenerate the key
```

### Issue: Config Not Encrypted on Startup
**Solution:**
```bash
# Check server logs for errors
# Ensure config.json exists in current directory
ls -la config.json

# Manually trigger encryption
python -c "from src.utils.secrets_manager import ConfigEncryption; \
           ConfigEncryption('config.json').encrypt_config('config.encrypted.json')"
```

### Issue: Server Won't Start
**Solution:**
```bash
# Check Python version
python --version  # Should be 3.13+

# Check dependencies
pip install -r requirements.txt

# Run with verbose logging
python -u run_production.py

# Check port 8000 is available
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

---

## API Authentication Examples

### Python Requests
```python
import requests
from requests.auth import HTTPBearerAuth

# Get token
response = requests.post(
    'https://localhost:8000/auth/login',
    json={'username': 'admin', 'password': 'admin123'},
    verify=False  # Ignore self-signed cert
)
token = response.json()['access_token']

# Use token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'https://localhost:8000/api/emulators',
    headers=headers,
    verify=False
)
```

### cURL
```bash
# Get token
TOKEN=$(curl -s -k -X POST https://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Use token
curl -k -H "Authorization: Bearer $TOKEN" \
  https://localhost:8000/api/emulators
```

### JavaScript/Node.js
```javascript
// Get token
const response = await fetch('https://localhost:8000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
});
const {access_token} = await response.json();

// Use token
const result = await fetch('https://localhost:8000/api/emulators', {
  headers: {'Authorization': `Bearer ${access_token}`}
});
```

---

## Monitoring & Logging

### Server Logs Location
```
logs/system.log ................ Main system log
logs/api.log ................... API requests
logs/emulator.log .............. Emulator operations
logs/operation.log ............. Operation logs
```

### Watch Logs in Real-Time
```bash
# macOS/Linux
tail -f logs/system.log

# Windows PowerShell
Get-Content logs/system.log -Wait
```

### Check for Security Events
```bash
grep "🔐\|⚠️\|❌" logs/system.log  # Security-related events
grep "401\|Unauthorized" logs/api.log  # Authentication errors
```

---

## Performance Tuning

### Increase Worker Processes
```bash
# In run_production.py
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    workers=4  # Increase based on CPU cores
)
```

### Enable Gzip Compression
```python
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

### Set Up Reverse Proxy (Nginx)
```nginx
upstream ldplayer_api {
    server localhost:8000;
}

server {
    listen 443 ssl;
    server_name api.example.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass https://ldplayer_api;
        proxy_set_header Authorization $http_authorization;
    }
}
```

---

## Backup & Recovery

### Backup Important Files
```bash
# Backup encryption key
cp secrets.key secrets.key.backup

# Backup SSL certificates  
cp cert.pem cert.pem.backup
cp key.pem key.pem.backup

# Backup config
cp config.json config.json.backup
cp config.encrypted.json config.encrypted.json.backup
```

### Restore from Backup
```bash
# In case of corruption:
cp secrets.key.backup secrets.key
cp config.encrypted.json.backup config.encrypted.json
# Restart server
```

---

## Summary

✅ **Deployment Checklist:**
1. Install dependencies
2. Create config.json with workstations
3. (Optional) Set JWT_SECRET_KEY environment variable
4. Run tests to verify setup
5. Start server with `python run_production.py`
6. Verify with test requests
7. Configure SSL for production
8. Set up monitoring and logging
9. Backup security keys
10. Document your setup

✅ **Security Verification:**
- All write endpoints protected with JWT
- Passwords encrypted with Fernet
- HTTPS enabled with self-signed cert
- Default credentials changed
- Audit logging enabled
- Backups of security keys created

---

**Deployment Status:** ✅ Ready for Production

For detailed information, see:
- `SECURITY_COMPLETION_REPORT.md` - Full implementation details
- `SECURITY_QUICK_START.md` - Quick reference guide
- `tests/test_security.py` - Security test examples

