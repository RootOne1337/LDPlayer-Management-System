#!/usr/bin/env python3
"""
Улучшенный парсинг эмуляторов через ldconsole list2.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any

def parse_ldconsole_list2(ldplayer_path: str = r"C:\LDPlayer\LDPlayer9") -> List[Dict[str, Any]]:
    """Распарсить вывод ldconsole list2.
    
    Args:
        ldplayer_path: Путь к LDPlayer
        
    Returns:
        Список словарей с информацией об эмуляторах
    """
    print("🔍 ПАРСИНГ LDCONSOLE LIST2")
    print("=" * 70)
    
    ldconsole = Path(ldplayer_path) / "ldconsole.exe"
    
    if not ldconsole.exists():
        print(f"❌ ldconsole не найден: {ldconsole}")
        return []
    
    print(f"✅ ldconsole: {ldconsole}\n")
    
    # Выполнить list2
    try:
        result = subprocess.run(
            [str(ldconsole), "list2"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Команда вернула код {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return []
        
        output = result.stdout.strip()
        print(f"📋 Вывод ldconsole list2:")
        print(f"{output}\n")
        
        # Парсинг
        emulators = []
        lines = output.split('\n')
        
        print(f"🔬 Анализ строк:")
        print("-" * 70)
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            print(f"\nСтрока {i}: '{line}'")
            
            # Формат: index,name,topWindowHandle,vBoxWindowHandle,binderWindowHandle,width,height,dpi,vBoxHeadless,vBoxVmSrvPid
            # Пример: 0,LDPlayer,0,0,0,-1,-1,960,540,160
            parts = line.split(',')
            
            if len(parts) >= 10:
                try:
                    emulator = {
                        'index': int(parts[0]),
                        'name': parts[1],
                        'top_window_handle': int(parts[2]),
                        'vbox_window_handle': int(parts[3]),
                        'binder_window_handle': int(parts[4]),
                        'width': int(parts[5]),
                        'height': int(parts[6]),
                        'resolution_width': int(parts[7]),
                        'resolution_height': int(parts[8]),
                        'dpi': int(parts[9])
                    }
                    
                    emulators.append(emulator)
                    
                    print(f"   ✅ Распознан эмулятор:")
                    print(f"      Индекс: {emulator['index']}")
                    print(f"      Имя: {emulator['name']}")
                    print(f"      Разрешение: {emulator['resolution_width']}x{emulator['resolution_height']}")
                    print(f"      DPI: {emulator['dpi']}")
                    
                    # Проверить, запущен ли
                    is_running = (
                        emulator['top_window_handle'] != 0 or
                        emulator['vbox_window_handle'] != 0 or
                        emulator['binder_window_handle'] != 0
                    )
                    emulator['is_running'] = is_running
                    print(f"      Статус: {'🟢 ЗАПУЩЕН' if is_running else '⚪ ОСТАНОВЛЕН'}")
                    
                except (ValueError, IndexError) as e:
                    print(f"   ⚠️ Ошибка парсинга: {e}")
            else:
                print(f"   ⚠️ Недостаточно полей ({len(parts)}), ожидается >= 10")
        
        print(f"\n{'=' * 70}")
        print(f"📊 ИТОГО: найдено {len(emulators)} эмуляторов")
        print(f"{'=' * 70}")
        
        return emulators
        
    except Exception as e:
        print(f"❌ Ошибка выполнения ldconsole: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_emulator_details(emulator_name: str, ldplayer_path: str = r"C:\LDPlayer\LDPlayer9") -> Dict[str, Any]:
    """Получить детальную информацию об эмуляторе.
    
    Args:
        emulator_name: Имя эмулятора
        ldplayer_path: Путь к LDPlayer
        
    Returns:
        Словарь с детальной информацией
    """
    ldconsole = Path(ldplayer_path) / "ldconsole.exe"
    
    details = {
        'name': emulator_name,
        'exists': False,
        'is_running': False,
        'properties': {}
    }
    
    try:
        # Проверить, существует ли
        result = subprocess.run(
            [str(ldconsole), "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if emulator_name in result.stdout:
            details['exists'] = True
        
        # Проверить статус
        result_status = subprocess.run(
            [str(ldconsole), "isrunning", "--name", emulator_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        details['is_running'] = (result_status.returncode == 0)
        
        # Получить свойства (если есть команда getprop)
        # Попробуем несколько команд
        prop_commands = [
            ["globalsetting", "--name", emulator_name],
            ["getprop", "--name", emulator_name],
        ]
        
        for cmd in prop_commands:
            try:
                result_prop = subprocess.run(
                    [str(ldconsole)] + cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result_prop.returncode == 0 and result_prop.stdout.strip():
                    details['properties'][' '.join(cmd)] = result_prop.stdout.strip()
            except:
                pass
        
    except Exception as e:
        print(f"Ошибка получения деталей для {emulator_name}: {e}")
    
    return details


if __name__ == "__main__":
    try:
        # Получить список через list2
        emulators = parse_ldconsole_list2()
        
        if emulators:
            print(f"\n{'=' * 70}")
            print("📋 СПИСОК ВСЕХ ЭМУЛЯТОРОВ")
            print(f"{'=' * 70}\n")
            
            for emu in emulators:
                print(f"{emu['index']}. {emu['name']}")
                print(f"   Разрешение: {emu['resolution_width']}x{emu['resolution_height']}")
                print(f"   DPI: {emu['dpi']}")
                print(f"   Статус: {'🟢 Запущен' if emu['is_running'] else '⚪ Остановлен'}")
                print()
            
            # Получить детали для каждого
            print(f"{'=' * 70}")
            print("🔍 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ")
            print(f"{'=' * 70}\n")
            
            for emu in emulators:
                details = get_emulator_details(emu['name'])
                
                print(f"📱 {emu['name']}")
                print(f"   Существует: {'✅' if details['exists'] else '❌'}")
                print(f"   Запущен: {'✅' if details['is_running'] else '❌'}")
                
                if details['properties']:
                    print(f"   Свойства:")
                    for key, value in details['properties'].items():
                        print(f"      {key}:")
                        for line in value.split('\n')[:5]:  # Первые 5 строк
                            print(f"         {line}")
                print()
        
        else:
            print("\n⚠️ Эмуляторы не найдены")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
