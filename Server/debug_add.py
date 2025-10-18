#!/usr/bin/env python3
"""
Отладка команды add.
"""

import subprocess

ldconsole = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"

print("🔍 ОТЛАДКА КОМАНДЫ ADD")
print("=" * 70)

# Получить количество до
result_before = subprocess.run(
    [ldconsole, "list2"],
    capture_output=True,
    text=True,
    timeout=30
)

count_before = len([l for l in result_before.stdout.split('\n') if ',' in l])
print(f"Эмуляторов до: {count_before}\n")

# Выполнить add
print("Выполняется: ldconsole add\n")

result = subprocess.run(
    [ldconsole, "add"],
    capture_output=True,
    text=True,
    timeout=120
)

print(f"Код возврата: {result.returncode}")
print(f"STDOUT: '{result.stdout}'")
print(f"STDERR: '{result.stderr}'")

# Проверить количество после
import time
time.sleep(2)

result_after = subprocess.run(
    [ldconsole, "list2"],
    capture_output=True,
    text=True,
    timeout=30
)

lines_after = [l for l in result_after.stdout.split('\n') if ',' in l]
count_after = len(lines_after)

print(f"\nЭмуляторов после: {count_after}")

if count_after > count_before:
    print(f"\n✅ Создано эмуляторов: {count_after - count_before}")
    print(f"\nПоследний эмулятор:")
    if lines_after:
        last = lines_after[-1]
        parts = last.split(',')
        print(f"   Индекс: {parts[0]}")
        print(f"   Имя: {parts[1]}")
        print(f"   Полная строка: {last}")
else:
    print(f"\n❌ Новые эмуляторы не созданы")

# Коды возврата ldconsole
print(f"\n📖 Информация о кодах возврата:")
print(f"   0 - успех")
print(f"   7 - код возврата при успешном создании через 'add'")
print(f"   Другие коды - ошибки")
