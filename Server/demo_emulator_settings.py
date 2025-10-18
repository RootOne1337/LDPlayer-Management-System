#!/usr/bin/env python3
"""
Демонстрация создания и изменения настроек эмуляторов.
"""

import sys
import subprocess
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def demo_emulator_management():
    """Демонстрация управления эмуляторами."""
    print("🎮 ДЕМОНСТРАЦИЯ УПРАВЛЕНИЯ НАСТРОЙКАМИ ЭМУЛЯТОРОВ")
    print("=" * 70)
    
    try:
        from src.core.config import WorkstationConfig
        from src.remote.workstation import WorkstationManager
        
        # Конфигурация
        config = WorkstationConfig(
            id="local",
            name="Локальная машина",
            ip_address="127.0.0.1",
            username="local",
            password="",
            ldplayer_path=r"C:\LDPlayer\LDPlayer9",
            ldconsole_path=r"C:\LDPlayer\LDPlayer9\ldconsole.exe"
        )
        
        manager = WorkstationManager(config)
        
        # Локальная подмена
        def local_run_command(command, args=None):
            args = args or []
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        
        manager.run_command = local_run_command
        
        print("✅ Менеджер готов\n")
        
        # Получить текущие эмуляторы
        print("📋 ТЕКУЩИЕ ЭМУЛЯТОРЫ:")
        print("-" * 70)
        emulators = manager.get_emulators_list()
        for emu in emulators:
            print(f"   {emu.name} - {emu.status.value}")
        
        # ПРИМЕР 1: Создать эмулятор с настройками
        print(f"\n{'=' * 70}")
        print("ПРИМЕР 1: Создание эмулятора с настройками")
        print(f"{'=' * 70}\n")
        
        new_name = "test_configured"
        
        print(f"Создание эмулятора '{new_name}' с конфигурацией...")
        
        success, msg = manager.create_emulator(
            new_name,
            config={
                'resolution': '1920,1080,240',
                'cpu': 4,
                'memory': 4096
            }
        )
        
        print(f"   {'✅' if success else '❌'} {msg}")
        
        # ПРИМЕР 2: Изменить настройки существующего эмулятора
        print(f"\n{'=' * 70}")
        print("ПРИМЕР 2: Изменение настроек эмулятора 'nifilim'")
        print(f"{'=' * 70}\n")
        
        if any(emu.name == 'nifilim' for emu in emulators):
            print("Изменение производительности...")
            
            success, msg = manager.modify_emulator('nifilim', {
                'cpu': 4,
                'memory': 8192,
                'resolution': '1920,1080,320'
            })
            
            print(f"   {'✅' if success else '❌'} {msg}")
            
            print("\nИзменение идентификации устройства...")
            
            success, msg = manager.modify_emulator('nifilim', {
                'manufacturer': 'samsung',
                'model': 'SM-G960F',
                'imei': 'auto',
                'mac': 'auto'
            })
            
            print(f"   {'✅' if success else '❌'} {msg}")
            
            print("\nИзменение системных настроек...")
            
            success, msg = manager.modify_emulator('nifilim', {
                'root': 1,
                'autorotate': 0,
                'lockwindow': 0
            })
            
            print(f"   {'✅' if success else '❌'} {msg}")
        
        # ПРИМЕР 3: Создать несколько эмуляторов с разными профилями
        print(f"\n{'=' * 70}")
        print("ПРИМЕР 3: Создание эмуляторов с разными профилями")
        print(f"{'=' * 70}\n")
        
        profiles = [
            {
                'name': 'samsung_s10',
                'config': {
                    'resolution': '1440,2960,560',
                    'cpu': 4,
                    'memory': 6144
                },
                'identity': {
                    'manufacturer': 'samsung',
                    'model': 'SM-G973F',
                    'imei': 'auto',
                    'mac': 'auto'
                }
            },
            {
                'name': 'xiaomi_mi9',
                'config': {
                    'resolution': '1080,2340,440',
                    'cpu': 4,
                    'memory': 4096
                },
                'identity': {
                    'manufacturer': 'xiaomi',
                    'model': 'MI 9',
                    'imei': 'auto',
                    'mac': 'auto'
                }
            }
        ]
        
        for profile in profiles:
            print(f"\nСоздание профиля: {profile['name']}")
            
            # Создать с базовой конфигурацией
            success, msg = manager.create_emulator(
                profile['name'],
                config=profile['config']
            )
            
            if success:
                print(f"   ✅ Создан")
                
                # Применить идентификацию
                success2, msg2 = manager.modify_emulator(
                    profile['name'],
                    profile['identity']
                )
                
                print(f"   {'✅' if success2 else '❌'} Идентификация: {msg2}")
            else:
                print(f"   ❌ {msg}")
        
        # Финальный список
        print(f"\n{'=' * 70}")
        print("📋 ФИНАЛЬНЫЙ СПИСОК ЭМУЛЯТОРОВ")
        print(f"{'=' * 70}\n")
        
        final_emulators = manager.get_emulators_list()
        
        for emu in final_emulators:
            print(f"   {emu.name} - {emu.status.value}")
        
        print(f"\n✅ Всего эмуляторов: {len(final_emulators)}")
        
        # Сводка возможностей
        print(f"\n{'=' * 70}")
        print("📚 СВОДКА ВОЗМОЖНОСТЕЙ")
        print(f"{'=' * 70}")
        
        print("""
✅ СОЗДАНИЕ с настройками:
   manager.create_emulator(name, config={
       'resolution': '1920,1080,240',
       'cpu': 4,
       'memory': 8192
   })

✅ ИЗМЕНЕНИЕ настроек:
   manager.modify_emulator(name, {
       'manufacturer': 'samsung',
       'model': 'SM-G960F',
       'imei': 'auto',
       'mac': 'auto',
       'root': 1
   })

✅ Поддерживаемые параметры:
   🖥️  Производительность: cpu, memory, resolution
   📱  Идентификация: manufacturer, model, imei, imsi, mac, androidid
   🔧  Система: root, autorotate, lockwindow

✅ Другие операции:
   - manager.start_emulator(name)
   - manager.stop_emulator(name)
   - manager.rename_emulator(old_name, new_name)
   - manager.delete_emulator(name)
   - manager.get_emulators_list()
        """)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = demo_emulator_management()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(0)
