#!/usr/bin/env python3
"""
Детальный анализ конфигурационных файлов эмуляторов.
Показать все доступные настройки.
"""

import json
from pathlib import Path

def analyze_emulator_config(config_path: Path):
    """Проанализировать один конфиг эмулятора."""
    print(f"\n{'=' * 70}")
    print(f"📄 {config_path.name}")
    print(f"{'=' * 70}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"\n📊 ОСНОВНЫЕ НАСТРОЙКИ:")
        print("-" * 70)
        
        # Группировка настроек
        categories = {
            'propertySettings': '🔧 Свойства устройства',
            'advancedSettings': '⚙️ Расширенные настройки',
            'basicSettings': '📋 Базовые настройки',
            'statusSettings': '📍 Статус и пути',
            'networkSettings': '🌐 Сеть'
        }
        
        for category, title in categories.items():
            matching_keys = [k for k in config.keys() if k.startswith(category)]
            
            if matching_keys:
                print(f"\n{title}:")
                
                for key in sorted(matching_keys):
                    value = config[key]
                    
                    # Форматирование значения
                    if isinstance(value, dict):
                        print(f"   {key}:")
                        for k, v in value.items():
                            print(f"      {k}: {v}")
                    elif isinstance(value, bool):
                        print(f"   {key}: {'✅' if value else '❌'} {value}")
                    elif isinstance(value, (int, float)):
                        print(f"   {key}: {value}")
                    elif isinstance(value, str) and len(value) > 50:
                        print(f"   {key}: {value[:50]}...")
                    else:
                        print(f"   {key}: {value}")
        
        # Важные параметры для изменения
        print(f"\n{'=' * 70}")
        print("⭐ КЛЮЧЕВЫЕ ПАРАМЕТРЫ ДЛЯ ИЗМЕНЕНИЯ:")
        print("=" * 70)
        
        important_params = {
            'advancedSettings.resolution': 'Разрешение экрана',
            'advancedSettings.resolutionDpi': 'DPI',
            'advancedSettings.cpuCount': 'Количество ядер CPU',
            'advancedSettings.memorySize': 'Размер памяти (MB)',
            'propertySettings.phoneModel': 'Модель телефона',
            'propertySettings.phoneManufacturer': 'Производитель',
            'propertySettings.phoneIMEI': 'IMEI',
            'propertySettings.phoneIMSI': 'IMSI',
            'propertySettings.phoneAndroidId': 'Android ID',
            'propertySettings.macAddress': 'MAC адрес',
            'basicSettings.rootMode': 'Root режим',
            'basicSettings.adbDebug': 'ADB отладка',
            'networkSettings.networkEnable': 'Сеть включена',
            'networkSettings.networkInterface': 'Сетевой интерфейс'
        }
        
        for param, description in important_params.items():
            if param in config:
                value = config[param]
                if isinstance(value, dict):
                    print(f"\n   {description} ({param}):")
                    for k, v in value.items():
                        print(f"      {k}: {v}")
                else:
                    print(f"   {description} ({param}): {value}")
        
        return config
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def main():
    """Главная функция."""
    print("🔍 АНАЛИЗ КОНФИГУРАЦИОННЫХ ФАЙЛОВ ЭМУЛЯТОРОВ")
    print("=" * 70)
    
    ldplayer_path = Path(r"C:\LDPlayer\LDPlayer9")
    configs_path = ldplayer_path / "vms" / "config"
    
    print(f"\n📂 Путь к конфигам: {configs_path}")
    print(f"   Существует: {configs_path.exists()}")
    
    if not configs_path.exists():
        print("\n❌ Папка с конфигами не найдена!")
        return
    
    # Найти все .config файлы
    config_files = list(configs_path.glob("*.config"))
    
    print(f"\n📋 Найдено конфигов: {len(config_files)}")
    
    all_configs = {}
    
    for config_file in sorted(config_files):
        config_data = analyze_emulator_config(config_file)
        if config_data:
            all_configs[config_file.name] = config_data
    
    # Сводная таблица возможных изменений
    print(f"\n\n{'=' * 70}")
    print("📊 СВОДНАЯ ТАБЛИЦА ДОСТУПНЫХ НАСТРОЕК")
    print("=" * 70)
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║ ПАРАМЕТР                          │ ВОЗМОЖНЫЕ ЗНАЧЕНИЯ             ║
╠════════════════════════════════════════════════════════════════════╣
║ 🖥️ ПРОИЗВОДИТЕЛЬНОСТЬ                                              ║
╟────────────────────────────────────────────────────────────────────╢
║ CPU ядер (cpuCount)               │ 1, 2, 3, 4, 8                  ║
║ Память (memorySize)               │ 256, 512, 1024, 2048, 4096,    ║
║                                   │ 8192 MB                        ║
║ DPI (resolutionDpi)               │ 120, 160, 240, 320, 480        ║
╠════════════════════════════════════════════════════════════════════╣
║ 📱 РАЗРЕШЕНИЕ ЭКРАНА                                                ║
╟────────────────────────────────────────────────────────────────────╢
║ resolution.width                  │ 540, 720, 1080, 1440, 1920     ║
║ resolution.height                 │ 960, 1280, 1920, 2560, 1080    ║
╠════════════════════════════════════════════════════════════════════╣
║ 📲 ИДЕНТИФИКАЦИЯ УСТРОЙСТВА                                         ║
╟────────────────────────────────────────────────────────────────────╢
║ phoneModel                        │ Любая строка (SM-S9110, ...)   ║
║ phoneManufacturer                 │ samsung, xiaomi, huawei, ...   ║
║ phoneIMEI                         │ 15-значное число               ║
║ phoneIMSI                         │ 15-значное число               ║
║ phoneAndroidId                    │ 16-символьный hex              ║
║ macAddress                        │ 12-символьный hex (XX:XX:...)  ║
║ phoneSimSerial                    │ 20-значное число               ║
╠════════════════════════════════════════════════════════════════════╣
║ 🔧 СИСТЕМНЫЕ НАСТРОЙКИ                                              ║
╟────────────────────────────────────────────────────────────────────╢
║ rootMode                          │ true / false                   ║
║ adbDebug                          │ 0, 1, 2                        ║
║ autoRotate                        │ true / false                   ║
║ verticalSync                      │ true / false                   ║
║ lockWindow                        │ true / false                   ║
╠════════════════════════════════════════════════════════════════════╣
║ 🌐 СЕТЬ                                                             ║
╟────────────────────────────────────────────────────────────────────╢
║ networkEnable                     │ true / false                   ║
║ networkStatic                     │ true / false (статический IP)  ║
║ networkAddress                    │ IP адрес                       ║
║ networkGateway                    │ IP шлюза                       ║
║ networkDNS1/DNS2                  │ DNS сервера                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Команды ldconsole для изменения
    print(f"\n{'=' * 70}")
    print("🔧 КОМАНДЫ LDCONSOLE ДЛЯ ИЗМЕНЕНИЯ НАСТРОЕК")
    print("=" * 70)
    
    print("""
# Изменить разрешение:
ldconsole modify --name <имя> --resolution <width>,<height>,<dpi>
Пример: ldconsole modify --name nifilim --resolution 1920,1080,240

# Изменить CPU:
ldconsole modify --name <имя> --cpu <1|2|3|4>
Пример: ldconsole modify --name nifilim --cpu 4

# Изменить память:
ldconsole modify --name <имя> --memory <256|512|1024|2048|4096|8192>
Пример: ldconsole modify --name nifilim --memory 4096

# Изменить модель устройства:
ldconsole modify --name <имя> --manufacturer <производитель> --model <модель>
Пример: ldconsole modify --name nifilim --manufacturer samsung --model SM-G960F

# Изменить IMEI (авто):
ldconsole modify --name <имя> --imei auto

# Изменить IMEI (конкретный):
ldconsole modify --name <имя> --imei 865166023949731

# Изменить MAC адрес:
ldconsole modify --name <имя> --mac auto

# Включить/выключить Root:
ldconsole modify --name <имя> --root <1|0>

# Автоповорот:
ldconsole modify --name <имя> --autorotate <1|0>

# Блокировка окна:
ldconsole modify --name <имя> --lockwindow <1|0>
    """)
    
    # Сохранить в JSON
    output_file = Path(__file__).parent / "emulator_configs_analysis.json"
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
