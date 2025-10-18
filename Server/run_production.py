#!/usr/bin/env python3
"""
Запуск LDPlayer Management System Server (Production Ready Version).

Модульная версия сервера с разделенными API роутами.
"""

import sys
import os
from pathlib import Path

# Добавить корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    from src.core.server_modular import app, run_server
    from src.core.config import get_config
    from src.utils.logger import get_logger, LogCategory
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    print("Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
    sys.exit(1)


def generate_self_signed_cert():
    """Сгенерировать self-signed SSL сертификат если его нет."""
    cert_file = Path("cert.pem")
    key_file = Path("key.pem")
    
    if cert_file.exists() and key_file.exists():
        return str(cert_file), str(key_file)
    
    print("🔐 Генерирование self-signed SSL сертификата...")
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from datetime import datetime, timedelta
        import ipaddress
        
        # Генерировать приватный ключ
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Создать сертификат
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"RU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Moscow"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Moscow"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"LDPlayer"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"127.0.0.1"),
                x509.IPAddress(ipaddress.IPv4Address(u"127.0.0.1")),
            ]),
            critical=False,
        ).sign(
            private_key, hashes.SHA256(), default_backend()
        )
        
        # Сохранить сертификат и ключ
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ SSL сертификат успешно создан")
        return str(cert_file), str(key_file)
        
    except ImportError:
        print("⚠️  cryptography модуль не установлен")
        print("   Установите: pip install cryptography")
        print("   Запуск без HTTPS...")
        return None, None
    except Exception as e:
        print(f"⚠️  Ошибка при создании сертификата: {e}")
        print("   Запуск без HTTPS...")
        return None, None


def main():
    """Главная функция запуска сервера."""
    print("=" * 60)
    print("🚀 LDPlayer Management System Server")
    print("   Version: 1.0.0 (Production Ready)")
    print("   Date: October 17, 2025")
    print("=" * 60)
    print()

    try:
        # Загрузить конфигурацию
        config = get_config()
        
        print("📋 Конфигурация:")
        print(f"   Хост: {config.server.host}")
        print(f"   Порт: {config.server.port}")
        print(f"   Режим отладки: {config.server.debug}")
        print(f"   Рабочих станций: {len(config.workstations)}")
        print()

        # Вывести список рабочих станций
        if config.workstations:
            print("🏭 Рабочие станции:")
            for i, ws in enumerate(config.workstations[:5], 1):
                print(f"   {i}. {ws.name} ({ws.ip_address})")
            if len(config.workstations) > 5:
                print(f"   ... и еще {len(config.workstations) - 5}")
            print()

        # Проверить/создать SSL сертификаты
        ssl_certfile, ssl_keyfile = generate_self_signed_cert()
        
        # Информация о доступе
        print("🌐 Доступ к API:")
        protocol = "https" if ssl_certfile else "http"
        ws_protocol = "wss" if ssl_certfile else "ws"
        
        print(f"   API Docs (Swagger): {protocol}://{config.server.host}:{config.server.port}/docs")
        print(f"   API Docs (ReDoc):   {protocol}://{config.server.host}:{config.server.port}/redoc")
        print(f"   WebSocket:          {ws_protocol}://{config.server.host}:{config.server.port}/ws")
        print()

        # Доступные endpoints
        print("📡 Основные endpoints:")
        print(f"   GET  /api/health            - Проверка здоровья")
        print(f"   GET  /api/status            - Статус сервера")
        print(f"   GET  /api/workstations      - Список станций")
        print(f"   GET  /api/emulators         - Все эмуляторы")
        print(f"   GET  /api/operations        - Активные операции")
        print()
        
        # Информация об аутентификации
        print("🔐 Аутентификация:")
        print(f"   POST /auth/login            - Получить JWT токен")
        print(f"   POST /auth/refresh          - Обновить токен")
        print(f"   GET  /auth/me               - Информация пользователя")
        print()

        print("✅ Запуск сервера...")
        print("   Нажмите Ctrl+C для остановки")
        print("=" * 60)
        print()

        # Запустить сервер с HTTPS если сертификаты есть
        if ssl_certfile and ssl_keyfile:
            print(f"🔒 HTTPS включен (cert: {ssl_certfile}, key: {ssl_keyfile})")
            run_server(
                host=config.server.host,
                port=config.server.port,
                reload=config.server.reload,
                ssl_certfile=ssl_certfile,
                ssl_keyfile=ssl_keyfile
            )
        else:
            print("⚠️  HTTPS не включен - используется HTTP")
            run_server(
                host=config.server.host,
                port=config.server.port,
                reload=config.server.reload
            )

    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
