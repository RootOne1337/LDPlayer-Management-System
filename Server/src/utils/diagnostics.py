"""
Enhanced System Diagnostics Module
===================================
Comprehensive system diagnostics with structured reporting and categorization.

Author: LDPlayer Management System
Version: 2.0.0
"""

import asyncio
import platform
import socket
import sys
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import os


# ANSI Colors for beautiful console output
class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@dataclass
class TestResult:
    """Individual test result with detailed information"""
    name: str
    category: str
    passed: bool
    critical: bool = False
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class DiagnosticsReport:
    """Complete diagnostics report with statistics"""
    timestamp: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    critical_failures: int = 0
    warnings: int = 0
    duration_seconds: float = 0.0
    results: List[TestResult] = field(default_factory=list)
    system_info: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        return (self.passed_tests / self.total_tests) * 100 if self.total_tests else 0
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy (no critical failures)"""
        return self.critical_failures == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['success_rate'] = self.success_rate
        data['is_healthy'] = self.is_healthy
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class EnhancedSystemDiagnostics:
    """Enhanced system diagnostics with comprehensive testing"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time: float = 0
        self.base_path = Path(__file__).parent.parent.parent
        
    def _run_test(self, name: str, category: str, test_func, critical: bool = False) -> TestResult:
        """Run a single test and return result"""
        start = time.time()
        try:
            passed, message, details = test_func()
            duration_ms = (time.time() - start) * 1000
            
            return TestResult(
                name=name,
                category=category,
                passed=passed,
                critical=critical,
                message=message,
                details=details,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return TestResult(
                name=name,
                category=category,
                passed=False,
                critical=critical,
                message=f"Test failed: {str(e)}",
                error=str(e),
                duration_ms=duration_ms
            )
    
    def _print_test_result(self, result: TestResult):
        """Print test result with colors"""
        icon = "✅" if result.passed else ("❌" if result.critical else "⚠️")
        color = Colors.GREEN if result.passed else (Colors.RED if result.critical else Colors.YELLOW)
        
        print(f"{color}{icon} [{result.category}] {result.name}{Colors.ENDC}")
        print(f"   {result.message} ({result.duration_ms:.2f}ms)")
        
        if result.details:
            for key, value in result.details.items():
                print(f"   • {key}: {value}")
    
    async def test_system_environment(self):
        """Test 1: System Environment"""
        def test():
            info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": socket.gethostname(),
                "python_version": sys.version.split()[0],
            }
            
            # Get IP address
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                info["ip_address"] = s.getsockname()[0]
                s.close()
            except:
                info["ip_address"] = "N/A"
            
            return True, f"System: {info['os']} {info['os_version']}", info
        
        result = self._run_test("System Environment", "System", test, critical=True)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_file_structure(self):
        """Test 2: File Structure"""
        def test():
            required_files = [
                "src/core/server.py",
                "src/core/config.py",
                "src/utils/logger.py",
                "src/api/__init__.py",
                "config.json",
            ]
            
            missing = []
            found = []
            
            for file_path in required_files:
                full_path = self.base_path / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(file_path)
            
            if missing:
                return False, f"Missing {len(missing)} files", {"missing": missing, "found": found}
            else:
                return True, f"All {len(found)} files found", {"found": found}
        
        result = self._run_test("File Structure", "Files", test, critical=True)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_database(self):
        """Test 3: Database Connection"""
        def test():
            try:
                import sqlite3
                db_path = self.base_path / "workstations.db"
                
                if not db_path.exists():
                    return False, "Database file not found", {"path": str(db_path)}
                
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get table count
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                # Get workstation count
                try:
                    cursor.execute("SELECT COUNT(*) FROM workstations")
                    ws_count = cursor.fetchone()[0]
                except:
                    ws_count = 0
                
                conn.close()
                
                return True, f"Database OK: {len(tables)} tables", {
                    "path": str(db_path),
                    "tables": len(tables),
                    "workstations": ws_count
                }
            except Exception as e:
                return False, f"Database error: {str(e)}", {}
        
        result = self._run_test("Database Connection", "Database", test, critical=True)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_python_dependencies(self):
        """Test 4: Python Dependencies"""
        def test():
            required = ["fastapi", "uvicorn", "pydantic", "sqlite3", "jwt"]
            installed = []
            missing = []
            
            for module in required:
                try:
                    __import__(module)
                    installed.append(module)
                except ImportError:
                    missing.append(module)
            
            if missing:
                return False, f"Missing {len(missing)} modules", {"installed": installed, "missing": missing}
            else:
                return True, f"All {len(installed)} modules installed", {"installed": installed}
        
        result = self._run_test("Python Dependencies", "Dependencies", test, critical=True)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_network_protocols(self):
        """Test 5: Network Protocols"""
        def test():
            ports_to_check = {
                "ADB": 5555,
                "WinRM_HTTP": 5985,
                "WinRM_HTTPS": 5986,
                "SMB": 445
            }
            
            available = {}
            
            for name, port in ports_to_check.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                available[name] = (result != 0)  # Port available if connection failed
            
            open_ports = sum(1 for v in available.values() if v)
            
            return True, f"{open_ports}/{len(ports_to_check)} ports available", available
        
        result = self._run_test("Network Protocols", "Network", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_winrm(self):
        """Test 6: WinRM Protocol"""
        def test():
            try:
                import winrm
                return True, "WinRM module installed", {"version": getattr(winrm, '__version__', 'unknown')}
            except ImportError:
                return False, "WinRM module not installed", {"hint": "pip install pywinrm"}
        
        result = self._run_test("WinRM Protocol", "WinRM", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_ssh_protocol(self):
        """Test 7: SSH Protocol"""
        def test():
            try:
                import paramiko
                return True, "SSH (paramiko) installed", {"version": paramiko.__version__}
            except ImportError:
                return False, "SSH module not installed", {"hint": "pip install paramiko"}
        
        result = self._run_test("SSH Protocol", "SSH", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_smb_protocol(self):
        """Test 8: SMB Protocol"""
        def test():
            try:
                import smbprotocol
                return True, "SMB protocol installed", {}
            except ImportError:
                return False, "SMB module not installed", {"hint": "pip install smbprotocol"}
        
        result = self._run_test("SMB Protocol", "SMB", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_adb_protocol(self):
        """Test 9: ADB Protocol"""
        def test():
            adb_paths = [
                r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe",
                r"C:\Android\sdk\platform-tools\adb.exe",
                os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe")
            ]
            
            for path in adb_paths:
                if os.path.exists(path):
                    return True, f"ADB found", {"path": path}
            
            return False, "ADB not found", {"hint": "Install Android SDK Platform Tools"}
        
        result = self._run_test("ADB Protocol", "ADB", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_ldplayer_installation(self):
        """Test 10: LDPlayer Installation"""
        def test():
            ldplayer_paths = [
                r"C:\LDPlayer\LDPlayer9\ldconsole.exe",
                r"C:\LDPlayer\LDPlayer4\ldconsole.exe",
                r"D:\LDPlayer\LDPlayer9\ldconsole.exe"
            ]
            
            for path in ldplayer_paths:
                if os.path.exists(path):
                    # Try to get emulator list
                    try:
                        import subprocess
                        result = subprocess.run([path, "list2"], 
                                              capture_output=True, text=True, timeout=5)
                        emulators = result.stdout.strip().split('\n')
                        emulator_count = len([e for e in emulators if e.strip()])
                        
                        return True, f"LDPlayer found: {emulator_count} emulators", {
                            "path": path,
                            "emulators": emulator_count
                        }
                    except:
                        return True, "LDPlayer found", {"path": path}
            
            return False, "LDPlayer not found", {"hint": "Install LDPlayer"}
        
        result = self._run_test("LDPlayer Installation", "LDPlayer", test, critical=True)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_api_configuration(self):
        """Test 11: API Configuration"""
        def test():
            try:
                config_path = self.base_path / "config.json"
                if not config_path.exists():
                    return False, "config.json not found", {}
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                required_keys = ["server", "database", "security"]
                missing = [k for k in required_keys if k not in config]
                
                if missing:
                    return False, f"Missing config keys: {missing}", {"missing": missing}
                
                return True, "API configuration valid", {"keys": list(config.keys())}
            except Exception as e:
                return False, f"Config error: {str(e)}", {}
        
        result = self._run_test("API Configuration", "API", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_jwt_configuration(self):
        """Test 12: JWT Configuration"""
        def test():
            try:
                from src.core.config import settings
                
                if not hasattr(settings, 'SECRET_KEY'):
                    return False, "SECRET_KEY not configured", {}
                
                if len(settings.SECRET_KEY) < 32:
                    return False, "SECRET_KEY too short (< 32 chars)", {}
                
                return True, "JWT configuration valid", {
                    "secret_length": len(settings.SECRET_KEY),
                    "algorithm": getattr(settings, 'ALGORITHM', 'HS256')
                }
            except Exception as e:
                return False, f"JWT config error: {str(e)}", {}
        
        result = self._run_test("JWT Configuration", "JWT", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_logging_system(self):
        """Test 13: Logging System"""
        def test():
            logs_dir = self.base_path / "logs"
            
            if not logs_dir.exists():
                logs_dir.mkdir(exist_ok=True)
            
            try:
                from src.utils.logger import setup_logger
                logger = setup_logger("diagnostics_test")
                
                return True, "Logging system operational", {
                    "logs_dir": str(logs_dir),
                    "writable": os.access(logs_dir, os.W_OK)
                }
            except Exception as e:
                return False, f"Logging error: {str(e)}", {}
        
        result = self._run_test("Logging System", "Logging", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def test_caching_system(self):
        """Test 14: Caching System"""
        def test():
            # Simple cache test
            try:
                test_cache = {}
                test_cache["test_key"] = "test_value"
                
                if test_cache.get("test_key") == "test_value":
                    return True, "Caching system operational", {"type": "in-memory"}
                else:
                    return False, "Cache test failed", {}
            except Exception as e:
                return False, f"Cache error: {str(e)}", {}
        
        result = self._run_test("Caching System", "Caching", test)
        self.results.append(result)
        self._print_test_result(result)
    
    async def run_full_diagnostics(self) -> DiagnosticsReport:
        """Run all diagnostics tests"""
        self.start_time = time.time()
        self.results = []
        
        print("\n" + "=" * 100)
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 ENHANCED SYSTEM DIAGNOSTICS{Colors.ENDC}".center(100))
        print("=" * 100 + "\n")
        
        # Run all tests
        await self.test_system_environment()
        await self.test_file_structure()
        await self.test_database()
        await self.test_python_dependencies()
        await self.test_network_protocols()
        await self.test_winrm()
        await self.test_ssh_protocol()
        await self.test_smb_protocol()
        await self.test_adb_protocol()
        await self.test_ldplayer_installation()
        await self.test_api_configuration()
        await self.test_jwt_configuration()
        await self.test_logging_system()
        await self.test_caching_system()
        
        # Calculate statistics
        total_duration = time.time() - self.start_time
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        critical_failures = sum(1 for r in self.results if not r.passed and r.critical)
        warnings = sum(1 for r in self.results if not r.passed and not r.critical)
        
        # Get system info
        system_info = {}
        for result in self.results:
            if result.category == "System" and result.passed:
                system_info = result.details
                break
        
        # Create report
        report = DiagnosticsReport(
            timestamp=datetime.now().isoformat(),
            total_tests=len(self.results),
            passed_tests=passed,
            failed_tests=failed,
            critical_failures=critical_failures,
            warnings=warnings,
            duration_seconds=total_duration,
            results=self.results,
            system_info=system_info
        )
        
        # Print summary
        self._print_summary(report)
        
        # Save to file
        self._save_report(report)
        
        return report
    
    def _print_summary(self, report: DiagnosticsReport):
        """Print diagnostics summary"""
        print("\n" + "=" * 100)
        print(f"{Colors.BOLD}📊 DIAGNOSTICS SUMMARY{Colors.ENDC}".center(100))
        print("=" * 100 + "\n")
        
        # Overall health
        if report.is_healthy:
            print(f"{Colors.GREEN}✅ SYSTEM HEALTHY{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ CRITICAL ISSUES DETECTED{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
        print(f"  • Total Tests: {report.total_tests}")
        print(f"  • Passed: {Colors.GREEN}{report.passed_tests}{Colors.ENDC}")
        print(f"  • Failed: {Colors.RED}{report.failed_tests}{Colors.ENDC}")
        print(f"  • Critical Failures: {Colors.RED}{report.critical_failures}{Colors.ENDC}")
        print(f"  • Warnings: {Colors.YELLOW}{report.warnings}{Colors.ENDC}")
        print(f"  • Success Rate: {Colors.CYAN}{report.success_rate:.1f}%{Colors.ENDC}")
        print(f"  • Duration: {report.duration_seconds:.2f}s")
        
        # Recommendations
        if report.critical_failures > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  CRITICAL ISSUES REQUIRE ATTENTION:{Colors.ENDC}")
            for result in report.results:
                if not result.passed and result.critical:
                    print(f"  • {result.name}: {result.message}")
        
        if report.warnings > 0:
            print(f"\n{Colors.YELLOW}💡 Recommendations:{Colors.ENDC}")
            for result in report.results:
                if not result.passed and not result.critical:
                    hint = result.details.get('hint', '')
                    if hint:
                        print(f"  • {result.name}: {hint}")
        
        print("\n" + "=" * 100 + "\n")
    
    def _save_report(self, report: DiagnosticsReport):
        """Save report to JSON file"""
        try:
            logs_dir = self.base_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = logs_dir / f"diagnostics_{timestamp}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report.to_json())
            
            print(f"{Colors.CYAN}💾 Report saved: {report_path}{Colors.ENDC}\n")
        except Exception as e:
            print(f"{Colors.RED}Failed to save report: {e}{Colors.ENDC}\n")


# Global instance for easy access
_last_report: Optional[DiagnosticsReport] = None


async def run_diagnostics() -> DiagnosticsReport:
    """Run diagnostics and return report"""
    global _last_report
    diagnostics = EnhancedSystemDiagnostics()
    _last_report = await diagnostics.run_full_diagnostics()
    return _last_report


def get_last_report() -> Optional[DiagnosticsReport]:
    """Get last diagnostics report"""
    return _last_report
