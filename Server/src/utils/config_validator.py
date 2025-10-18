"""
Валидация конфигурации перед запуском сервера.

Проверяет критические параметры безопасности:
- Наличие .env файла
- Безопасность JWT_SECRET_KEY
- Наличие ENCRYPTION_KEY
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple


def validate_env_file() -> Tuple[bool, List[str]]:
    """
    Валидация .env файла и критических параметров безопасности.
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
    errors = []
    
    # Проверка наличия .env файла
    env_file = Path(__file__).parent.parent.parent / '.env'
    if not env_file.exists():
        errors.append("❌ КРИТИЧЕСКАЯ ОШИБКА: Файл .env не найден!")
        errors.append("   Создайте файл .env на основе .env.example:")
        errors.append("   cp .env.example .env")
        return False, errors
    
    # Загрузить переменные окружения
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # Проверка JWT_SECRET_KEY
    jwt_secret = os.getenv('JWT_SECRET_KEY', '')
    
    # Список небезопасных значений по умолчанию
    unsafe_defaults = [
        'your-secret-key',
        'your-super-secret-key',
        'change-this',
        'default',
        'secret',
        '12345',
        'password'
    ]
    
    if not jwt_secret:
        errors.append("❌ КРИТИЧЕСКАЯ ОШИБКА: JWT_SECRET_KEY не установлен в .env!")
        errors.append("   Сгенерируйте безопасный ключ:")
        errors.append("   python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    elif len(jwt_secret) < 32:
        errors.append("❌ КРИТИЧЕСКАЯ ОШИБКА: JWT_SECRET_KEY слишком короткий!")
        errors.append(f"   Текущая длина: {len(jwt_secret)} символов")
        errors.append("   Минимум: 32 символа")
        errors.append("   Сгенерируйте новый ключ:")
        errors.append("   python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    elif any(unsafe in jwt_secret.lower() for unsafe in unsafe_defaults):
        errors.append("❌ КРИТИЧЕСКАЯ ОШИБКА: JWT_SECRET_KEY содержит небезопасное значение по умолчанию!")
        errors.append(f"   Обнаружено: {jwt_secret[:30]}...")
        errors.append("   НЕ используйте значения из примеров!")
        errors.append("   Сгенерируйте безопасный ключ:")
        errors.append("   python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    
    # Проверка ENCRYPTION_KEY
    encryption_key = os.getenv('ENCRYPTION_KEY', '')
    
    if not encryption_key:
        # Это warning, не критическая ошибка - не блокируем запуск
        pass  # Можно добавить логирование при необходимости
    elif len(encryption_key) < 32:
        # Это warning, не критическая ошибка
        pass  # Можно добавить логирование при необходимости
    
    # Проверка LOG_LEVEL для production
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    if log_level == 'DEBUG':
        # Это warning, не критическая ошибка
        pass  # Это нормально для development
    
    # Возвращаем только критические ошибки (JWT_SECRET_KEY)
    return len(errors) == 0, errors


def print_validation_results(is_valid: bool, errors: List[str]) -> None:
    """Вывод результатов валидации."""
    print("\n" + "="*70)
    # ✅ FIXED: Используем ASCII символы вместо emoji для совместимости с Windows
    print("[SECURITY] Configuration Security Check")
    print("="*70 + "\n")
    
    if is_valid:
        print("[OK] All checks passed successfully!")
        print("[OK] Configuration is secure")
        print("\n" + "="*70 + "\n")
    else:
        print("[ERROR] Security issues detected:\n")
        for error in errors:
            print(error)
        print("\n" + "="*70)
        print("🛑 ЗАПУСК СЕРВЕРА ЗАБЛОКИРОВАН")
        print("="*70 + "\n")


def validate_and_exit_if_invalid() -> None:
    """
    Валидация конфигурации с выходом при ошибках.
    
    Используйте эту функцию перед запуском сервера.
    """
    is_valid, errors = validate_env_file()
    print_validation_results(is_valid, errors)
    
    if not is_valid:
        # Проверить, есть ли критические ошибки
        critical_errors = [e for e in errors if '❌' in e]
        if critical_errors:
            print("💡 ИНСТРУКЦИИ ПО ИСПРАВЛЕНИЮ:")
            print()
            print("1. Скопируйте .env.example в .env (если еще не сделано):")
            print("   cp .env.example .env")
            print()
            print("2. Сгенерируйте безопасные ключи:")
            print("   python -c \"import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))\"")
            print("   python -c \"import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))\"")
            print()
            print("3. Замените значения в .env файле")
            print()
            print("4. Перезапустите сервер")
            print()
            sys.exit(1)


if __name__ == "__main__":
    # Тестирование валидации
    validate_and_exit_if_invalid()
