"""
Secure Secrets Management
Шифрование и хранение конфиденциальной информации
"""
import os
import json
from cryptography.fernet import Fernet
from pathlib import Path
import hashlib
import base64


class SecretsManager:
    """
    Управление зашифрованными секретами
    """
    
    def __init__(self, secrets_file: str = "secrets.key"):
        self.secrets_file = secrets_file
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Загрузить или создать ключ шифрования"""
        if os.path.exists(self.secrets_file):
            with open(self.secrets_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.secrets_file, 'wb') as f:
                f.write(key)
            # Установить безопасные права доступа
            os.chmod(self.secrets_file, 0o600)
            print(f"✅ Created encryption key: {self.secrets_file}")
            return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Зашифровать текст
        
        Args:
            plaintext: Открытый текст
            
        Returns:
            Зашифрованный текст в base64
        """
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровать текст
        
        Args:
            ciphertext: Зашифрованный текст в base64
            
        Returns:
            Открытый текст
        """
        try:
            encrypted = base64.b64decode(ciphertext)
            plaintext = self.cipher.decrypt(encrypted).decode()
            return plaintext
        except Exception as e:
            raise ValueError(f"Failed to decrypt: {e}")
    
    def encrypt_password(self, password: str) -> str:
        """Зашифровать пароль"""
        return self.encrypt(password)
    
    def decrypt_password(self, encrypted: str) -> str:
        """Расшифровать пароль"""
        return self.decrypt(encrypted)


class ConfigEncryption:
    """
    Управление шифрованием конфигурационного файла
    """
    
    def __init__(self, config_path: str = "config.json", secrets_file: str = "secrets.key"):
        self.config_path = config_path
        self.secrets_manager = SecretsManager(secrets_file)
    
    def encrypt_config(self, output_path: str = "config.encrypted.json"):
        """
        Зашифровать пароли в config.json
        
        Args:
            output_path: Путь для сохранения зашифрованного config
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Зашифровать пароли для каждой рабочей станции
        if 'workstations' in config:
            for workstation in config['workstations']:
                if 'password' in workstation:
                    plaintext = workstation['password']
                    encrypted = self.secrets_manager.encrypt(plaintext)
                    workstation['password'] = encrypted
                    workstation['_encrypted'] = True  # Маркер шифрования
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Encrypted config saved to: {output_path}")
    
    def decrypt_config(self, encrypted_path: str = "config.encrypted.json") -> dict:
        """
        Расшифровать config.json
        
        Args:
            encrypted_path: Путь к зашифрованному config
            
        Returns:
            Расшифрованная конфигурация
        """
        with open(encrypted_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Расшифровать пароли
        if 'workstations' in config:
            for workstation in config['workstations']:
                if workstation.get('_encrypted') and 'password' in workstation:
                    encrypted = workstation['password']
                    plaintext = self.secrets_manager.decrypt(encrypted)
                    workstation['password'] = plaintext
                    del workstation['_encrypted']  # Удалить маркер
        
        return config
    
    def create_env_template(self, output_path: str = ".env.template"):
        """
        Создать шаблон .env файла для environment переменных
        
        Args:
            output_path: Путь к шаблону
        """
        template = """# LDPlayer Management System - Security Configuration

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Default Admin Credentials (CHANGE IN PRODUCTION!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me-immediately

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False

# Database
DATABASE_URL=sqlite:///./ldplayer_system.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
RATE_LIMIT_PER_MINUTE=60

# LDPlayer Configuration
LDPLAYER_PATH=C:\\LDPlayer\\LDPlayer9

# Remote Management (optional)
ENABLE_WINRM=False
WINRM_PORT=5985
"""
        with open(output_path, 'w') as f:
            f.write(template)
        print(f"✅ Created .env template: {output_path}")


def main():
    """
    Пример использования
    """
    print("\n" + "="*60)
    print("🔐 LDPlayer Management System - Secrets Manager")
    print("="*60)
    
    # Инициализировать менеджер секретов
    secrets = SecretsManager()
    
    # Пример: Зашифровать пароль
    password = "MySecurePassword123!"
    encrypted = secrets.encrypt_password(password)
    print(f"\n✅ Original password: {password}")
    print(f"✅ Encrypted: {encrypted[:50]}...")
    
    # Расшифровать
    decrypted = secrets.decrypt_password(encrypted)
    print(f"✅ Decrypted: {decrypted}")
    
    # Работа с config
    print(f"\n" + "-"*60)
    print("Config Encryption")
    print("-"*60)
    
    config_enc = ConfigEncryption("config.json")
    
    try:
        # Зашифровать config
        config_enc.encrypt_config("config.encrypted.json")
        
        # Расшифровать
        decrypted_config = config_enc.decrypt_config("config.encrypted.json")
        print(f"✅ Successfully encrypted/decrypted {len(decrypted_config.get('workstations', []))} workstations")
    except FileNotFoundError:
        print("⚠️  config.json not found - creating template")
        config_enc.create_env_template()
    
    # Создать .env шаблон
    config_enc.create_env_template(".env.template")
    
    print("\n" + "="*60)
    print("🔐 Secrets management configured!")
    print("="*60)


if __name__ == "__main__":
    main()
