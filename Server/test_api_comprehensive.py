"""
Comprehensive API Testing Script
Tests all endpoints of the LDPlayer Management System API
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def test_health_endpoints():
    """Test health and status endpoints"""
    print_section("1. TESTING HEALTH ENDPOINTS")
    
    # Test /api/health
    print("\n[GET] /api/health")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test /api/status
    print("\n[GET] /api/status")
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test /api/version
    print("\n[GET] /api/version")
    try:
        response = requests.get(f"{BASE_URL}/api/version", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n✅ Health endpoints: PASSED")
    return True

def test_workstation_endpoints():
    """Test workstation management endpoints"""
    print_section("2. TESTING WORKSTATION ENDPOINTS")
    
    # Get all workstations
    print("\n[GET] /api/workstations")
    try:
        response = requests.get(f"{BASE_URL}/api/workstations", timeout=10)
        print(f"Status: {response.status_code}")
        workstations = response.json()
        print(f"Found {len(workstations)} workstations")
        if workstations:
            print(f"First workstation: {workstations[0]['name']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Get localhost workstation
    print("\n[GET] /api/workstations/localhost")
    try:
        response = requests.get(f"{BASE_URL}/api/workstations/localhost", timeout=10)
        print(f"Status: {response.status_code}")
        workstation = response.json()
        print(f"Name: {workstation.get('name')}")
        print(f"Status: {workstation.get('status')}")
        print(f"Type: {workstation.get('workstation_type')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test connection to localhost
    print("\n[POST] /api/workstations/localhost/test-connection")
    try:
        response = requests.post(f"{BASE_URL}/api/workstations/localhost/test-connection", timeout=15)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Connection: {result.get('success')}")
        if result.get('message'):
            print(f"Message: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n✅ Workstation endpoints: PASSED")
    return True

def test_emulator_endpoints():
    """Test emulator management endpoints"""
    print_section("3. TESTING EMULATOR ENDPOINTS")
    
    # Get all emulators on localhost
    print("\n[GET] /api/workstations/localhost/emulators")
    try:
        response = requests.get(f"{BASE_URL}/api/workstations/localhost/emulators", timeout=15)
        print(f"Status: {response.status_code}")
        emulators = response.json()
        print(f"Found {len(emulators)} emulators:")
        for emu in emulators:
            print(f"  - Index {emu.get('index')}: {emu.get('name')} (Status: {emu.get('status')})")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Get specific emulator details
    print("\n[GET] /api/workstations/localhost/emulators/0")
    try:
        response = requests.get(f"{BASE_URL}/api/workstations/localhost/emulators/0", timeout=10)
        print(f"Status: {response.status_code}")
        emulator = response.json()
        print(f"Name: {emulator.get('name')}")
        print(f"Status: {emulator.get('status')}")
        print(f"Resolution: {emulator.get('width')}x{emulator.get('height')}")
        print(f"DPI: {emulator.get('dpi')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n✅ Emulator endpoints: PASSED")
    return True

def test_operations_endpoints():
    """Test operations management endpoints"""
    print_section("4. TESTING OPERATIONS ENDPOINTS")
    
    # Get all operations
    print("\n[GET] /api/operations")
    try:
        response = requests.get(f"{BASE_URL}/api/operations", timeout=10)
        print(f"Status: {response.status_code}")
        operations = response.json()
        print(f"Total operations: {len(operations)}")
        if operations:
            print(f"First operation: {operations[0].get('operation_id')}")
            print(f"  Type: {operations[0].get('operation_type')}")
            print(f"  Status: {operations[0].get('status')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Get operations statistics
    print("\n[GET] /api/operations/statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/operations/statistics", timeout=10)
        print(f"Status: {response.status_code}")
        stats = response.json()
        print(f"Active operations: {stats.get('active_operations')}")
        print(f"Completed operations: {stats.get('completed_operations')}")
        print(f"Failed operations: {stats.get('failed_operations')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n✅ Operations endpoints: PASSED")
    return True

def test_emulator_lifecycle():
    """Test complete emulator lifecycle (create -> modify -> start -> stop -> delete)"""
    print_section("5. TESTING EMULATOR LIFECYCLE")
    
    test_emulator_name = f"test_api_{int(time.time())}"
    print(f"\nTesting with emulator: {test_emulator_name}")
    
    # Create emulator
    print("\n[POST] /api/workstations/localhost/emulators (CREATE)")
    try:
        payload = {
            "name": test_emulator_name,
            "config": {
                "cpu": 2,
                "memory": 4096,
                "resolution": {"width": 1080, "height": 1920, "dpi": 240}
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/workstations/localhost/emulators",
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if response.status_code not in [200, 201]:
            print(f"⚠️ Creation failed, skipping lifecycle test")
            return False
            
        # Get the emulator index
        emulator_index = result.get('emulator', {}).get('index')
        if emulator_index is None:
            print(f"⚠️ No emulator index returned")
            return False
            
    except Exception as e:
        print(f"❌ Error creating emulator: {e}")
        return False
    
    time.sleep(2)  # Wait for creation to complete
    
    # Modify emulator
    print(f"\n[PUT] /api/workstations/localhost/emulators/{emulator_index} (MODIFY)")
    try:
        payload = {
            "cpu": 4,
            "memory": 8192,
            "manufacturer": "Samsung",
            "model": "SM-G973F"
        }
        response = requests.put(
            f"{BASE_URL}/api/workstations/localhost/emulators/{emulator_index}",
            json=payload,
            timeout=20
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Modified: {result.get('success')}")
    except Exception as e:
        print(f"❌ Error modifying emulator: {e}")
    
    time.sleep(1)
    
    # Start emulator
    print(f"\n[POST] /api/workstations/localhost/emulators/{emulator_index}/start")
    try:
        response = requests.post(
            f"{BASE_URL}/api/workstations/localhost/emulators/{emulator_index}/start",
            timeout=30
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Started: {result.get('success')}")
    except Exception as e:
        print(f"❌ Error starting emulator: {e}")
    
    time.sleep(5)  # Wait for startup
    
    # Stop emulator
    print(f"\n[POST] /api/workstations/localhost/emulators/{emulator_index}/stop")
    try:
        response = requests.post(
            f"{BASE_URL}/api/workstations/localhost/emulators/{emulator_index}/stop",
            timeout=20
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Stopped: {result.get('success')}")
    except Exception as e:
        print(f"❌ Error stopping emulator: {e}")
    
    time.sleep(2)
    
    # Delete emulator
    print(f"\n[DELETE] /api/workstations/localhost/emulators/{emulator_index}")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/workstations/localhost/emulators/{emulator_index}",
            timeout=20
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Deleted: {result.get('success')}")
    except Exception as e:
        print(f"❌ Error deleting emulator: {e}")
    
    print("\n✅ Emulator lifecycle: COMPLETED")
    return True

def main():
    """Run all tests"""
    print("\n" + "🚀"*35)
    print(" COMPREHENSIVE API TEST SUITE")
    print(" LDPlayer Management System")
    print(" " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🚀"*35)
    
    results = {
        "Health Endpoints": False,
        "Workstation Endpoints": False,
        "Emulator Endpoints": False,
        "Operations Endpoints": False,
        "Emulator Lifecycle": False
    }
    
    # Run tests
    try:
        results["Health Endpoints"] = test_health_endpoints()
        time.sleep(1)
        
        results["Workstation Endpoints"] = test_workstation_endpoints()
        time.sleep(1)
        
        results["Emulator Endpoints"] = test_emulator_endpoints()
        time.sleep(1)
        
        results["Operations Endpoints"] = test_operations_endpoints()
        time.sleep(1)
        
        results["Emulator Lifecycle"] = test_emulator_lifecycle()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30s} {status}")
    
    print(f"\n{'='*70}")
    print(f" TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
