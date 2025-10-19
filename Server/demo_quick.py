#!/usr/bin/env python3
"""Quick demo of LDPlayer Management System API"""

import requests
import json

BASE = 'http://127.0.0.1:8000/api/v1'

print('\n' + '='*70)
print('🚀  LDPlayer Management System - API Demo')
print('='*70)

# Step 1: Login
print('\n🔐 1. ПОЛУЧАЕМ JWT ТОКЕН')
print('-'*70)

login_response = requests.post(f'{BASE}/auth/login', json={
    'username': 'admin',
    'password': 'admin'
})

if login_response.status_code == 200:
    token_data = login_response.json()
    token = token_data['access_token']
    print('✅ Успешный логин!')
    print(f'   Токен: {token[:50]}...')
    print(f'   Роль: {token_data["user"]["role"]}')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 2: Get Emulators
    print('\n📱 2. ПОЛУЧАЕМ СПИСОК ЭМУЛЯТОРОВ')
    print('-'*70)
    
    emul_response = requests.get(f'{BASE}/emulators?skip=0&limit=100', headers=headers)
    
    if emul_response.status_code == 200:
        data = emul_response.json()
        print(f'✅ Ответ получен!')
        print(f'   Success: {data["success"]}')
        print(f'   Message: {data["message"]}')
        print(f'   Всего эмуляторов: {data["pagination"]["total"]}')
        print(f'   На странице: {len(data["data"])}')
        
        if data['data']:
            print(f'\n   📋 Первые эмуляторы (всего {len(data["data"])}):\n')
            for i, emul in enumerate(data['data'], 1):
                status_icon = '▶️ ' if emul['status'] == 'running' else '⏹️ '
                print(f'      {i}. {status_icon}{emul["name"]} (ID: {emul["id"]})')
                print(f'         Станция: {emul["workstation_id"]}')
                print(f'         Статус: {emul["status"]}')
                print(f'         Разрешение: {emul["resolution"]} | DPI: {emul["dpi"]}')
                print(f'         CPU: {emul["cpu_cores"]} cores | RAM: {emul["ram_mb"]}MB')
        else:
            print('\n   ⚠️  Эмуляторы не найдены')
    else:
        print(f'❌ Ошибка: {emul_response.status_code}')
        print(f'   {emul_response.text}')

    # Step 3: Get Workstations
    print('\n\n🖥️  3. ПОЛУЧАЕМ РАБОЧИЕ СТАНЦИИ')
    print('-'*70)
    
    ws_response = requests.get(f'{BASE}/workstations', headers=headers)
    
    if ws_response.status_code == 200:
        data = ws_response.json()
        print(f'✅ Ответ получен!')
        print(f'   Всего станций: {len(data["data"])}')
        
        if data['data']:
            print(f'\n   🖥️  Рабочие станции:\n')
            for i, ws in enumerate(data['data'], 1):
                status_icon = '🟢' if ws['status'] == 'online' else '🔴'
                print(f'      {i}. {status_icon} {ws["name"]} (ID: {ws["id"]})')
                print(f'         IP: {ws["ip_address"]}')
                print(f'         Статус: {ws["status"]}')
                print(f'         LDPlayer: {ws["ldplayer_path"]}')
        else:
            print('\n   ⚠️  Станции не найдены')
    else:
        print(f'❌ Ошибка: {ws_response.status_code}')

    # Step 4: Health Check
    print('\n\n💚 4. ПРОВЕРЯЕМ ЗДОРОВЬЕ СЕРВЕРА')
    print('-'*70)
    
    health_response = requests.get('http://127.0.0.1:8000/api/v1/health')
    
    if health_response.status_code == 200:
        health = health_response.json()
        print(f'✅ Статус: {health.get("status", "ok")}')
        print(f'   Версия: {health.get("version", "1.0.0")}')
        print(f'   Uptime: {health.get("uptime", "0:00:00")}')
        print(f'   Database: {health.get("database_status", "ok")}')
        print(f'   Рабочих станций: {health.get("workstations_count", "?")}')
        print(f'   Эмуляторов: {health.get("emulators_count", "?")}')
    else:
        print(f'❌ Ошибка: {health_response.status_code}')

    # Step 5: API Response Model
    print('\n\n📋 5. ФОРМАТ API ОТВЕТА (Unified Response Model)')
    print('-'*70)
    print('''
    {
      "success": true,
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
          "ram_mb": 2048,
          "rom_gb": 10,
          "created_at": "2025-10-19T18:52:26.758953",
          "last_used": "2025-10-19T18:52:26.758953"
        }
      ],
      "pagination": {
        "skip": 0,
        "limit": 10,
        "total": 5,
        "has_more": false,
        "page": 1
      },
      "timestamp": "2025-10-19T18:52:26.758953"
    }
    ''')

else:
    print(f'❌ Ошибка логина: {login_response.status_code}')
    print(f'   {login_response.text}')

print('\n' + '='*70)
print('✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА')
print('='*70)
print('\n📚 Документация доступна на: http://localhost:8000/docs')
print('🔄 OpenAPI Schema: http://localhost:8000/openapi.json\n')
