#!/usr/bin/env python3
"""
Real-Time Monitoring Dashboard for LDPlayer Management System

Features:
- Live workstation status monitoring
- Emulator count tracking
- Connection health checks
- Auto-refresh every 5 seconds
- Alert on failures
- Color-coded status display
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QStatusBar,
    QHeaderView, QGroupBox, QGridLayout, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QColor, QFont

# Add Server to path for imports
sys.path.insert(0, str(Path(__file__).parent / "Server"))

try:
    from src.core.config import get_config
    from src.remote.workstation import WorkstationManager
    from src.utils.logger import get_logger, LogCategory
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you're running from project root")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

REFRESH_INTERVAL = 5000  # 5 seconds
MAX_LOG_LINES = 100
ALERT_THRESHOLD = 3  # Alert after 3 consecutive failures

# Status colors
STATUS_COLORS = {
    "online": QColor(46, 204, 113),      # Green
    "offline": QColor(231, 76, 60),      # Red
    "warning": QColor(241, 196, 15),     # Yellow
    "unknown": QColor(149, 165, 166),    # Gray
}


# ============================================================================
# MONITORING WORKER THREAD
# ============================================================================

class MonitoringWorker(QThread):
    """Background thread for monitoring workstations"""
    
    # Signals
    status_updated = pyqtSignal(dict)  # {ws_id: {status, emulators, latency, error}}
    error_occurred = pyqtSignal(str, str)  # (ws_id, error_message)
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.logger = get_logger(LogCategory.API)
        self.running = True
        self.managers: Dict[str, WorkstationManager] = {}
        self.failure_counts: Dict[str, int] = defaultdict(int)
        
        # Initialize managers
        for ws_config in self.config.workstations:
            self.managers[ws_config.id] = WorkstationManager(ws_config)
    
    def run(self):
        """Main monitoring loop"""
        self.logger.info("Monitoring worker started")
        
        while self.running:
            results = {}
            
            for ws_id, manager in self.managers.items():
                try:
                    start_time = time.time()
                    
                    # Test connection
                    is_connected = manager.test_connection()
                    latency = int((time.time() - start_time) * 1000)  # ms
                    
                    if is_connected:
                        # Get emulator list
                        try:
                            code, output, stderr = manager.run_ldconsole_command("list2")
                            emulator_count = len([line for line in output.split('\n') if line.strip() and ',' in line])
                        except Exception as e:
                            emulator_count = 0
                            self.logger.warn(f"Failed to get emulators for {ws_id}: {e}")
                        
                        results[ws_id] = {
                            "status": "online",
                            "emulators": emulator_count,
                            "latency": latency,
                            "error": None,
                            "last_check": datetime.now().strftime("%H:%M:%S")
                        }
                        
                        # Reset failure count
                        self.failure_counts[ws_id] = 0
                    else:
                        # Connection failed
                        error_msg = manager.get_last_error() or "Connection failed"
                        results[ws_id] = {
                            "status": "offline",
                            "emulators": 0,
                            "latency": latency,
                            "error": error_msg,
                            "last_check": datetime.now().strftime("%H:%M:%S")
                        }
                        
                        # Increment failure count
                        self.failure_counts[ws_id] += 1
                        
                        # Emit alert if threshold exceeded
                        if self.failure_counts[ws_id] == ALERT_THRESHOLD:
                            self.error_occurred.emit(ws_id, error_msg)
                            self.logger.error(f"ALERT: {ws_id} failed {ALERT_THRESHOLD} times - {error_msg}")
                
                except Exception as e:
                    results[ws_id] = {
                        "status": "unknown",
                        "emulators": 0,
                        "latency": 0,
                        "error": str(e),
                        "last_check": datetime.now().strftime("%H:%M:%S")
                    }
                    self.logger.error(f"Monitoring error for {ws_id}: {e}")
            
            # Emit results
            self.status_updated.emit(results)
            
            # Sleep (check every 500ms if should stop)
            for _ in range(10):  # 10 * 500ms = 5s
                if not self.running:
                    break
                time.sleep(0.5)
        
        self.logger.info("Monitoring worker stopped")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False


# ============================================================================
# MAIN DASHBOARD WINDOW
# ============================================================================

class MonitoringDashboard(QMainWindow):
    """Main monitoring dashboard window"""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.logger = get_logger(LogCategory.API)
        self.worker: Optional[MonitoringWorker] = None
        self.alert_count = 0
        
        self.init_ui()
        self.start_monitoring()
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("LDPlayer Management System - Monitoring Dashboard")
        self.setGeometry(100, 100, 1200, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Splitter for table and logs
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Status table
        self.table = self.create_status_table()
        splitter.addWidget(self.table)
        
        # Event log
        log_group = QGroupBox("📋 Event Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        splitter.addWidget(log_group)
        
        splitter.setSizes([500, 200])
        layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Initializing monitoring...")
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def create_header(self) -> QWidget:
        """Create header with stats and controls"""
        header = QGroupBox()
        layout = QGridLayout()
        
        # Title
        title = QLabel("🖥️ Real-Time Workstation Monitoring")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title, 0, 0, 1, 4)
        
        # Stats labels
        self.stat_total = QLabel("Total: 0")
        self.stat_online = QLabel("🟢 Online: 0")
        self.stat_offline = QLabel("🔴 Offline: 0")
        self.stat_emulators = QLabel("📱 Emulators: 0")
        
        for label in [self.stat_total, self.stat_online, self.stat_offline, self.stat_emulators]:
            label.setFont(QFont("Arial", 12))
        
        layout.addWidget(self.stat_total, 1, 0)
        layout.addWidget(self.stat_online, 1, 1)
        layout.addWidget(self.stat_offline, 1, 2)
        layout.addWidget(self.stat_emulators, 1, 3)
        
        # Control buttons
        self.btn_refresh = QPushButton("🔄 Refresh Now")
        self.btn_refresh.clicked.connect(self.manual_refresh)
        
        self.btn_pause = QPushButton("⏸️ Pause")
        self.btn_pause.clicked.connect(self.toggle_monitoring)
        
        self.btn_clear_log = QPushButton("🗑️ Clear Log")
        self.btn_clear_log.clicked.connect(self.clear_log)
        
        layout.addWidget(self.btn_refresh, 2, 0)
        layout.addWidget(self.btn_pause, 2, 1)
        layout.addWidget(self.btn_clear_log, 2, 2)
        
        header.setLayout(layout)
        return header
    
    def create_status_table(self) -> QTableWidget:
        """Create workstation status table"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Workstation ID", "Name", "IP Address", "Status", 
            "Emulators", "Latency (ms)", "Last Check"
        ])
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        # Populate rows
        table.setRowCount(len(self.config.workstations))
        for i, ws in enumerate(self.config.workstations):
            table.setItem(i, 0, QTableWidgetItem(ws.id))
            table.setItem(i, 1, QTableWidgetItem(ws.name))
            table.setItem(i, 2, QTableWidgetItem(ws.ip_address))
            table.setItem(i, 3, QTableWidgetItem("Checking..."))
            table.setItem(i, 4, QTableWidgetItem("-"))
            table.setItem(i, 5, QTableWidgetItem("-"))
            table.setItem(i, 6, QTableWidgetItem("-"))
        
        return table
    
    def start_monitoring(self):
        """Start background monitoring"""
        self.worker = MonitoringWorker()
        self.worker.status_updated.connect(self.update_status)
        self.worker.error_occurred.connect(self.show_alert)
        self.worker.start()
        
        self.add_log("🚀 Monitoring started")
        self.status_bar.showMessage("Monitoring active - Refresh every 5 seconds")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
            self.add_log("⏹️ Monitoring stopped")
            self.status_bar.showMessage("Monitoring stopped")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.worker and self.worker.running:
            self.stop_monitoring()
            self.btn_pause.setText("▶️ Resume")
        else:
            self.start_monitoring()
            self.btn_pause.setText("⏸️ Pause")
    
    def manual_refresh(self):
        """Force immediate refresh"""
        self.add_log("🔄 Manual refresh triggered")
        # Monitoring worker will pick up on next cycle
    
    def update_status(self, results: Dict):
        """Update table with monitoring results"""
        online_count = 0
        offline_count = 0
        total_emulators = 0
        
        for i, ws in enumerate(self.config.workstations):
            ws_id = ws.id
            if ws_id not in results:
                continue
            
            data = results[ws_id]
            status = data["status"]
            emulators = data["emulators"]
            latency = data["latency"]
            last_check = data["last_check"]
            error = data.get("error")
            
            # Update counts
            if status == "online":
                online_count += 1
                total_emulators += emulators
            elif status == "offline":
                offline_count += 1
            
            # Update table cells
            status_item = QTableWidgetItem(status.upper())
            status_item.setBackground(STATUS_COLORS.get(status, STATUS_COLORS["unknown"]))
            self.table.setItem(i, 3, status_item)
            
            self.table.setItem(i, 4, QTableWidgetItem(str(emulators)))
            self.table.setItem(i, 5, QTableWidgetItem(str(latency) if latency > 0 else "-"))
            self.table.setItem(i, 6, QTableWidgetItem(last_check))
            
            # Log errors
            if error and status == "offline":
                self.add_log(f"❌ {ws_id}: {error}")
        
        # Update stats
        total = len(self.config.workstations)
        self.stat_total.setText(f"Total: {total}")
        self.stat_online.setText(f"🟢 Online: {online_count}")
        self.stat_offline.setText(f"🔴 Offline: {offline_count}")
        self.stat_emulators.setText(f"📱 Emulators: {total_emulators}")
        
        # Update status bar
        self.status_bar.showMessage(
            f"Last refresh: {datetime.now().strftime('%H:%M:%S')} | "
            f"Online: {online_count}/{total} | "
            f"Emulators: {total_emulators}"
        )
    
    def show_alert(self, ws_id: str, error: str):
        """Show alert for critical failure"""
        self.alert_count += 1
        alert_msg = f"⚠️ ALERT #{self.alert_count}: {ws_id} - {error}"
        self.add_log(alert_msg)
        self.logger.error(alert_msg)
    
    def add_log(self, message: str):
        """Add message to event log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        
        # Add to text widget
        self.log_text.append(log_line)
        
        # Limit log lines
        text = self.log_text.toPlainText()
        lines = text.split('\n')
        if len(lines) > MAX_LOG_LINES:
            self.log_text.setPlainText('\n'.join(lines[-MAX_LOG_LINES:]))
        
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def clear_log(self):
        """Clear event log"""
        self.log_text.clear()
        self.add_log("📋 Log cleared")
    
    def apply_dark_theme(self):
        """Apply dark theme to dashboard"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QGroupBox {
            border: 2px solid #555555;
            border-radius: 5px;
            margin-top: 10px;
            font-weight: bold;
            padding: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QTableWidget {
            background-color: #1e1e1e;
            alternate-background-color: #2b2b2b;
            gridline-color: #555555;
            selection-background-color: #3d3d3d;
        }
        QHeaderView::section {
            background-color: #3d3d3d;
            padding: 5px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        QPushButton {
            background-color: #0d7377;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #14a085;
        }
        QPushButton:pressed {
            background-color: #0a5a5d;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            color: #00ff00;
            font-family: Consolas;
        }
        QStatusBar {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_stylesheet)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.stop_monitoring()
        self.logger.info("Monitoring dashboard closed")
        event.accept()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show dashboard
    dashboard = MonitoringDashboard()
    dashboard.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
