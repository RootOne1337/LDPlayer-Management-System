#!/usr/bin/env python3
"""Live demo of LDPlayer Management System API with error handling"""

import requests
import json
import sys
import time

BASE = 'http://127.0.0.1:8000/api'

print('\n' + '='*70)
print('🚀  LDPlayer Management System - LIVE API Demo')
print('='*70)

# Step 1: Health Check
print('\n🏥 0. ПРОВЕРЯЕМ ЗДОРОВЬЕ СЕРВЕРА')
print('-'*70)

try:
    health = requests.get('http://127.0.0.1:8000/api/health', timeout=5)
    print(f'✅ Сервер доступен! Status: {health.status_code}')
    print(f'   Response: {health.json()}')
except Exception as e:
    print(f'❌ ОШИБКА: {e}')
    sys.exit(1)

# Step 2: Login
print('\n🔐 1. ПОЛУЧАЕМ JWT ТОКЕН')
print('-'*70)

try:
    login_response = requests.post(
        f'{BASE}/auth/login',
        json={'username': 'admin', 'password': 'admin'},
        timeout=5
    )
    
    print(f'📤 POST /api/auth/login')
    print(f'   Status: {login_response.status_code}')
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data['access_token']
        print('✅ Успешный логин!')
        print(f'   Токен: {token[:40]}...')
        print(f'   Тип: {token_data.get("token_type", "unknown")}')
        if 'user' in token_data:
            print(f'   Роль: {token_data["user"]["role"]}')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 3: Get Emulators
        print('\n📱 2. ПОЛУЧАЕМ СПИСОК ЭМУЛЯТОРОВ')
        print('-'*70)
        
        try:
            emul_response = requests.get(
                f'{BASE}/emulators?skip=0&limit=10',
                headers=headers,
                timeout=5
            )
            
            print(f'📥 GET /api/emulators')
            print(f'   Status: {emul_response.status_code}')
            
            if emul_response.status_code == 200:
                data = emul_response.json()
                print(f'✅ Ответ получен!')
                print(f'   Success: {data.get("success")}')
                print(f'   Message: {data.get("message")}')
                if 'pagination' in data:
                    print(f'   Всего эмуляторов: {data["pagination"].get("total", "?")}')
                    print(f'   На странице: {len(data.get("data", []))}')
                
                if data.get('data'):
                    print(f'\n   📋 Первые эмуляторы:\n')
                    for i, emul in enumerate(data['data'][:5], 1):
                        status_icon = '▶️ ' if emul.get('status') == 'running' else '⏹️ '
                        print(f'      {i}. {status_icon}{emul.get("name", "N/A")} (ID: {emul.get("id", "N/A")})')
                        print(f'         Станция: {emul.get("workstation_id", "N/A")}')
                        print(f'         Статус: {emul.get("status", "unknown")}')
                else:
                    print('   📭 Эмуляторов не найдено')
            else:
                print(f'❌ ОШИБКА: Status {emul_response.status_code}')
                print(f'   Response: {emul_response.text[:200]}')
                
        except Exception as e:
            print(f'❌ ОШИБКА при запросе эмуляторов: {e}')
        
        # Step 4: Get Workstations
        print('\n🖥️  3. ПОЛУЧАЕМ РАБОЧИЕ СТАНЦИИ')
        print('-'*70)
        
        try:
            ws_response = requests.get(
                f'{BASE}/workstations',
                headers=headers,
                timeout=5
            )
            
            print(f'📥 GET /api/workstations')
            print(f'   Status: {ws_response.status_code}')
            
            if ws_response.status_code == 200:
                ws_data = ws_response.json()
                print(f'✅ Ответ получен!')
                if ws_data.get('data'):
                    print(f'   Найдено станций: {len(ws_data["data"])}')
                    for i, ws in enumerate(ws_data['data'][:3], 1):
                        print(f'      {i}. {ws.get("name", "N/A")} (ID: {ws.get("id", "N/A")})')
                else:
                    print('   📭 Станций не найдено')
            else:
                print(f'❌ ОШИБКА: Status {ws_response.status_code}')
                
        except Exception as e:
            print(f'❌ ОШИБКА при запросе станций: {e}')
            
    else:
        print(f'❌ ОШИБКА ЛОГИНА: Status {login_response.status_code}')
        print(f'   Response: {login_response.text[:300]}')
        
except Exception as e:
    print(f'❌ КРИТИЧЕСКАЯ ОШИБКА: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '='*70)
print('✨ Demo завершена!')
print('='*70 + '\n')
