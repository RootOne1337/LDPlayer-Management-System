"""
Unit Tests for LDPlayer Management System
Using pytest framework
"""
import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Import modules to test
from src.utils.jwt_auth import JWTManager, JWTConfig, TokenData, authenticate_user
from src.utils.secrets_manager import SecretsManager, ConfigEncryption
from src.core.config import SystemConfig


class TestJWTManager:
    """Тесты для JWT менеджера"""
    
    @pytest.fixture
    def jwt_manager(self):
        """Fixture для JWT менеджера"""
        return JWTManager()
    
    def test_create_token(self, jwt_manager):
        """Тест создания токена"""
        token_data = {"sub": "testuser"}
        token = jwt_manager.create_access_token(token_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self, jwt_manager):
        """Тест проверки валидного токена"""
        token_data = {"sub": "testuser", "user_id": "123"}
        token = jwt_manager.create_access_token(token_data)
        
        payload = jwt_manager.verify_token(token)
        
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"
    
    def test_verify_token_expired(self, jwt_manager):
        """Тест проверки истёкшего токена"""
        token_data = {"sub": "testuser"}
        # Создать с временем жизни -1 минута
        from datetime import timedelta
        token = jwt_manager.create_access_token(
            token_data,
            expires_delta=timedelta(minutes=-1)
        )
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            jwt_manager.verify_token(token)
    
    def test_verify_token_invalid(self, jwt_manager):
        """Тест проверки невалидного токена"""
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            jwt_manager.verify_token("invalid.token.data")
    
    def test_login_success(self, jwt_manager):
        """Тест успешного входа"""
        token_response = jwt_manager.login("admin", "admin")
        
        assert token_response.access_token is not None
        assert token_response.token_type == "bearer"
        assert token_response.expires_in > 0
    
    def test_login_invalid_credentials(self, jwt_manager):
        """Тест входа с неверными учётными данными"""
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            jwt_manager.login("admin", "wrongpassword")
    
    def test_login_nonexistent_user(self, jwt_manager):
        """Тест входа с несуществующим пользователем"""
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            jwt_manager.login("nonexistent", "password")


class TestSecretsManager:
    """Тесты для менеджера секретов"""
    
    @pytest.fixture
    def temp_secrets_file(self):
        """Fixture для временного файла секретов"""
        from cryptography.fernet import Fernet
        fd, path = tempfile.mkstemp(suffix=".key")
        os.close(fd)
        # Создать валидный Fernet ключ в файле
        key = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(key)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def secrets_manager(self, temp_secrets_file):
        """Fixture для менеджера секретов"""
        return SecretsManager(secrets_file=temp_secrets_file)
    
    def test_encrypt_decrypt_password(self, secrets_manager):
        """Тест шифрования и расшифровки пароля"""
        password = "MySecurePassword123!"
        
        encrypted = secrets_manager.encrypt_password(password)
        decrypted = secrets_manager.decrypt_password(encrypted)
        
        assert decrypted == password
        assert encrypted != password
    
    def test_encrypt_decrypt_text(self, secrets_manager):
        """Тест шифрования и расшифровки текста"""
        plaintext = "Sensitive information"
        
        encrypted = secrets_manager.encrypt(plaintext)
        decrypted = secrets_manager.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_consistency(self, secrets_manager):
        """Тест что одинаковый текст шифруется по-разному"""
        plaintext = "test"
        
        encrypted1 = secrets_manager.encrypt(plaintext)
        encrypted2 = secrets_manager.encrypt(plaintext)
        
        # Шифрование Fernet использует random IV
        assert encrypted1 != encrypted2
        # Но расшифровка должна быть одинаковой
        assert secrets_manager.decrypt(encrypted1) == secrets_manager.decrypt(encrypted2)
    
    def test_decrypt_invalid_ciphertext(self, secrets_manager):
        """Тест расшифровки невалидного текста"""
        with pytest.raises(ValueError):
            secrets_manager.decrypt("invalid-base64-!")


class TestConfigEncryption:
    """Тесты для шифрования конфигурации"""
    
    @pytest.fixture
    def temp_config_files(self):
        """Fixture для временных файлов конфигурации"""
        # Создать temp config.json
        config_data = {
            "ldplayer_path": "C:\\\\LDPlayer\\\\LDPlayer9",
            "workstations": [
                {
                    "name": "Test Station 1",
                    "host": "192.168.1.101",
                    "username": "admin",
                    "password": "pass123"
                },
                {
                    "name": "Test Station 2",
                    "host": "192.168.1.102",
                    "username": "admin",
                    "password": "pass456"
                }
            ]
        }
        
        config_fd, config_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(config_fd, 'w') as f:
            json.dump(config_data, f)
        
        # Создать временный файл ключей с валидным Fernet ключом
        from cryptography.fernet import Fernet
        secrets_fd, secrets_path = tempfile.mkstemp(suffix=".key")
        key = Fernet.generate_key()
        with os.fdopen(secrets_fd, 'wb') as f:
            f.write(key)
        
        yield config_path, secrets_path
        
        # Cleanup
        for path in [config_path, secrets_path]:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_encrypt_config(self, temp_config_files):
        """Тест шифрования конфигурации"""
        config_path, secrets_path = temp_config_files
        
        config_enc = ConfigEncryption(config_path, secrets_path)
        encrypted_path = config_path.replace(".json", ".encrypted.json")
        
        config_enc.encrypt_config(encrypted_path)
        
        assert os.path.exists(encrypted_path)
        
        with open(encrypted_path, 'r') as f:
            encrypted_config = json.load(f)
        
        # Проверить что пароли зашифрованы
        for ws in encrypted_config.get("workstations", []):
            assert ws.get("_encrypted") == True
            assert ws["password"] != "pass123"
            assert ws["password"] != "pass456"
        
        os.unlink(encrypted_path)
    
    def test_decrypt_config(self, temp_config_files):
        """Тест расшифровки конфигурации"""
        config_path, secrets_path = temp_config_files
        
        config_enc = ConfigEncryption(config_path, secrets_path)
        encrypted_path = config_path.replace(".json", ".encrypted.json")
        
        # Зашифровать
        config_enc.encrypt_config(encrypted_path)
        
        # Расшифровать
        decrypted_config = config_enc.decrypt_config(encrypted_path)
        
        # Проверить что пароли восстановлены
        assert decrypted_config["workstations"][0]["password"] == "pass123"
        assert decrypted_config["workstations"][1]["password"] == "pass456"
        
        # Маркеры должны быть удалены
        for ws in decrypted_config.get("workstations", []):
            assert "_encrypted" not in ws
        
        os.unlink(encrypted_path)


class TestAuthenticateUser:
    """Тесты для аутентификации пользователей"""
    
    def test_authenticate_admin_valid(self):
        """Тест аутентификации администратора с верными данными"""
        user = authenticate_user("admin", "admin")
        
        assert user is not None
        assert user["username"] == "admin"
        assert user["active"] == True
    
    def test_authenticate_user_valid(self):
        """Тест аутентификации пользователя с верными данными"""
        user = authenticate_user("user", "user")
        
        assert user is not None
        assert user["username"] == "user"
        assert user["active"] == True
    
    def test_authenticate_invalid_password(self):
        """Тест аутентификации с неверным паролем"""
        user = authenticate_user("admin", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_nonexistent_user(self):
        """Тест аутентификации несуществующего пользователя"""
        user = authenticate_user("nonexistent", "password")
        
        assert user is None


# Parametrized tests
@pytest.mark.parametrize("password", [
    "simple",
    "P@ssw0rd!",
    "Very$Long$P@ssw0rd$W1th$Spec1al$Ch@rs$123",
    "🔒 Unicode пароль 中文",
])
def test_secrets_manager_various_passwords(password):
    """Тест шифрования различных паролей"""
    secrets = SecretsManager()
    
    encrypted = secrets.encrypt_password(password)
    decrypted = secrets.decrypt_password(encrypted)
    
    assert decrypted == password


# Integration tests
class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_auth_flow(self):
        """Тест полного цикла аутентификации"""
        jwt_manager = JWTManager()
        
        # 1. Вход
        token_response = jwt_manager.login("admin", "admin")
        assert token_response.access_token is not None
        
        # 2. Проверка токена
        payload = jwt_manager.verify_token(token_response.access_token)
        assert payload["sub"] == "admin"
        
        # 3. Создание нового токена с тем же пользователем
        new_token = jwt_manager.create_access_token({"sub": payload["sub"]})
        assert new_token is not None
        
        # 4. Проверка нового токена
        new_payload = jwt_manager.verify_token(new_token)
        assert new_payload["sub"] == "admin"


# Performance tests
class TestPerformance:
    """Тесты производительности"""
    
    def test_jwt_creation_performance(self):
        """Тест производительности создания JWT"""
        jwt_manager = JWTManager()
        
        import time
        start = time.time()
        
        for _ in range(100):
            jwt_manager.create_access_token({"sub": "testuser"})
        
        elapsed = time.time() - start
        
        # Должно быть быстро (менее 2 секунд для 100 токенов)
        assert elapsed < 2.0
    
    def test_encryption_performance(self):
        """Тест производительности шифрования"""
        secrets = SecretsManager()
        
        import time
        start = time.time()
        
        for _ in range(50):
            encrypted = secrets.encrypt("test password")
            secrets.decrypt(encrypted)
        
        elapsed = time.time() - start
        
        # Должно быть быстро (менее 5 секунд для 50 пар)
        assert elapsed < 5.0


if __name__ == "__main__":
    # Запустить тесты: pytest tests_security.py -v
    print("✅ Security tests module loaded")
    print("Run with: pytest tests_security.py -v")
