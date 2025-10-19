#!/usr/bin/env python3
"""Тест API используя FastAPI TestClient - не требует запущенного сервера"""

from fastapi.testclient import TestClient
from src.core.server import app

client = TestClient(app)

print('\n' + '='*80)
print('🎯 LDPlayer Management System - API TESTING')
print('='*80)

# 1. Health check
print('\n1. HEALTH CHECK')
print('─'*80)
response = client.get('/api/health')
print(f'GET /api/health')
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')

# 2. Login
print('\n2. ЛОГИРОВАНИЕ')
print('─'*80)
response = client.post('/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
print(f'POST /api/auth/login')
print(f'Status: {response.status_code}')
data = response.json()
print(f'Response: {data}')

if response.status_code == 200:
    token = data.get('access_token', '')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 3. Get emulators
    print('\n3. ЭМУЛЯТОРЫ')
    print('─'*80)
    response = client.post('/api/emulators', json={}, headers=headers)  # POST instead of GET
    print(f'POST /api/emulators')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Response: {data}')
    
    # 4. Get workstations
    print('\n4. РАБОЧИЕ СТАНЦИИ')
    print('─'*80)
    response = client.get('/api/workstations', headers=headers)
    print(f'GET /api/workstations')
    print(f'Status: {response.status_code}')
    data = response.json()
    
    ws_list = data if isinstance(data, list) else data.get('data', [])
    print(f'Total: {len(ws_list)}')
    
    if ws_list:
        print('\n   🖥️  Stations:')
        for i, ws in enumerate(ws_list[:3], 1):
            print(f'      {i}. {ws.get("name")} ({ws.get("host")})')

print('\n' + '='*80)
print('✨ TEST COMPLETED')
print('='*80 + '\n')
