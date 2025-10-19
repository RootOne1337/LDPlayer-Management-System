#!/usr/bin/env python3
"""Полная демонстрация LDPlayer Management System API"""

import requests
import json
import time

BASE = 'http://localhost:8000/api'

print('\n' + '='*80)
print('🎯 LDPlayer Management System - ПОЛНАЯ ДЕМОНСТРАЦИЯ')
print('='*80)

# Попробуем несколько раз в случае если сервер ещё не полностью готов
MAX_RETRIES = 5
for attempt in range(MAX_RETRIES):
    try:
        print(f'\n[{attempt+1}/{MAX_RETRIES}] Ждём сервер...')
        health = requests.get(f'{BASE}/health', timeout=2)
        if health.status_code == 200:
            print('✅ Сервер доступен!')
            break
    except:
        if attempt < MAX_RETRIES - 1:
            print(f'   ⏳ Сервер не готов, жду 2 сек...')
            time.sleep(2)
        else:
            print('❌ Сервер не запустился!')
            exit(1)

# ==================================================================
# 1. ЛОГИРОВАНИЕ
# ==================================================================
print('\n' + '─'*80)
print('1️⃣  ЛОГИРОВАНИЕ (JWT)')
print('─'*80)

try:
    login_resp = requests.post(
        f'{BASE}/auth/login',
        json={'username': 'admin', 'password': 'admin'},
        timeout=5
    )
    
    if login_resp.status_code == 200:
        token_data = login_resp.json()
        token = token_data.get('access_token', '')
        print(f'✅ Логин успешный!')
        print(f'   Token: {token[:30]}...')
        print(f'   Type: {token_data.get("token_type", "Bearer")}')
        print(f'   User: {token_data.get("user", {}).get("username", "?")}')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # ==================================================================
        # 2. ПРОВЕРКА ЗДОРОВЬЯ
        # ==================================================================
        print('\n' + '─'*80)
        print('2️⃣  ЗДОРОВЬЕ СИСТЕМЫ')
        print('─'*80)
        
        health_resp = requests.get(f'{BASE}/health', headers=headers, timeout=5)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            print(f'✅ Система здорова!')
            print(f'   Status: {health_data.get("data", {}).get("status", "?")}')
        
        # ==================================================================
        # 3. ЭМУЛЯТОРЫ
        # ==================================================================
        print('\n' + '─'*80)
        print('3️⃣  ЭМУЛЯТОРЫ')
        print('─'*80)
        
        emul_resp = requests.get(
            f'{BASE}/emulators?skip=0&limit=100',
            headers=headers,
            timeout=5
        )
        
        if emul_resp.status_code == 200:
            emul_data = emul_resp.json()
            total = emul_data.get('pagination', {}).get('total', 0)
            print(f'✅ Получены данные эмуляторов!')
            print(f'   Всего: {total}')
            print(f'   На странице: {len(emul_data.get("data", []))}')
            
            if emul_data.get('data'):
                print(f'\n   📱 Список эмуляторов:\n')
                for i, emul in enumerate(emul_data['data'][:5], 1):
                    status = emul.get('status', '?')
                    icon = '▶️ ' if status == 'running' else '⏸️ '
                    print(f'      {i}. {icon}{emul.get("name", "?")}')
                    print(f'         ID: {emul.get("id", "?")}')
                    print(f'         Станция: {emul.get("workstation_id", "?")}')
                    print(f'         Статус: {status}')
        
        # ==================================================================
        # 4. РАБОЧИЕ СТАНЦИИ
        # ==================================================================
        print('\n' + '─'*80)
        print('4️⃣  РАБОЧИЕ СТАНЦИИ')
        print('─'*80)
        
        ws_resp = requests.get(
            f'{BASE}/workstations',
            headers=headers,
            timeout=5
        )
        
        if ws_resp.status_code == 200:
            ws_data = ws_resp.json()
            ws_list = ws_data.get('data', [])
            print(f'✅ Получены данные рабочих станций!')
            print(f'   Всего: {len(ws_list)}')
            
            if ws_list:
                print(f'\n   🖥️  Список станций:\n')
                for i, ws in enumerate(ws_list[:5], 1):
                    print(f'      {i}. {ws.get("name", "?")}')
                    print(f'         ID: {ws.get("id", "?")}')
                    print(f'         Host: {ws.get("host", "?")}')
    else:
        print(f'❌ Ошибка логина: {login_resp.status_code}')
        print(f'   {login_resp.text[:200]}')
        
except Exception as e:
    print(f'❌ Ошибка: {e}')

print('\n' + '='*80)
print('✨ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА')
print('='*80 + '\n')
