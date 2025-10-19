#!/usr/bin/env python3
"""Quick test - проверим что есть в app routes"""

from src.core.server import app

print("\n📋 Все зарегистрированные маршруты:\n")
print("-" * 80)

for route in app.routes:
    print(f"📍 {route.path:<50} {str(route.methods) if hasattr(route, 'methods') else 'NO METHODS'}")

print("-" * 80)
print(f"\n✅ Всего маршрутов: {len(app.routes)}\n")

# Ищем auth маршруты
print("\n🔐 Ищем auth маршруты:")
for route in app.routes:
    if 'auth' in route.path.lower() or 'login' in route.path.lower():
        print(f"   ✅ {route.path}")

print("\n🏥 Ищем health маршруты:")
for route in app.routes:
    if 'health' in route.path.lower():
        print(f"   ✅ {route.path}")

print("\n📱 Ищем emulator маршруты:")
for route in app.routes:
    if 'emulator' in route.path.lower():
        print(f"   ✅ {route.path}")
