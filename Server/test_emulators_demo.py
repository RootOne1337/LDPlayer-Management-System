#!/usr/bin/env python3
"""
Demo script: Управление эмуляторами через LDPlayer Management System API
Демонстрирует: Аутентификацию, получение списка, фильтрацию, пейджинг
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Default credentials
DEFAULT_USER = "admin"
DEFAULT_PASS = "admin"

class LDPlayerAPIClient:
    """Клиент для работы с LDPlayer Management API"""
    
    def __init__(self, base_url: str = API_V1):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        
    def login(self, username: str, password: str) -> bool:
        """Аутентификация и получение JWT токена"""
        print(f"\n🔐 Логинимся как '{username}'...")
        
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"✅ Успешная аутентификация!")
            print(f"   Роль: {data['user']['role']}")
            return True
        else:
            print(f"❌ Ошибка аутентификации: {response.status_code}")
            print(f"   {response.text}")
            return False
    
    def get_emulators(self, skip: int = 0, limit: int = 10, 
                      status: str = None, workstation_id: str = None) -> Dict[str, Any]:
        """Получить список эмуляторов с фильтрацией и пейджингом"""
        print(f"\n📱 Запрашиваем эмуляторы (skip={skip}, limit={limit})...")
        
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        if workstation_id:
            params["workstation_id"] = workstation_id
        
        response = requests.get(
            f"{self.base_url}/emulators",
            headers=self.headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Ошибка получения эмуляторов: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    def get_workstations(self) -> Dict[str, Any]:
        """Получить список рабочих станций"""
        print(f"\n🖥️  Запрашиваем рабочие станции...")
        
        response = requests.get(
            f"{self.base_url}/workstations",
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Ошибка получения станций: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    def get_health(self) -> Dict[str, Any]:
        """Проверить здоровье сервера"""
        print(f"\n💚 Проверяем здоровье сервера...")
        
        response = requests.get(f"{self.base_url}/health")
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Ошибка здоровья: {response.status_code}")
            return None


def print_section(title: str):
    """Печать красивого заголовка секции"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def main():
    """Главная демонстрация"""
    
    print_section("🚀 LDPlayer Management System - API Demo")
    print(f"📍 API URL: {API_V1}")
    
    # Инициализируем клиент
    client = LDPlayerAPIClient()
    
    # 1. Проверяем здоровье сервера
    print_section("1️⃣  ПРОВЕРКА ЗДОРОВЬЯ СЕРВЕРА")
    health = client.get_health()
    if health:
        print(f"✅ Статус: {health.get('status', 'unknown')}")
        print(f"   Версия: {health.get('version', 'unknown')}")
        print(f"   Uptime: {health.get('uptime', 'unknown')}")
        print(f"   Database: {health.get('database_status', 'unknown')}")
    
    # 2. Аутентификация
    print_section("2️⃣  АУТЕНТИФИКАЦИЯ")
    if not client.login(DEFAULT_USER, DEFAULT_PASS):
        print("❌ Не удалось залогиниться. Выход.")
        return
    
    # 3. Получаем рабочие станции
    print_section("3️⃣  РАБОЧИЕ СТАНЦИИ")
    ws_data = client.get_workstations()
    if ws_data and "data" in ws_data:
        workstations = ws_data["data"]
        print(f"📊 Всего рабочих станций: {len(workstations)}")
        for ws in workstations:
            status_emoji = "🟢" if ws.get("status") == "online" else "🔴"
            print(f"\n  {status_emoji} {ws.get('name')} (ID: {ws.get('id')})")
            print(f"     IP: {ws.get('ip_address')}")
            print(f"     Статус: {ws.get('status')}")
            print(f"     LDPlayer путь: {ws.get('ldplayer_path')}")
    
    # 4. Получаем эмуляторы (все)
    print_section("4️⃣  ВСЕ ЭМУЛЯТОРЫ (без фильтра)")
    emul_data = client.get_emulators(limit=100)
    if emul_data and "data" in emul_data:
        emulators = emul_data["data"]
        pagination = emul_data.get("pagination", {})
        
        print(f"📊 Всего эмуляторов: {pagination.get('total', 'unknown')}")
        print(f"   На странице: {len(emulators)}")
        print(f"   Пейджинг: skip={pagination.get('skip')}, limit={pagination.get('limit')}")
        
        if emulators:
            for i, emul in enumerate(emulators, 1):
                status_emoji = "▶️ " if emul.get("status") == "running" else "⏹️ "
                print(f"\n  {i}. {status_emoji} {emul.get('name')} (ID: {emul.get('id')})")
                print(f"     Станция: {emul.get('workstation_id')}")
                print(f"     Статус: {emul.get('status')}")
                print(f"     Разрешение: {emul.get('resolution')}")
                print(f"     DPI: {emul.get('dpi')}")
        else:
            print("⚠️  Эмуляторы не найдены")
    
    # 5. Фильтрация эмуляторов по статусу
    print_section("5️⃣  ЭМУЛЯТОРЫ С ФИЛЬТРОМ (status=running)")
    running_data = client.get_emulators(status="running", limit=100)
    if running_data and "data" in running_data:
        running = running_data["data"]
        print(f"📊 Запущенных эмуляторов: {len(running)}")
        for emul in running:
            print(f"  ▶️  {emul.get('name')} - {emul.get('status')}")
    
    # 6. Пейджинг демонстрация
    print_section("6️⃣  ДЕМОНСТРАЦИЯ ПЕЙДЖИНГА")
    print("📄 Страница 1 (skip=0, limit=2):")
    page1 = client.get_emulators(skip=0, limit=2)
    if page1 and "data" in page1:
        for emul in page1["data"]:
            print(f"  • {emul.get('name')}")
        print(f"  Есть ещё страницы: {page1.get('pagination', {}).get('has_more')}")
    
    print("\n📄 Страница 2 (skip=2, limit=2):")
    page2 = client.get_emulators(skip=2, limit=2)
    if page2 and "data" in page2:
        for emul in page2["data"]:
            print(f"  • {emul.get('name')}")
    
    # 7. API Response Format
    print_section("7️⃣  ФОРМАТ API ОТВЕТА")
    print("✅ Unified API Response Model:")
    print(json.dumps({
        "success": True,
        "message": "Emulators retrieved successfully",
        "data": [
            {
                "id": "emul_001",
                "name": "Android 11",
                "workstation_id": "ws_001",
                "status": "running",
                "resolution": "720x1280",
                "dpi": 300,
                "cpu_cores": 2,
                "ram_mb": 2048
            }
        ],
        "pagination": {
            "skip": 0,
            "limit": 10,
            "total": 5,
            "has_more": False
        },
        "timestamp": "2025-10-19T18:52:26.758953"
    }, indent=2, ensure_ascii=False))
    
    print_section("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("📚 Документация доступна на: http://localhost:8000/docs")
    print("🔄 OpenAPI Schema: http://localhost:8000/openapi.json")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
