#!/usr/bin/env python3
"""
Восстановление: создать эмулятор с именем nifilim.
"""

import subprocess
import time

ldconsole = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"

print("🔧 ВОССТАНОВЛЕНИЕ ЭМУЛЯТОРА")
print("=" * 70)

# Текущий список
result = subprocess.run(
    [ldconsole, "list2"],
    capture_output=True,
    text=True,
    timeout=30
)

print("\n📋 Текущие эмуляторы:")
for line in result.stdout.strip().split('\n'):
    if ',' in line:
        parts = line.split(',')
        print(f"   {parts[0]}. {parts[1]}")

# Проверить, есть ли уже nifilim
if 'nifilim' in result.stdout:
    print("\n✅ Эмулятор 'nifilim' уже существует!")
else:
    print("\n🚀 Создание эмулятора...")
    
    # Создать новый
    result_add = subprocess.run(
        [ldconsole, "add"],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    print(f"   Создан с кодом: {result_add.returncode}")
    
    time.sleep(2)
    
    # Получить список снова
    result_list = subprocess.run(
        [ldconsole, "list2"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    lines = [l for l in result_list.stdout.strip().split('\n') if ',' in l]
    if lines:
        last_line = lines[-1]
        parts = last_line.split(',')
        created_name = parts[1]
        
        print(f"   Создан: {created_name}")
        
        # Переименовать
        if created_name != "nifilim":
            print(f"   Переименование в 'nifilim'...")
            
            result_rename = subprocess.run(
                [ldconsole, "rename", "--name", created_name, "--title", "nifilim"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_rename.returncode == 0:
                print(f"   ✅ Переименовано")
            else:
                print(f"   ⚠️ Ошибка переименования: {result_rename.returncode}")

# Финальный список
print(f"\n{'=' * 70}")
print("📋 ФИНАЛЬНЫЙ СПИСОК")
print(f"{'=' * 70}\n")

time.sleep(1)

result_final = subprocess.run(
    [ldconsole, "list2"],
    capture_output=True,
    text=True,
    timeout=30
)

for line in result_final.stdout.strip().split('\n'):
    if ',' in line:
        parts = line.split(',')
        marker = "✨" if parts[1] == "nifilim" else ""
        print(f"   {parts[0]}. {parts[1]} {marker}")

print(f"\n✅ ГОТОВО!")
