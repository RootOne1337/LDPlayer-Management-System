#!/usr/bin/env python3
"""
Тест всех вариантов создания эмулятора.
"""

import subprocess
import time

ldconsole = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"

def test_command(name, args):
    """Тест одной команды."""
    print(f"\n{'=' * 70}")
    print(f"Тест: {name}")
    print(f"Команда: {' '.join([ldconsole] + args)}")
    print(f"{'=' * 70}")
    
    result = subprocess.run(
        [ldconsole] + args,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    print(f"Код возврата: {result.returncode}")
    if result.stdout.strip():
        print(f"STDOUT:\n{result.stdout[:500]}")
    if result.stderr.strip():
        print(f"STDERR:\n{result.stderr[:500]}")
    
    return result.returncode == 0

print("🔧 ТЕСТ СОЗДАНИЯ ЭМУЛЯТОРОВ")
print("=" * 70)

# Получить список существующих
result_list = subprocess.run(
    [ldconsole, "list"],
    capture_output=True,
    text=True,
    timeout=30
)

existing = [line.strip() for line in result_list.stdout.split('\n') if line.strip()]
print(f"\n📋 Существующие эмуляторы:")
for emu in existing[1:]:  # Пропустить заголовок
    print(f"   - {emu}")

# Тест 1: add без параметров
test_command(
    "1. add без параметров",
    ["add"]
)

time.sleep(2)

# Проверить, что создалось
result_list2 = subprocess.run(
    [ldconsole, "list"],
    capture_output=True,
    text=True,
    timeout=30
)

new_emulators = [line.strip() for line in result_list2.stdout.split('\n') if line.strip()]
difference = set(new_emulators) - set(existing)

if difference:
    print(f"\n✅ Создан эмулятор: {difference}")
    created_name = list(difference)[0]
    
    # Попробуем переименовать
    test_command(
        "2. rename созданного эмулятора в br230",
        ["rename", "--name", created_name, "--title", "br230"]
    )
    
else:
    print(f"\n⚠️ Новые эмуляторы не обнаружены")
    
    # Тест 3: add с именем
    test_command(
        "3. add --name br231",
        ["add", "--name", "br231"]
    )

# Финальная проверка
print(f"\n{'=' * 70}")
print(f"ФИНАЛЬНЫЙ СПИСОК")
print(f"{'=' * 70}")

result_final = subprocess.run(
    [ldconsole, "list2"],
    capture_output=True,
    text=True,
    timeout=30
)

print(result_final.stdout)
