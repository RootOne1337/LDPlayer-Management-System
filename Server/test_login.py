#!/usr/bin/env python3
"""Simple test - login only"""

import requests
import sys

BASE = 'http://localhost:8000/api'

print('🔐 Trying to login...\n')

try:
    response = requests.post(
        f'{BASE}/auth/login',
        json={'username': 'admin', 'password': 'admin'},
        timeout=5
    )
    print(f'Status: {response.status_code}')
    print(f'Response: {response.json()}')
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
