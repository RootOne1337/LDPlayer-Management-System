#!/usr/bin/env python3
"""
Очистка эмуляторов: оставить только 0 и 1, переименовать 1 в nifilim.
"""

import subprocess
import time

ldconsole = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"

print("🧹 ОЧИСТКА ЭМУЛЯТОРОВ")
print("=" * 70)

# Получить список
print("\n📋 Получение списка эмуляторов...")
result = subprocess.run(
    [ldconsole, "list2"],
    capture_output=True,
    text=True,
    timeout=30
)

if result.returncode != 0:
    print(f"❌ Ошибка получения списка")
    exit(1)

# Парсинг
emulators = []
for line in result.stdout.strip().split('\n'):
    if ',' in line:
        parts = line.split(',')
        if len(parts) >= 2:
            emulators.append({
                'index': int(parts[0]),
                'name': parts[1]
            })

print(f"Найдено эмуляторов: {len(emulators)}\n")

for emu in emulators:
    print(f"   {emu['index']}. {emu['name']}")

# Удалить все, кроме 0 и 1
print(f"\n{'=' * 70}")
print("🗑️ УДАЛЕНИЕ ЛИШНИХ ЭМУЛЯТОРОВ")
print(f"{'=' * 70}\n")

keep_indices = {0, 1}
deleted_count = 0

for emu in emulators:
    if emu['index'] not in keep_indices:
        print(f"Удаление: {emu['index']}. {emu['name']}")
        
        result_remove = subprocess.run(
            [ldconsole, "remove", "--index", str(emu['index'])],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result_remove.returncode == 0:
            print(f"   ✅ Удален")
            deleted_count += 1
        else:
            print(f"   ⚠️ Код возврата: {result_remove.returncode}")
        
        time.sleep(0.5)  # Небольшая задержка

print(f"\n✅ Удалено эмуляторов: {deleted_count}")

# Переименовать эмулятор с индексом 1 в "nifilim"
print(f"\n{'=' * 70}")
print("✏️ ПЕРЕИМЕНОВАНИЕ ЭМУЛЯТОРА")
print(f"{'=' * 70}\n")

# Найти эмулятор с индексом 1
print("Переименование эмулятора с индексом 1 в 'nifilim'...")

result_rename = subprocess.run(
    [ldconsole, "rename", "--index", "1", "--title", "nifilim"],
    capture_output=True,
    text=True,
    timeout=30
)

if result_rename.returncode == 0:
    print("✅ Переименовано успешно")
else:
    print(f"⚠️ Код возврата: {result_rename.returncode}")
    print(f"STDERR: {result_rename.stderr}")

# Финальная проверка
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

final_emulators = []
for line in result_final.stdout.strip().split('\n'):
    if ',' in line:
        parts = line.split(',')
        if len(parts) >= 2:
            index = parts[0]
            name = parts[1]
            print(f"   {index}. {name}")
            final_emulators.append(name)

print(f"\n{'=' * 70}")
print("✅ ГОТОВО!")
print(f"{'=' * 70}")

if 'nifilim' in final_emulators:
    print("\n✅ Эмулятор 'nifilim' найден в списке!")
else:
    print("\n⚠️ Эмулятор 'nifilim' не найден")

print(f"\nВсего эмуляторов осталось: {len(final_emulators)}")
