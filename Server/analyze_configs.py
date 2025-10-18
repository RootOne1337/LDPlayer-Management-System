#!/usr/bin/env python3
"""
Детальный анализ конфигурационных файлов эмуляторов.
"""

from pathlib import Path
import json

def analyze_config_file(config_path: Path):
    """Детально проанализировать один .config файл."""
    print(f"\n{'='*70}")
    print(f"📄 {config_path.name}")
    print(f"📍 {config_path}")
    print(f"{'='*70}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📏 Размер: {len(content)} байт")
        
        # Парсинг свойств
        properties = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                properties[key.strip()] = value.strip().strip('"')
        
        print(f"📋 Свойств: {len(properties)}")
        
        # Важные свойства
        important_keys = [
            'statusSettings.playerName',
            'statusSettings.playerIndex',
            'resolution.width',
            'resolution.height',
            'propertySettings.phoneMemory',
            'propertySettings.phoneCPUCores',
            'advancedSettings.cpuModel',
            'advancedSettings.manufacturer'
        ]
        
        print(f"\n🔑 Ключевые параметры:")
        for key in important_keys:
            if key in properties:
                print(f"   {key}: {properties[key]}")
        
        # Все свойства для полного анализа
        if len(properties) < 30:  # Если мало свойств, покажем все
            print(f"\n📝 Все свойства:")
            for key, value in sorted(properties.items()):
                print(f"   {key} = {value}")
        
        return properties
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {}


def main():
    """Главная функция."""
    print("🔬 ДЕТАЛЬНЫЙ АНАЛИЗ КОНФИГУРАЦИОННЫХ ФАЙЛОВ")
    print("="*70)
    
    ldplayer_path = Path(r"C:\LDPlayer\LDPlayer9")
    
    # Найти все .config файлы
    config_paths = []
    
    # В vms/config
    vms_config = ldplayer_path / "vms" / "config"
    if vms_config.exists():
        for f in vms_config.glob("*.config"):
            config_paths.append(f)
    
    # Непосредственно в vms
    vms_path = ldplayer_path / "vms"
    if vms_path.exists():
        for f in vms_path.glob("*.config"):
            if f not in config_paths:  # Избежать дубликатов
                config_paths.append(f)
    
    print(f"\n📂 Найдено уникальных файлов: {len(config_paths)}")
    
    # Анализ каждого файла
    all_configs = {}
    for config_path in sorted(config_paths):
        props = analyze_config_file(config_path)
        all_configs[str(config_path)] = props
    
    # Сравнение с ldconsole
    print(f"\n{'='*70}")
    print("🔧 СРАВНЕНИЕ С LDCONSOLE")
    print(f"{'='*70}")
    
    ldconsole = ldplayer_path / "ldconsole.exe"
    
    try:
        import subprocess
        result = subprocess.run(
            [str(ldconsole), "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            ldconsole_emulators = [
                line.strip() 
                for line in result.stdout.strip().split('\n')[1:] 
                if line.strip()
            ]
            
            print(f"\n✅ ldconsole list вернул:")
            for emu in ldconsole_emulators:
                print(f"   - {emu}")
            
            # Попробовать получить больше информации
            print(f"\n🔍 Дополнительные команды ldconsole:")
            
            # list2 - расширенный список
            result2 = subprocess.run(
                [str(ldconsole), "list2"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result2.returncode == 0 and result2.stdout.strip():
                print(f"\n   ldconsole list2:")
                print(f"   {result2.stdout}")
            
            # Попробовать runninglist
            result3 = subprocess.run(
                [str(ldconsole), "runninglist"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result3.returncode == 0:
                print(f"\n   ldconsole runninglist:")
                print(f"   {result3.stdout if result3.stdout.strip() else '(пусто - нет запущенных)'}")
            
            # Для каждого эмулятора из конфигов попробуем isrunning
            print(f"\n📊 Проверка статуса эмуляторов:")
            
            checked_names = set()
            for config_path, props in all_configs.items():
                name = props.get('statusSettings.playerName')
                if not name:
                    name = Path(config_path).stem
                
                if name in checked_names:
                    continue
                checked_names.add(name)
                
                result_status = subprocess.run(
                    [str(ldconsole), "isrunning", "--name", name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                status = "running" if result_status.returncode == 0 else "stopped"
                print(f"   {name}: {status}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Сохранить результат
    output_file = Path(__file__).parent / "config_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_configs, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Полный анализ сохранен в: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
