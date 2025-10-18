#!/usr/bin/env python3
"""
Простой запуск сервера для тестирования.
"""

import sys
from pathlib import Path

# Добавить корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

import uvicorn
from src.core.server import app

if __name__ == "__main__":
    print("🚀 Запуск LDPlayer Management System Server")
    print("=" * 60)
    print("Сервер: http://127.0.0.1:8001")
    print("Swagger UI: http://127.0.0.1:8001/docs")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8001,
        log_level="info"
    )
