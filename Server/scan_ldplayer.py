#!/usr/bin/env python3
"""
Тест поиска эмуляторов LDPlayer.
Проверяет локальную установку LDPlayer и список эмуляторов.
"""

import os
import subprocess
import sys
from pathlib import Path

# Возможные пути установки LDPlayer
LDPLAYER_PATHS = [
    r"C:\LDPlayer\LDPlayer9.0",
    r"C:\LDPlayer\LDPlayer9",
    r"C:\LDPlayer\LDPlayer4.0",
    r"C:\LDPlayer\LDPlayer4",
    r"C:\LDPlayer",
    r"D:\LDPlayer\LDPlayer9.0",
    r"D:\LDPlayer\LDPlayer9",
    r"C:\Program Files\LDPlayer",
    r"C:\Program Files (x86)\LDPlayer",
]

def find_ldplayer():
    """Найти установку LDPlayer на локальной машине."""
    print("🔍 ПОИСК УСТАНОВКИ LDPLAYER")
    print("=" * 60)
    
    found_paths = []
    
    for path in LDPLAYER_PATHS:
        ldplayer_dir = Path(path)
        if ldplayer_dir.exists():
            print(f"✅ Найдена директория: {path}")
            
            # Проверить наличие ldconsole.exe
            ldconsole = ldplayer_dir / "ldconsole.exe"
            if ldconsole.exists():
                print(f"   ✅ ldconsole.exe найден")
                found_paths.append((ldplayer_dir, ldconsole))
            else:
                print(f"   ⚠️ ldconsole.exe не найден")
        else:
            print(f"❌ Не найдена: {path}")
    
    return found_paths


def test_ldconsole(ldconsole_path):
    """Протестировать ldconsole.exe."""
    print(f"\n📡 ТЕСТИРОВАНИЕ LDCONSOLE")
    print("=" * 60)
    print(f"Путь: {ldconsole_path}")
    
    try:
        # Попробовать выполнить команду list
        result = subprocess.run(
            [str(ldconsole_path), "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"\nВыход команды (код: {result.returncode}):")
        print("-" * 60)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        # Попробовать распарсить вывод
        if result.returncode == 0 and result.stdout:
            print("\n📊 ПАРСИНГ РЕЗУЛЬТАТА:")
            print("-" * 60)
            
            lines = result.stdout.strip().split('\n')
            print(f"Всего строк: {len(lines)}")
            
            emulator_count = 0
            for i, line in enumerate(lines):
                if i == 0:
                    print(f"Заголовок: {line}")
                elif line.strip():
                    print(f"Эмулятор {emulator_count + 1}: {line}")
                    emulator_count += 1
            
            print(f"\n✅ Найдено эмуляторов: {emulator_count}")
            return emulator_count
        else:
            print("⚠️ Команда вернула ошибку или пустой результат")
            return 0
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут выполнения команды (10 сек)")
        return 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 0


def test_ldconsole_version(ldconsole_path):
    """Получить версию LDPlayer."""
    print(f"\n📋 ВЕРСИЯ LDPLAYER")
    print("=" * 60)
    
    try:
        # Попробовать получить версию
        result = subprocess.run(
            [str(ldconsole_path), "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.stdout:
            print(f"Версия: {result.stdout.strip()}")
        else:
            print("⚠️ Не удалось получить версию")
            
    except Exception as e:
        print(f"⚠️ Ошибка получения версии: {e}")


def test_running_emulators(ldconsole_path):
    """Проверить запущенные эмуляторы."""
    print(f"\n🚀 ЗАПУЩЕННЫЕ ЭМУЛЯТОРЫ")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [str(ldconsole_path), "runninglist"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            running_count = len([line for line in lines[1:] if line.strip()])
            print(f"✅ Запущено эмуляторов: {running_count}")
            
            if running_count > 0:
                print("\nСписок:")
                for line in lines[1:]:
                    if line.strip():
                        print(f"  - {line}")
        else:
            print("⚠️ Нет запущенных эмуляторов")
            
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")


def main():
    """Главная функция."""
    print("🎮 LDPlayer Emulator Scanner")
    print("=" * 60)
    print()
    
    # Найти LDPlayer
    found_installations = find_ldplayer()
    
    if not found_installations:
        print("\n" + "=" * 60)
        print("❌ LDPlayer НЕ НАЙДЕН на этой машине")
        print("=" * 60)
        print("\nВозможные причины:")
        print("1. LDPlayer не установлен")
        print("2. Установлен в другую директорию")
        print("3. Используется другая версия")
        print("\nДля работы системы нужно:")
        print("- Установить LDPlayer 9 или указать путь в config.json")
        print("- Или использовать удаленное подключение к станциям с LDPlayer")
        return
    
    print("\n" + "=" * 60)
    print(f"✅ Найдено установок LDPlayer: {len(found_installations)}")
    print("=" * 60)
    
    # Тестировать каждую найденную установку
    for ldplayer_dir, ldconsole_path in found_installations:
        print(f"\n\n🔧 ТЕСТИРОВАНИЕ: {ldplayer_dir}")
        print("=" * 60)
        
        # Версия
        test_ldconsole_version(ldconsole_path)
        
        # Список эмуляторов
        emulator_count = test_ldconsole(ldconsole_path)
        
        # Запущенные эмуляторы
        test_running_emulators(ldconsole_path)
        
        if emulator_count > 0:
            print("\n" + "=" * 60)
            print("✅ ЭМУЛЯТОРЫ НАЙДЕНЫ! Система может работать с ними!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ Эмуляторы не найдены. Создайте их через LDPlayer или ldconsole")
            print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
