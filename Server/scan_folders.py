#!/usr/bin/env python3
"""
Детальное сканирование папок LDPlayer для обнаружения всех эмуляторов.
Анализирует файловую систему, а не только вывод ldconsole.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

def scan_ldplayer_folders(ldplayer_path: str = r"C:\LDPlayer\LDPlayer9") -> Dict[str, Any]:
    """Сканировать папки LDPlayer для обнаружения эмуляторов.
    
    Args:
        ldplayer_path: Путь к установке LDPlayer
        
    Returns:
        Словарь с информацией об эмуляторах
    """
    print("🔍 ДЕТАЛЬНОЕ СКАНИРОВАНИЕ ПАПОК LDPLAYER")
    print("=" * 70)
    
    result = {
        "ldplayer_path": ldplayer_path,
        "exists": False,
        "vms_folder": None,
        "emulators": [],
        "config_files": []
    }
    
    ldpath = Path(ldplayer_path)
    
    if not ldpath.exists():
        print(f"❌ Путь не существует: {ldplayer_path}")
        return result
    
    result["exists"] = True
    print(f"✅ Путь существует: {ldplayer_path}\n")
    
    # 1. Поиск папки с виртуальными машинами
    print("📁 ШАГ 1: Поиск папки с эмуляторами")
    print("-" * 70)
    
    possible_vm_folders = ["vms", "VirtualBox VMs", "VMs"]
    vms_path = None
    
    for folder in possible_vm_folders:
        test_path = ldpath / folder
        if test_path.exists():
            vms_path = test_path
            result["vms_folder"] = str(test_path)
            print(f"✅ Найдена папка VMs: {test_path}")
            break
    
    if not vms_path:
        # Поиск в родительской директории
        parent = ldpath.parent
        for folder in possible_vm_folders:
            test_path = parent / folder
            if test_path.exists():
                vms_path = test_path
                result["vms_folder"] = str(test_path)
                print(f"✅ Найдена папка VMs (в родительской): {test_path}")
                break
    
    if not vms_path:
        print("⚠️ Папка с VMs не найдена, ищем по другим признакам...")
    
    # 2. Поиск папки конфигураций
    print("\n📁 ШАГ 2: Поиск папки конфигураций")
    print("-" * 70)
    
    config_folders = []
    
    # 2.1 Стандартная папка configs
    configs_path = ldpath / "vms" / "config"
    if configs_path.exists():
        config_folders.append(configs_path)
        print(f"✅ Найдена папка configs: {configs_path}")
    
    # 2.2 Альтернативная папка leidian
    leidian_path = ldpath / "vms" / "leidian"
    if leidian_path.exists():
        config_folders.append(leidian_path)
        print(f"✅ Найдена папка leidian: {leidian_path}")
    
    # 2.3 Прямо в vms
    vms_direct = ldpath / "vms"
    if vms_direct.exists():
        config_folders.append(vms_direct)
        print(f"✅ Проверим папку vms: {vms_direct}")
    
    if not config_folders:
        print("⚠️ Папки конфигураций не найдены")
    
    # 3. Сканирование конфигурационных файлов
    print("\n📄 ШАГ 3: Поиск конфигурационных файлов .config")
    print("-" * 70)
    
    config_files = []
    
    for config_folder in config_folders:
        if not config_folder.exists():
            continue
            
        print(f"\n   Сканирование: {config_folder}")
        
        # Поиск .config файлов
        for item in config_folder.rglob("*.config"):
            config_files.append(item)
            result["config_files"].append(str(item))
            print(f"      📄 Найден: {item.name}")
    
    print(f"\n   Всего .config файлов: {len(config_files)}")
    
    # 4. Анализ каждого конфига
    print("\n🔬 ШАГ 4: Анализ конфигурационных файлов")
    print("-" * 70)
    
    emulators = []
    
    for config_file in config_files:
        print(f"\n📋 Анализ: {config_file.name}")
        
        try:
            # Чтение конфига (может быть в разных форматах)
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            emulator_info = {
                "config_file": str(config_file),
                "name": None,
                "properties": {}
            }
            
            # Попытка распарсить как INI/properties
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    
                    emulator_info["properties"][key] = value
                    
                    # Ключевые поля
                    if key.lower() in ['statusSettings.playerName'.lower(), 'name', 'vmname']:
                        emulator_info["name"] = value
                        print(f"   ✅ Имя эмулятора: {value}")
                    
                    if key.lower() in ['resolution.width', 'width']:
                        print(f"   📐 Ширина: {value}")
                    
                    if key.lower() in ['resolution.height', 'height']:
                        print(f"   📐 Высота: {value}")
                    
                    if key.lower() in ['propertySettings.phoneMemory'.lower(), 'memory']:
                        print(f"   💾 Память: {value} MB")
                    
                    if key.lower() in ['propertySettings.phoneCPUCores'.lower(), 'cpucores']:
                        print(f"   🖥️ CPU ядер: {value}")
            
            # Если имя не найдено, используем имя файла
            if not emulator_info["name"]:
                emulator_info["name"] = config_file.stem
                print(f"   ℹ️ Имя из файла: {emulator_info['name']}")
            
            emulators.append(emulator_info)
            
        except Exception as e:
            print(f"   ❌ Ошибка чтения файла: {e}")
    
    result["emulators"] = emulators
    
    # 5. Проверка через ldconsole
    print("\n" + "=" * 70)
    print("🔧 ШАГ 5: Проверка через ldconsole.exe")
    print("=" * 70)
    
    ldconsole_path = ldpath / "ldconsole.exe"
    if ldconsole_path.exists():
        print(f"✅ ldconsole найден: {ldconsole_path}")
        
        try:
            import subprocess
            result_cmd = subprocess.run(
                [str(ldconsole_path), "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_cmd.returncode == 0:
                lines = result_cmd.stdout.strip().split('\n')
                ldconsole_emulators = [line.strip() for line in lines[1:] if line.strip()]
                
                print(f"\n📋 ldconsole вернул {len(ldconsole_emulators)} эмуляторов:")
                for emu in ldconsole_emulators:
                    print(f"   - {emu}")
                
                # Сравнение с найденными по файлам
                file_names = {e["name"] for e in emulators if e["name"]}
                ldconsole_names = set(ldconsole_emulators)
                
                print(f"\n🔍 Сравнение:")
                print(f"   По файлам: {len(file_names)} эмуляторов")
                print(f"   По ldconsole: {len(ldconsole_names)} эмуляторов")
                
                only_in_files = file_names - ldconsole_names
                only_in_ldconsole = ldconsole_names - file_names
                
                if only_in_files:
                    print(f"\n   ⚠️ Только в файлах: {only_in_files}")
                
                if only_in_ldconsole:
                    print(f"\n   ⚠️ Только в ldconsole: {only_in_ldconsole}")
                
                if file_names == ldconsole_names:
                    print(f"\n   ✅ Полное совпадение!")
                
        except Exception as e:
            print(f"❌ Ошибка выполнения ldconsole: {e}")
    else:
        print(f"⚠️ ldconsole не найден: {ldconsole_path}")
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    
    print(f"\n✅ LDPlayer установлен: {ldplayer_path}")
    if result["vms_folder"]:
        print(f"✅ Папка VMs: {result['vms_folder']}")
    print(f"✅ Найдено .config файлов: {len(config_files)}")
    print(f"✅ Распознано эмуляторов: {len(emulators)}")
    
    if emulators:
        print(f"\n📋 СПИСОК ЭМУЛЯТОРОВ:")
        for i, emu in enumerate(emulators, 1):
            print(f"\n{i}. {emu['name']}")
            print(f"   Конфиг: {Path(emu['config_file']).name}")
            if emu['properties']:
                # Показать важные свойства
                key_props = ['resolution.width', 'resolution.height', 
                           'propertySettings.phoneMemory', 'propertySettings.phoneCPUCores']
                for prop in key_props:
                    if prop in emu['properties']:
                        print(f"   {prop}: {emu['properties'][prop]}")
    
    return result


if __name__ == "__main__":
    try:
        result = scan_ldplayer_folders()
        
        # Сохранить результат в JSON
        output_file = Path(__file__).parent / "scan_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Результаты сохранены в: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
