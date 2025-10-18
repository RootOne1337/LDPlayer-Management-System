# 📅 WEEK 2 - ДЕТАЛЬНЫЙ ПЛАН РАБОТ

**Период:** 18-22 октября 2025  
**Цель:** Подключить реальные данные + Тесты + Мониторинг  
**Target Progress:** 50% → 75%

---

## 🎯 ГЛАВНЫЕ ЦЕЛИ НЕДЕЛИ

1. **Подключить хотя бы 1 real workstation** - выйти из DEV режима
2. **Написать 20+ automated tests** - обеспечить качество
3. **Добавить базовый monitoring** - видеть состояние системы
4. **Достичь 75% system readiness** - готовность к pre-production

---

## 📆 DAY-BY-DAY BREAKDOWN

### 🔴 DAY 1: WinRM Setup (18 октября) - P0 CRITICAL

**Время:** 4-6 часов  
**Цель:** Настроить WinRM на 1 тестовой машине

#### Задачи:

**1.1 Выбрать тестовую машину** (30 мин)
- [ ] Определить IP address (например: 192.168.1.101)
- [ ] Проверить, что LDPlayer установлен
- [ ] Убедиться в сетевой доступности
- [ ] Запомнить credentials (admin/password)

**1.2 Настроить WinRM на workstation** (1 час)
```powershell
# На удаленной машине (192.168.1.101):

# 1. Enable WinRM
winrm quickconfig
# Ответить "Y" на все вопросы

# 2. Enable PowerShell Remoting
Enable-PSRemoting -Force

# 3. Добавить trusted hosts (на сервере)
Set-Item WSMan:\localhost\Client\TrustedHosts "192.168.1.101" -Force

# 4. Включить Basic auth (для PyWinRM)
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'

# 5. Проверить статус
winrm get winrm/config

# 6. Открыть firewall (если нужно)
netsh advfirewall firewall add rule name="WinRM-HTTP" dir=in action=allow protocol=TCP localport=5985
```

**Verification:**
```powershell
# С локальной машины:
Test-WSMan -ComputerName 192.168.1.101
```

**1.3 Создать тестовый скрипт подключения** (1 час)
```python
# Server/test_winrm_connection.py

from pywinrm.protocol import Protocol
import sys
import json

def test_winrm_connection(host, username, password):
    """Test WinRM connection to remote workstation"""
    print(f"\n🔍 Testing connection to {host}...")
    
    try:
        # Create WinRM protocol
        endpoint = f'http://{host}:5985/wsman'
        p = Protocol(
            endpoint=endpoint,
            transport='plaintext',
            username=username,
            password=password,
            server_cert_validation='ignore'
        )
        
        # Test 1: Run simple command
        print("Test 1: Running 'ipconfig'...")
        result = p.run_cmd('ipconfig')
        if result.status_code == 0:
            print("✅ Command executed successfully")
            print(result.std_out.decode('utf-8')[:200])
        else:
            print(f"❌ Command failed: {result.std_err}")
            return False
        
        # Test 2: Check LDPlayer installation
        print("\nTest 2: Checking LDPlayer installation...")
        ldplayer_check = '''
        $ldpath = "C:\\Program Files\\LDPlayer\\LDPlayer4.0"
        if (Test-Path $ldpath) {
            Write-Output "LDPlayer found at: $ldpath"
            Get-ChildItem $ldpath -Filter "dnconsole.exe" | Select-Object FullName
        } else {
            Write-Output "LDPlayer not found"
        }
        '''
        result = p.run_ps(ldplayer_check)
        if result.status_code == 0:
            output = result.std_out.decode('utf-8')
            print(output)
            if "LDPlayer found" in output:
                print("✅ LDPlayer installation detected")
            else:
                print("⚠️ LDPlayer not found - check installation path")
        
        # Test 3: List emulators
        print("\nTest 3: Listing emulators...")
        list_cmd = '''
        $ldconsole = "C:\\Program Files\\LDPlayer\\LDPlayer4.0\\dnconsole.exe"
        if (Test-Path $ldconsole) {
            & $ldconsole list
        } else {
            Write-Output "dnconsole.exe not found"
        }
        '''
        result = p.run_ps(list_cmd)
        if result.status_code == 0:
            output = result.std_out.decode('utf-8')
            print(output)
            print("✅ Emulator list retrieved")
        
        print(f"\n🎉 All tests passed! WinRM connection to {host} is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    # Configuration
    HOST = "192.168.1.101"
    USERNAME = "admin"
    PASSWORD = "your_password"
    
    # Test connection
    success = test_winrm_connection(HOST, USERNAME, PASSWORD)
    sys.exit(0 if success else 1)
```

**Run test:**
```powershell
cd Server
python test_winrm_connection.py
```

**Expected Output:**
```
🔍 Testing connection to 192.168.1.101...
Test 1: Running 'ipconfig'...
✅ Command executed successfully
Windows IP Configuration...

Test 2: Checking LDPlayer installation...
LDPlayer found at: C:\Program Files\LDPlayer\LDPlayer4.0
✅ LDPlayer installation detected

Test 3: Listing emulators...
0,Android-Game-1,running,0,0
1,Android-Game-2,stopped,0,0
✅ Emulator list retrieved

🎉 All tests passed! WinRM connection to 192.168.1.101 is working!
```

**1.4 Обновить config.json с real workstation** (30 мин)
```json
{
  "workstations": [
    {
      "id": "ws-production-1",
      "name": "Production Workstation 1",
      "host": "192.168.1.101",
      "protocol": "winrm",
      "ldplayer_path": "C:\\Program Files\\LDPlayer\\LDPlayer4.0",
      "auth": {
        "username": "admin",
        "password": "ENCRYPTED_BY_FERNET"
      },
      "enabled": true
    }
  ]
}
```

**Encrypt password:**
```python
from src.core.security import SecurityManager
security = SecurityManager()
encrypted = security.encrypt_password("your_password")
print(encrypted)  # Добавить в config.json
```

**1.5 Запустить server БЕЗ DEV_MODE** (30 мин)
```powershell
cd Server
# БЕЗ DEV_MODE - использует реальные подключения
python run_server_stable.py
```

**Check logs:**
```
[INFO] 🚀 Starting LDPlayer Management Server...
[INFO] 🔗 Connecting to workstation: Production Workstation 1 (192.168.1.101)...
[INFO] ✅ Connected via WinRM
[INFO] 🎮 Detecting emulators...
[INFO] ✅ Found 2 emulators: [Android-Game-1, Android-Game-2]
[INFO] 🌐 Server started on https://localhost:8000
```

**1.6 Проверить UI** (30 мин)
```
1. Открыть http://localhost:3000
2. Login: admin / admin123
3. Dashboard должен показать:
   ✅ 1 online workstation (вместо mock 4)
   ✅ Реальное количество эмуляторов
4. Перейти в Emulators
   ✅ Видеть реальные эмуляторы с workstation
5. Попробовать Start/Stop на реальном эмуляторе
   ✅ Эмулятор должен запуститься/остановиться
```

**Success Criteria Day 1:**
- ✅ WinRM настроен и работает
- ✅ Server подключается к workstation
- ✅ Обнаруживает LDPlayer и эмуляторы
- ✅ UI показывает реальные данные
- ✅ Start/Stop работает на реальном железе

---

### 🔴 DAY 2: Production Mode Refinement (19 октября) - P0

**Время:** 4 часа  
**Цель:** Стабилизировать работу с real workstation

#### Задачи:

**2.1 Добавить error handling для WinRM** (1.5 часа)
```python
# src/remote/workstation.py

from tenacity import retry, stop_after_attempt, wait_exponential
import logging

class Workstation:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def connect(self):
        """Connect to workstation with retry logic"""
        try:
            self.logger.info(f"🔗 Connecting to {self.name} ({self.host})...")
            self.protocol = Protocol(
                endpoint=f'http://{self.host}:5985/wsman',
                transport='plaintext',
                username=self.auth['username'],
                password=self.auth['password']
            )
            # Test connection
            result = self.protocol.run_cmd('echo test')
            if result.status_code != 0:
                raise ConnectionError(f"Failed to connect: {result.std_err}")
            
            self.logger.info(f"✅ Connected to {self.name}")
            self.connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Connection failed: {e}")
            self.connected = False
            raise

    def disconnect(self):
        """Gracefully disconnect"""
        if self.connected:
            self.logger.info(f"👋 Disconnecting from {self.name}...")
            self.protocol = None
            self.connected = False
```

**2.2 Добавить timeout management** (1 час)
```python
# src/api/emulators.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

@router.post("/{emulator_id}/start")
async def start_emulator(emulator_id: str, token: str = Depends(verify_token)):
    """Start emulator with timeout"""
    try:
        # Run blocking operation in thread pool with timeout
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                executor,
                lambda: server.start_emulator(emulator_id)
            ),
            timeout=30.0  # 30 second timeout
        )
        return {"status": "started", "emulator_id": emulator_id}
    
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Operation timed out after 30 seconds"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**2.3 Улучшить логирование** (1 час)
```python
# Добавить structured logging для operations

logger.info("🎮 Starting emulator", extra={
    "emulator_id": emulator_id,
    "workstation": workstation.name,
    "operation": "start",
    "timestamp": datetime.utcnow().isoformat()
})

# Log operation duration
start_time = time.time()
try:
    result = start_emulator(emulator_id)
    duration = time.time() - start_time
    logger.info(f"✅ Emulator started in {duration:.2f}s", extra={
        "emulator_id": emulator_id,
        "duration_seconds": duration,
        "status": "success"
    })
except Exception as e:
    duration = time.time() - start_time
    logger.error(f"❌ Failed to start emulator after {duration:.2f}s", extra={
        "emulator_id": emulator_id,
        "duration_seconds": duration,
        "error": str(e),
        "status": "failed"
    })
    raise
```

**2.4 Тестировать стабильность** (30 мин)
```python
# Server/test_stress.py
# Тест стабильности: 10 операций подряд

import requests
import time

BASE_URL = "http://localhost:8000"
token = None

def login():
    global token
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["access_token"]
    print("✅ Logged in")

def test_operations():
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get emulators
    response = requests.get(f"{BASE_URL}/api/emulators", headers=headers)
    emulators = response.json()
    print(f"✅ Found {len(emulators)} emulators")
    
    if not emulators:
        print("⚠️ No emulators found")
        return
    
    emulator_id = emulators[0]["id"]
    
    # Stress test: Start/Stop 10 times
    for i in range(10):
        print(f"\n--- Iteration {i+1}/10 ---")
        
        # Start
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/emulators/{emulator_id}/start",
            headers=headers
        )
        print(f"Start: {response.status_code} ({time.time()-start:.2f}s)")
        
        time.sleep(5)  # Wait for startup
        
        # Stop
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/emulators/{emulator_id}/stop",
            headers=headers
        )
        print(f"Stop: {response.status_code} ({time.time()-start:.2f}s)")
        
        time.sleep(2)

if __name__ == "__main__":
    login()
    test_operations()
    print("\n🎉 Stress test completed!")
```

**Run:**
```powershell
python test_stress.py
```

**Success Criteria Day 2:**
- ✅ Error handling работает (retry on failure)
- ✅ Timeouts предотвращают зависание
- ✅ Логи содержат полезную информацию
- ✅ System стабильна под нагрузкой (10 операций)

---

### 🟡 DAY 3: Automated Tests - Part 1 (20 октября) - P1

**Время:** 4-5 часов  
**Цель:** Написать первые 10 тестов

#### Задачи:

**3.1 Setup pytest инфраструктура** (1 час)
```python
# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from src.core.server_modular import app
import os

@pytest.fixture(scope="session")
def test_client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture(scope="session")
def auth_token(test_client):
    """Get JWT token for authenticated requests"""
    response = test_client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture(scope="session", autouse=True)
def setup_dev_mode():
    """Force DEV_MODE for tests"""
    os.environ["DEV_MODE"] = "true"
    yield
    os.environ.pop("DEV_MODE", None)
```

**3.2 Test Mock Data** (1 час)
```python
# tests/test_mock_data.py

from src.utils.mock_data import (
    get_mock_emulators,
    get_mock_workstations,
    get_mock_system_status
)

def test_mock_emulators_structure():
    """Test mock emulators have correct structure"""
    emulators = get_mock_emulators()
    
    assert isinstance(emulators, list)
    assert len(emulators) == 6
    
    for emu in emulators:
        assert "id" in emu
        assert "name" in emu
        assert "status" in emu
        assert "workstation_id" in emu
        assert "config" in emu
        assert emu["status"] in ["running", "stopped"]

def test_mock_workstations_structure():
    """Test mock workstations have correct structure"""
    workstations = get_mock_workstations()
    
    assert isinstance(workstations, list)
    assert len(workstations) == 4
    
    for ws in workstations:
        assert "id" in ws
        assert "name" in ws
        assert "host" in ws
        assert "status" in ws
        assert ws["status"] in ["online", "offline"]

def test_mock_system_status():
    """Test mock system status"""
    status = get_mock_system_status()
    
    assert status["online_workstations"] == 3
    assert status["total_emulators"] == 6
    assert status["active_operations"] == 1
```

**3.3 Test Health Endpoints** (1 час)
```python
# tests/test_api_health.py

def test_health_endpoint(test_client):
    """Test /api/health endpoint"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_server_status(test_client, auth_headers):
    """Test /api/status endpoint"""
    response = test_client.get("/api/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "connected_workstations" in data

def test_version_endpoint(test_client):
    """Test /api/version endpoint"""
    response = test_client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
```

**3.4 Test Authentication** (1.5 часа)
```python
# tests/test_api_auth.py

def test_login_success(test_client):
    """Test successful login"""
    response = test_client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(test_client):
    """Test login with wrong password"""
    response = test_client.post("/auth/login", json={
        "username": "admin",
        "password": "wrong_password"
    })
    assert response.status_code == 401

def test_protected_endpoint_without_token(test_client):
    """Test accessing protected endpoint without token"""
    response = test_client.get("/api/emulators")
    assert response.status_code == 401

def test_protected_endpoint_with_invalid_token(test_client):
    """Test with invalid JWT token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.get("/api/emulators", headers=headers)
    assert response.status_code == 401
```

**3.5 Run tests** (30 мин)
```bash
# Install pytest if needed
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Open coverage report
start htmlcov/index.html
```

**Success Criteria Day 3:**
- ✅ 10+ tests written and passing
- ✅ Mock data validated
- ✅ Health endpoints tested
- ✅ Authentication flow tested
- ✅ Coverage report generated

---

### 🟡 DAY 4: Automated Tests - Part 2 (21 октября) - P1

**Время:** 4-5 часов  
**Цель:** Довести до 20+ тестов, 75% coverage

#### Задачи:

**4.1 Test Emulator API** (2 часа)
```python
# tests/test_api_emulators.py

def test_get_all_emulators(test_client, auth_headers):
    """Test GET /api/emulators"""
    response = test_client.get("/api/emulators", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 0

def test_get_emulator_by_id(test_client, auth_headers):
    """Test GET /api/emulators/{id}"""
    # Get first emulator
    response = test_client.get("/api/emulators", headers=auth_headers)
    emulators = response.json()
    
    if emulators:
        emu_id = emulators[0]["id"]
        response = test_client.get(f"/api/emulators/{emu_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == emu_id

def test_start_emulator(test_client, auth_headers):
    """Test POST /api/emulators/{id}/start"""
    # In DEV_MODE, this should succeed with mock
    emulators = test_client.get("/api/emulators", headers=auth_headers).json()
    
    if emulators:
        emu_id = emulators[0]["id"]
        response = test_client.post(
            f"/api/emulators/{emu_id}/start",
            headers=auth_headers
        )
        # Should return 200 or appropriate status
        assert response.status_code in [200, 202, 400]

def test_stop_emulator(test_client, auth_headers):
    """Test POST /api/emulators/{id}/stop"""
    emulators = test_client.get("/api/emulators", headers=auth_headers).json()
    
    if emulators:
        emu_id = emulators[0]["id"]
        response = test_client.post(
            f"/api/emulators/{emu_id}/stop",
            headers=auth_headers
        )
        assert response.status_code in [200, 202, 400]
```

**4.2 Test Workstation API** (1.5 часа)
```python
# tests/test_api_workstations.py

def test_get_workstations(test_client, auth_headers):
    """Test GET /api/workstations"""
    response = test_client.get("/api/workstations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_workstation_emulators(test_client, auth_headers):
    """Test GET /api/workstations/{id}/emulators"""
    workstations = test_client.get("/api/workstations", headers=auth_headers).json()
    
    if workstations:
        ws_id = workstations[0]["id"]
        response = test_client.get(
            f"/api/workstations/{ws_id}/emulators",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

def test_workstation_status(test_client, auth_headers):
    """Test workstation status tracking"""
    workstations = test_client.get("/api/workstations", headers=auth_headers).json()
    
    for ws in workstations:
        assert "status" in ws
        assert ws["status"] in ["online", "offline"]
```

**4.3 Integration Tests** (1 час)
```python
# tests/test_integration.py

def test_full_login_to_emulator_flow(test_client):
    """Test complete flow: login → get emulators → get details"""
    # Step 1: Login
    response = test_client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get emulators
    response = test_client.get("/api/emulators", headers=headers)
    assert response.status_code == 200
    emulators = response.json()
    
    # Step 3: Get first emulator details
    if emulators:
        emu_id = emulators[0]["id"]
        response = test_client.get(f"/api/emulators/{emu_id}", headers=headers)
        assert response.status_code == 200

def test_error_handling_invalid_emulator_id(test_client, auth_headers):
    """Test error handling for invalid ID"""
    response = test_client.get(
        "/api/emulators/invalid-id-9999",
        headers=auth_headers
    )
    # Should return 404 or appropriate error
    assert response.status_code in [404, 400]
```

**4.4 Review Coverage** (30 мин)
```bash
# Generate coverage report
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Analyze results
# Target: 75%+ overall
# Focus on:
#   - src/api/*.py (should be 80%+)
#   - src/core/security.py (should be 90%+)
#   - src/utils/mock_data.py (should be 100%)
```

**Success Criteria Day 4:**
- ✅ 20+ total tests
- ✅ All emulator endpoints tested
- ✅ All workstation endpoints tested
- ✅ Integration flows tested
- ✅ 75%+ code coverage achieved

---

### 🟡 DAY 5: Monitoring (22 октября) - P1

**Время:** 4 часа  
**Цель:** Добавить базовый monitoring

#### Задачи:

**5.1 Install dependencies** (15 мин)
```bash
pip install psutil prometheus-client
```

**5.2 Create monitoring module** (2 часа)
```python
# src/utils/monitoring.py

import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from collections import deque

@dataclass
class MetricSnapshot:
    """Single point-in-time metric snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int

class SystemMonitor:
    """Monitor system resources and health"""
    
    def __init__(self, history_size: int = 60):
        self.start_time = datetime.utcnow()
        self.history_size = history_size
        self.metric_history = deque(maxlen=history_size)
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        snapshot = MetricSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv
        )
        
        self.metric_history.append(snapshot)
        
        return {
            "current": asdict(snapshot),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
                "per_cpu": psutil.cpu_percent(interval=1, percpu=True)
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_gb": disk.used / (1024**3),
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get metric history"""
        return [asdict(snapshot) for snapshot in self.metric_history]
```

**5.3 Create monitoring API** (1 час)
```python
# src/api/monitoring.py

from fastapi import APIRouter, Depends
from src.core.security import verify_token
from src.utils.monitoring import SystemMonitor

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])
monitor = SystemMonitor(history_size=60)  # Keep 60 samples

@router.get("/metrics")
async def get_metrics(token: str = Depends(verify_token)):
    """Get current system metrics"""
    return monitor.get_current_metrics()

@router.get("/history")
async def get_history(token: str = Depends(verify_token)):
    """Get metric history (last 60 samples)"""
    return monitor.get_history()

@router.get("/health")
async def get_health_status(token: str = Depends(verify_token)):
    """Get health status based on metrics"""
    metrics = monitor.get_current_metrics()
    
    # Define health thresholds
    cpu_warn = 80
    memory_warn = 85
    disk_warn = 90
    
    warnings = []
    if metrics["cpu"]["percent"] > cpu_warn:
        warnings.append(f"High CPU usage: {metrics['cpu']['percent']:.1f}%")
    if metrics["memory"]["percent"] > memory_warn:
        warnings.append(f"High memory usage: {metrics['memory']['percent']:.1f}%")
    if metrics["disk"]["percent"] > disk_warn:
        warnings.append(f"High disk usage: {metrics['disk']['percent']:.1f}%")
    
    status = "healthy" if not warnings else "warning"
    
    return {
        "status": status,
        "warnings": warnings,
        "metrics": metrics["current"]
    }
```

**5.4 Add monitoring to server** (30 мин)
```python
# src/core/server_modular.py

from src.api import health, auth, emulators, workstations, monitoring

# Add monitoring router
app.include_router(monitoring.router)
```

**5.5 Test monitoring** (30 мин)
```python
# Server/test_monitoring.py

import requests
import time

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get current metrics
response = requests.get(f"{BASE_URL}/api/monitoring/metrics", headers=headers)
print("📊 Current Metrics:")
print(response.json())

# Get health status
response = requests.get(f"{BASE_URL}/api/monitoring/health", headers=headers)
print("\n💚 Health Status:")
print(response.json())

# Get history (after collecting some samples)
time.sleep(10)
response = requests.get(f"{BASE_URL}/api/monitoring/history", headers=headers)
print(f"\n📈 History: {len(response.json())} samples")
```

**Success Criteria Day 5:**
- ✅ Monitoring module created
- ✅ API endpoints работают
- ✅ CPU/RAM/Disk/Network tracked
- ✅ Health status calculated
- ✅ Metric history available

---

## 📊 WEEK 2 SUCCESS METRICS

**Must Have (P0):**
- ✅ WinRM configured and tested
- ✅ Server connects to real workstation
- ✅ Real emulators visible in UI
- ✅ Start/Stop works on real hardware

**Should Have (P1):**
- ✅ 20+ automated tests written
- ✅ 75%+ code coverage
- ✅ Monitoring endpoints working
- ✅ Health status tracking

**Could Have (P2):**
- ⚠️ Retry logic with exponential backoff
- ⚠️ Timeout management
- ⚠️ Circuit breakers

---

## 🎉 EXPECTED OUTCOMES

**After Week 2, you will have:**

1. **Production-Ready Connections** ✅
   - Real workstation management
   - Actual emulator control
   - No mock data dependency

2. **Quality Assurance** ✅
   - 20+ automated tests
   - 75%+ code coverage
   - CI/CD ready

3. **Operational Visibility** ✅
   - System metrics tracking
   - Health monitoring
   - Performance data

4. **System Progress: 75%** ✅
   - Week 1: 50% → Week 2: 75%
   - Ready for Week 3-4 polish
   - Pre-production state

---

## 🚀 NEXT STEPS AFTER WEEK 2

**Week 3-4 Focus:**
- Production deployment
- Performance tuning
- Advanced features (circuit breakers, graceful shutdown)
- Documentation finalization

**You're on track for production! 🎯**

---

**Created:** 17 октября 2025  
**Target Completion:** 22 октября 2025  
**Status:** 📅 Ready to Execute
