# Session 8: Next Steps & Implementation Plan

**Prepared by:** Session 7 Audit  
**Current Status:** 85% readiness (up from 75%)  
**Target:** 90%+ readiness  

---

## 🎯 Session 8 Overview

Session 7 выявил **IMPORTANT и MEDIUM** issues которые нужны на Session 8. Вот конкретный план.

---

## 🔴 Priority 1: IMPORTANT Audit Fixes (1-2 hours)

### 1.1 Fallback Implementations for Missing Dependencies

**Location:** `src/services/emulator_service.py`, `src/core/server.py`

**Issue:** Если какая-то зависимость отсутствует, код падает вместо graceful fallback.

**Action Plan:**

```python
# BEFORE: No fallback
try:
    emulators = self.manager.get_emulators()
except Exception as e:
    # Just crashes
    raise

# AFTER: Proper fallback
def get_emulators(self) -> List[Emulator]:
    """Get all emulators with graceful fallback."""
    try:
        return self.manager.get_emulators()
    except ConnectionError:
        logger.warning("LDPlayer not accessible, returning cached emulators")
        return self._cached_emulators or []
    except Exception as e:
        logger.error(f"Error getting emulators: {e}")
        return []  # Empty list fallback
```

**Tests Needed:**
- [ ] Test behavior when LDPlayer is offline
- [ ] Test cache usage when offline
- [ ] Test recovery when LDPlayer comes back online

**Estimated Time:** 30 minutes

---

### 1.2 Auth Module-Level Initialization Issues

**Location:** `src/api/auth.py`, `src/api/auth_routes.py`

**Issue:** Некоторый initialization code выполняется на уровне модуля (когда импортируется), а не в startup event.

**Current Code (Problematic):**
```python
# src/api/auth.py line 15-20
# This runs when module is imported, may fail silently
default_users = init_default_users()  # ← BAD: Runs at import time
```

**Action Plan:**

```python
# BETTER: Initialize in startup
async def lifespan(app: FastAPI):
    """Application lifespan - startup/shutdown."""
    # Startup
    init_default_users()  # ← GOOD: Runs during startup
    
    yield
    
    # Shutdown
    await cleanup_resources()

app = FastAPI(lifespan=lifespan)
```

**Tests Needed:**
- [ ] Test auth initialization during startup
- [ ] Test that default users are created
- [ ] Test error handling if init fails

**Estimated Time:** 45 minutes

---

## 🟠 Priority 2: Missing Endpoints (1-2 hours)

### 2.1 PATCH Endpoint for Workstations

**Location:** `src/api/workstations.py`

**Current Status:** Endpoint exists but test is skipped (in test_integration.py:184)

**Action Plan:**

```python
# src/api/workstations.py
@router.patch("/{workstation_id}")
async def update_workstation(
    workstation_id: str,
    update: UpdateWorkstationRequest,  # Define this schema
    service: WorkstationService = Depends(get_workstation_service)
) -> WorkstationResponse:
    """Update workstation configuration."""
    updated = await service.update_workstation(workstation_id, update)
    return WorkstationResponse.from_model(updated)
```

**Schema Needed:**
```python
class UpdateWorkstationRequest(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict] = None
    # ... other updatable fields
```

**Tests Needed:**
- [ ] Test successful update
- [ ] Test partial update
- [ ] Test validation errors

**Estimated Time:** 45 minutes

---

### 2.2 DELETE Endpoint for Workstations

**Location:** `src/api/workstations.py`

**Current Status:** Endpoint exists but test is skipped

**Action Plan:**

```python
# src/api/workstations.py
@router.delete("/{workstation_id}")
async def delete_workstation(
    workstation_id: str,
    service: WorkstationService = Depends(get_workstation_service)
) -> Dict[str, str]:
    """Delete workstation."""
    await service.delete_workstation(workstation_id)
    return {"message": "Workstation deleted"}
```

**Tests Needed:**
- [ ] Test successful deletion
- [ ] Test 404 when not found
- [ ] Test cascade deletion of emulators

**Estimated Time:** 30 minutes

---

## 🟡 Priority 3: Input Validation (1 hour)

### 3.1 Comprehensive Input Validation

**Issue:** Not all API inputs are validated. Need to add validation to ALL endpoints.

**Action Plan:**

```python
# Create validation utility
# src/utils/validators.py

def validate_workstation_name(name: str) -> str:
    """Validate workstation name format."""
    if not name or len(name) < 3:
        raise ValueError("Name must be at least 3 characters")
    if not name.replace('_', '').replace('-', '').isalnum():
        raise ValueError("Name can only contain alphanumeric, -, _")
    return name

def validate_emulator_config(config: Dict) -> Dict:
    """Validate emulator configuration."""
    required_fields = ['width', 'height', 'dpi']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    return config

# Use in endpoints
@router.post("/")
async def create_emulator(
    emulator: CreateEmulatorRequest,
    service: EmulatorService = Depends(...)
):
    # Validation happens automatically via Pydantic
    # But add custom validation too
    validate_emulator_config(emulator.config)
    return await service.create_emulator(emulator)
```

**Tests Needed:**
- [ ] Test all validation rules
- [ ] Test error messages
- [ ] Test edge cases

**Estimated Time:** 1 hour

---

## 🔵 Priority 4: Logging Unification (30 minutes)

### 4.1 Unify Logging Across Modules

**Current State:** Different modules use different logging patterns

**Action Plan:**

```python
# src/utils/logger.py - Define standard logging functions

class StandardLogger:
    @staticmethod
    def info(message: str, module: str, data: Dict = None):
        """Standard info logging."""
        logger.info(f"[{module}] {message}", extra={"data": data})
    
    @staticmethod
    def error(message: str, module: str, exception: Exception = None):
        """Standard error logging."""
        logger.error(f"[{module}] {message}", exc_info=exception)
    
    @staticmethod
    def warning(message: str, module: str):
        """Standard warning logging."""
        logger.warning(f"[{module}] {message}")

# Use consistently everywhere
from utils.logger import StandardLogger
StandardLogger.info("Emulator started", "EmulatorService", {"id": emulator_id})
```

**Estimated Time:** 30 minutes

---

## 📊 Session 8 Timeline

```
Priority 1: Fallbacks + Auth Init    → 1.5 hours ⏱️
Priority 2: PATCH/DELETE endpoints   → 1 hour ⏱️  
Priority 3: Input validation         → 1 hour ⏱️
Priority 4: Logging unification      → 0.5 hours ⏱️
─────────────────────────────────────────────────
Total Estimated Time:                 4 hours
```

---

## 🎯 Expected Outcomes (Session 8)

| Item | Current | After Session 8 |
|------|---------|-----------------|
| Readiness | 85% | 90%+ |
| Tests Passing | 125/125 | 132+/132+ |
| Failures | 0 | 0 |
| IMPORTANT Issues | 3 | 0 |
| PATCH/DELETE Endpoints | ❌ Skipped | ✅ Working |
| Fallback Mechanisms | ❌ None | ✅ Implemented |

---

## ✅ Verification Checklist for Session 8

Before marking as complete:

- [ ] All fallback mechanisms implemented
- [ ] Auth initialization in lifespan
- [ ] PATCH endpoint works and tested
- [ ] DELETE endpoint works and tested
- [ ] All inputs validated
- [ ] Logging unified across modules
- [ ] 130+ tests passing
- [ ] Server starts cleanly
- [ ] Zero regressions

---

## 📝 Code Templates Ready

All templates available in this file for copy-paste implementation.

**Files to modify:**
1. `src/services/emulator_service.py` - Add fallbacks
2. `src/api/auth.py` - Fix initialization
3. `src/api/workstations.py` - Add PATCH/DELETE
4. `src/utils/validators.py` - Create & add validation
5. `src/utils/logger.py` - Unify logging

---

## 🚀 Ready for Session 8

All issues clearly identified.  
All templates provided.  
All acceptance criteria defined.  
Expected duration: 4 hours.  
Expected final readiness: 90%+

**Next session ready to begin! 🎯**
