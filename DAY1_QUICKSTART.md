# 🚀 WEEK 2 DAY 1 - QUICK START GUIDE

**Date:** October 18, 2025  
**Goal:** Connect to Real Workstation via WinRM  
**Time:** 4-6 hours  
**Status:** 🎯 Ready to Execute

---

## ✅ WHAT YOU HAVE NOW

### Scripts Created (3 new files):
```
Server/
├── test_winrm_connection.py ... 🧪 Test WinRM connectivity
├── encrypt_password.py ......... 🔐 Encrypt passwords  
└── add_workstation.py .......... ➕ Add workstation to config
```

### System Status:
- ✅ Backend running: http://localhost:8000
- ✅ Frontend running: http://localhost:3000
- ✅ Mock data active (6 emulators, 4 workstations)

---

## 🎯 DAY 1 TASKS

### ⏰ Task 1: Prepare Test Machine (30 min)

**1.1 Choose a test machine:**
```
Requirements:
✓ Windows 10/11
✓ LDPlayer installed
✓ Network accessible
✓ Administrator access

Record info:
IP Address: _____________ (e.g., 192.168.1.101)
Username:   _____________ (e.g., admin)
Password:   _____________ (keep secure!)
```

**1.2 Verify LDPlayer installation:**
```powershell
# On the test machine, check:
Test-Path "C:\Program Files\LDPlayer\LDPlayer4.0\dnconsole.exe"

# If False, find correct path:
Get-ChildItem "C:\" -Recurse -Filter "dnconsole.exe" -ErrorAction SilentlyContinue
```

---

### ⏰ Task 2: Enable WinRM (30 min)

**On the REMOTE test machine (as Administrator):**

```powershell
# Step 1: Quick config (enables WinRM service)
winrm quickconfig
# Press Y for all prompts

# Step 2: Enable PowerShell Remoting
Enable-PSRemoting -Force

# Step 3: Set trusted hosts (allows any host to connect)
Set-Item WSMan:\localhost\Client\TrustedHosts "*" -Force

# Step 4: Enable Basic Authentication (required for PyWinRM)
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'

# Step 5: Verify configuration
winrm get winrm/config

# Step 6: Check WinRM service status
Get-Service WinRM

# Step 7: Open firewall (if needed)
netsh advfirewall firewall add rule name="WinRM-HTTP" dir=in action=allow protocol=TCP localport=5985

# Step 8: Test locally
Test-WSMan -ComputerName localhost
```

**Expected Output:**
```
wsmid           : http://schemas.dmtf.org/wbem/wsman/identity/1/wsmanidentity.xsd
ProtocolVersion : http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd
ProductVendor   : Microsoft Corporation
ProductVersion  : OS: 10.0.19045 SP: 0.0 Stack: 3.0
```

---

### ⏰ Task 3: Test Connection (1 hour)

**On YOUR development machine:**

**3.1 Update test script:**
```powershell
cd C:\Users\dimas\Documents\Remote\LDPlayerManagementSystem\Server

# Open test_winrm_connection.py in editor
code test_winrm_connection.py

# Update these lines (around line 17-19):
HOST = "192.168.1.101"      # ⬅️ YOUR REMOTE MACHINE IP
USERNAME = "admin"           # ⬅️ YOUR USERNAME
PASSWORD = "your_password"   # ⬅️ YOUR PASSWORD
```

**3.2 Run test:**
```powershell
python test_winrm_connection.py
```

**Expected Success Output:**
```
============================================================
  🔌 WinRM Connection Test Suite
============================================================
📅 Date: 2025-10-18 10:00:00
🎯 Target: 192.168.1.101
👤 User: admin

ℹ️  Initializing WinRM connection...
✅ WinRM protocol initialized

============================================================
  Test 1: Basic WinRM Connection
============================================================
✅ WinRM connection established!
ℹ️  Response: WinRM Connection Test

============================================================
  Test 2: System Information
============================================================
✅ System info retrieved!
ℹ️  System Details:
    Hostname: DESKTOP-ABC123
    OS: Microsoft Windows 10 Pro
    Version: 10.0.19045
    Architecture: 64-bit
    Memory: 16.00 GB

============================================================
  Test 3: LDPlayer Installation & Emulators
============================================================
ℹ️  Checking LDPlayer installation paths...
✅ LDPlayer found at: C:\Program Files\LDPlayer\LDPlayer4.0
ℹ️  Checking dnconsole.exe...
✅ dnconsole.exe found!
ℹ️  Listing emulators...
✅ Found 2 emulator(s)!
ℹ️  Emulator List:
    [0] Android-Game-1 - Status: running
    [1] Android-Game-2 - Status: stopped

============================================================
  📊 Test Results Summary
============================================================
✅ PASS  Test 1 - Basic Connection
✅ PASS  Test 2 - System Info
✅ PASS  Test 3 - LDPlayer Detection

============================================================
📈 Results: 3/3 tests passed (100.0%)
============================================================

🎉 SUCCESS! All tests passed!

📋 Next Steps:
   1. Update Server/config.json with this workstation
   2. Encrypt password using SecurityManager
   3. Run server in production mode (without DEV_MODE)
   4. Check UI for real emulators!
```

**If tests fail:**
```
Common issues and fixes in WEEK2_PLAN.md Day 1, Task 3.2
```

---

### ⏰ Task 4: Add Workstation to Config (30 min)

**Method 1: Automated (Recommended)**
```powershell
cd Server
python add_workstation.py
```

Follow the prompts:
```
Workstation ID: ws-prod-1
Workstation Name: Production Workstation 1
Workstation IP/Hostname: 192.168.1.101
Protocol: winrm
LDPlayer Path: C:\Program Files\LDPlayer\LDPlayer4.0
Username: admin
Password: ********
Confirm Password: ********

⏳ Encrypting password...
✅ Password encrypted

✅ Workstation added to config.json
```

**Method 2: Manual**

**Step 1: Encrypt password**
```powershell
python encrypt_password.py
```

**Step 2: Edit config.json**
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "ssl": {
      "enabled": false
    }
  },
  "workstations": [
    {
      "id": "ws-prod-1",
      "name": "Production Workstation 1",
      "host": "192.168.1.101",
      "protocol": "winrm",
      "ldplayer_path": "C:\\Program Files\\LDPlayer\\LDPlayer4.0",
      "auth": {
        "username": "admin",
        "password": "gAAAAABm... (encrypted string from step 1)"
      },
      "enabled": true
    }
  ],
  "users": [
    {
      "username": "admin",
      "password": "existing_encrypted_password",
      "role": "admin",
      "enabled": true
    }
  ]
}
```

---

### ⏰ Task 5: Run Production Mode (1 hour)

**5.1 Stop DEV mode server**
```powershell
# Stop backend (Ctrl+C in backend terminal)
# Keep frontend running
```

**5.2 Start production server**
```powershell
cd Server
python run_server_stable.py
```

**Expected Output:**
```
2025-10-18 10:00:00 [INFO] 🚀 Starting LDPlayer Management Server...
2025-10-18 10:00:00 [INFO] 📋 Loaded 1 workstation(s) from config
2025-10-18 10:00:00 [INFO] 🔗 Connecting to workstation: Production Workstation 1 (192.168.1.101)...
2025-10-18 10:00:01 [INFO] ✅ Connected via WinRM
2025-10-18 10:00:01 [INFO] 🎮 Detecting emulators...
2025-10-18 10:00:02 [INFO] ✅ Found 2 emulators: [Android-Game-1, Android-Game-2]
2025-10-18 10:00:02 [INFO] 🌐 Server started on https://localhost:8000
2025-10-18 10:00:02 [INFO] 📖 API Docs: https://localhost:8000/docs
```

**If errors occur:**
- Check config.json syntax (valid JSON)
- Verify encrypted password is correct
- Check WinRM is still running on remote machine
- See troubleshooting section below

---

### ⏰ Task 6: Verify in UI (30 min)

**6.1 Open Web UI**
```
http://localhost:3000
```

**6.2 Login**
```
Username: admin
Password: admin123
```

**6.3 Check Dashboard**
```
✓ Should show 1 online workstation (not 3 mock ones)
✓ Should show 2 real emulators (not 6 mock ones)
✓ Statistics should be real data
```

**6.4 Check Emulators Page**
```
✓ Should list 2 real emulators
✓ Names should match your LDPlayer emulators
✓ Status should be accurate (running/stopped)
```

**6.5 Test Operations**
```
✓ Click Start on a stopped emulator
✓ Wait 10-15 seconds
✓ Emulator should actually start on remote machine!
✓ Status should update to "running"

✓ Click Stop on a running emulator
✓ Wait 5 seconds
✓ Emulator should actually stop
✓ Status should update to "stopped"
```

---

## ✅ DAY 1 SUCCESS CRITERIA

Check all that apply:
- [ ] WinRM enabled on remote machine
- [ ] test_winrm_connection.py passes all 3 tests
- [ ] Workstation added to config.json
- [ ] Production server connects to workstation
- [ ] UI shows real workstation (not mock)
- [ ] UI shows real emulators (not mock)
- [ ] Start button actually starts emulator
- [ ] Stop button actually stops emulator

**If all checked: 🎉 DAY 1 COMPLETE!**

---

## 🆘 TROUBLESHOOTING

### Issue: "Connection refused" or "Timeout"
```
Possible causes:
✗ WinRM not enabled
✗ Firewall blocking port 5985
✗ Wrong IP address
✗ Remote machine offline

Fix:
1. On remote machine:
   winrm quickconfig
   Get-Service WinRM  # Should be "Running"
   
2. Check firewall:
   Test-NetConnection -ComputerName 192.168.1.101 -Port 5985
   
3. Verify IP:
   ping 192.168.1.101
```

### Issue: "Access denied" or "401 Unauthorized"
```
Possible causes:
✗ Wrong username/password
✗ Basic auth not enabled

Fix:
1. Verify credentials
2. On remote machine:
   winrm set winrm/config/service/auth '@{Basic="true"}'
   winrm get winrm/config/service/auth  # Verify Basic = true
```

### Issue: "LDPlayer not found"
```
Possible causes:
✗ LDPlayer installed in different location
✗ Path incorrect in config.json

Fix:
1. On remote machine, find LDPlayer:
   Get-ChildItem "C:\" -Recurse -Filter "dnconsole.exe" -ErrorAction SilentlyContinue
   
2. Update config.json with correct path:
   "ldplayer_path": "D:\\LDPlayer\\LDPlayer4.0"
```

### Issue: "No emulators found"
```
This is OK! You can:
1. Create emulators in LDPlayer on remote machine
2. Or continue without emulators (test with empty list)
```

### Issue: Server starts but UI still shows mock data
```
Possible causes:
✗ Backend still in DEV_MODE
✗ Old server process still running

Fix:
1. Kill all python processes
2. Verify run_server_stable.py (NOT run_dev_ui.py)
3. Check logs for "DEV режиме" message (should NOT appear)
4. Hard refresh browser (Ctrl+F5)
```

---

## 📊 PROGRESS TRACKING

**Time spent:**
- [ ] Task 1: _____ min (estimated: 30)
- [ ] Task 2: _____ min (estimated: 30)
- [ ] Task 3: _____ min (estimated: 60)
- [ ] Task 4: _____ min (estimated: 30)
- [ ] Task 5: _____ min (estimated: 60)
- [ ] Task 6: _____ min (estimated: 30)

**Total:** _____ min / 240 min (4 hours)

---

## 🎯 NEXT: DAY 2

After completing Day 1:
```
✓ Read WEEK2_PLAN.md Day 2 section
✓ Goals: Stability improvements
✓ Tasks: Error handling, timeouts, retry logic
```

---

**Created:** October 18, 2025  
**Status:** ✅ Ready to Execute  
**Progress:** Week 2 Day 1 / 5
