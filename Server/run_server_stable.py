"""
Production Server Runner - No Auto-Reload for Testing
"""
import uvicorn
import sys
import os
from pathlib import Path


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
        print("   Запуск без HTTPS...")
        return None, None
    except Exception as e:
        print(f"⚠️  Ошибка при создании сертификата: {e}")
        print("   Запуск без HTTPS...")
        return None, None


if __name__ == "__main__":
    print("="*60)
    print("🚀 Starting LDPlayer Management System Server")
    print("   Mode: Production (No Auto-Reload)")
    print("   Port: 8000")
    print("="*60)
    print()
    
    # Создать SSL сертификаты если нужны
    ssl_certfile, ssl_keyfile = generate_self_signed_cert()
    print()
    
    if ssl_certfile and ssl_keyfile:
        print(f"🔒 HTTPS включен (cert: {ssl_certfile}, key: {ssl_keyfile})")
        print()
    else:
        print("⚠️  HTTPS не включен - используется HTTP")
        print()
    
    uvicorn.run(
        "src.core.server_modular:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,  # Disable auto-reload for stable testing
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile
    )
