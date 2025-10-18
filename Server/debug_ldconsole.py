#!/usr/bin/env python3
"""
Отладка выполнения ldconsole команд.
"""

import subprocess
import sys
from pathlib import Path

def debug_ldconsole():
    """Отладка ldconsole."""
    print("🔍 ОТЛАДКА LDCONSOLE")
    print("=" * 60)
    
    ldconsole_path = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"
    
    print(f"\n📍 Путь: {ldconsole_path}")
    print(f"   Существует: {Path(ldconsole_path).exists()}")
    
    # Тест 1: Прямой вызов
    print("\n" + "=" * 60)
    print("ТЕСТ 1: Прямой вызов subprocess.run")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [ldconsole_path, "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\nКод возврата: {result.returncode}")
        print(f"\nSTDOUT ({len(result.stdout)} символов):")
        print(f"'{result.stdout}'")
        print(f"\nSTDERR ({len(result.stderr)} символов):")
        print(f"'{result.stderr}'")
        
        # Разбор построчно
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            print(f"\n📋 Строк в выводе: {len(lines)}")
            for i, line in enumerate(lines, 1):
                print(f"   {i}. '{line}' (длина: {len(line)})")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    # Тест 2: Через метод WorkstationManager
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Через WorkstationManager._parse_emulators_list")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.remote.workstation import WorkstationManager
        
        # Получаем вывод
        result = subprocess.run(
            [ldconsole_path, "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        print(f"\nИсходный вывод: '{output}'")
        
        # Используем метод парсинга (статический)
        class DummyManager:
            """Заглушка для доступа к статическому методу."""
            @staticmethod
            def _parse_emulators_list(output_text):
                return WorkstationManager._parse_emulators_list(None, output_text)
        
        emulators = DummyManager._parse_emulators_list(output)
        
        print(f"\n✅ Распознано эмуляторов: {len(emulators)}")
        for emu in emulators:
            print(f"   - {emu}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 3: Проверка через метод run_command
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Через подмененный run_command")
    print("=" * 60)
    
    try:
        def local_run_command(command, args=None):
            """Локальное выполнение команды."""
            args = args or []
            print(f"\n   Выполняется: {command} {' '.join(args)}")
            
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print(f"   Код возврата: {result.returncode}")
            print(f"   STDOUT: '{result.stdout}'")
            print(f"   STDERR: '{result.stderr}'")
            
            return result.returncode, result.stdout, result.stderr
        
        exitcode, stdout, stderr = local_run_command(ldconsole_path, ["list"])
        
        print(f"\n📊 Результат:")
        print(f"   exitcode: {exitcode}")
        print(f"   stdout длина: {len(stdout)}")
        print(f"   stderr длина: {len(stderr)}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        debug_ldconsole()
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
