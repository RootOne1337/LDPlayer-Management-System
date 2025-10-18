"""
JWT Authentication Module
Полная реализация JWT для FastAPI
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from functools import lru_cache

import jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer


# Configuration
class JWTConfig:
    """JWT конфигурация"""
    
    # Получить из переменных окружения или использовать default
    SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "your-super-secret-key-change-this-in-production-12345"
    )
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))


# Pydantic Models
class TokenData(BaseModel):
    """Данные в JWT токене"""
    username: str
    user_id: Optional[str] = None
    scopes: list = []


class Token(BaseModel):
    """Ответ с токеном"""
    access_token: str
    token_type: str
    expires_in: int


class UserLogin(BaseModel):
    """Запрос на вход"""
    username: str
    password: str


class User(BaseModel):
    """Модель пользователя"""
    username: str
    user_id: Optional[str] = None
    active: bool = True
    scopes: list = []


# Fake users database (используется для примера)
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "user_id": "001",
        "hashed_password": os.getenv("ADMIN_PASSWORD_HASH", "admin"),  # В production - хешировать!
        "active": True,
        "scopes": ["read", "write", "delete"]
    },
    "user": {
        "username": "user",
        "user_id": "002",
        "hashed_password": os.getenv("USER_PASSWORD_HASH", "user"),
        "active": True,
        "scopes": ["read"]
    }
}


class JWTManager:
    """
    Менеджер JWT токенов
    """
    
    def __init__(self, config: JWTConfig = JWTConfig()):
        self.config = config
    
    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Создать JWT токен
        
        Args:
            data: Данные для включения в токен
            expires_delta: Время жизни токена
            
        Returns:
            JWT токен
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.EXPIRATION_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """
        Проверить JWT токен
        
        Args:
            token: JWT токен
            
        Returns:
            Данные из токена
            
        Raises:
            HTTPException: Если токен невалиден
        """
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM]
            )
            
            username: str = payload.get("sub")
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing username"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def login(
        self,
        username: str,
        password: str,
        scopes: list = None
    ) -> Token:
        """
        Выполнить вход и получить токен
        
        Args:
            username: Имя пользователя
            password: Пароль
            scopes: Список разрешений
            
        Returns:
            Объект Token с access_token
            
        Raises:
            HTTPException: Если учётные данные неверны
        """
        # Проверить учётные данные
        user = FAKE_USERS_DB.get(username)
        
        if not user or user["hashed_password"] != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user["active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )
        
        # Создать токен
        access_scopes = scopes or user.get("scopes", [])
        
        token_data = {
            "sub": user["username"],
            "user_id": user["user_id"],
            "scopes": access_scopes
        }
        
        access_token = self.create_access_token(data=token_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.config.EXPIRATION_MINUTES * 60
        )


# Глобальный менеджер
jwt_manager = JWTManager()
security = HTTPBearer()


# Dependency functions
async def get_current_user(
    credentials = Depends(security)
) -> User:
    """
    Получить текущего пользователя из токена
    
    Args:
        credentials: HTTP Bearer токен
        
    Returns:
        Объект User
    """
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)
    
    username: str = payload.get("sub")
    user_id: str = payload.get("user_id")
    scopes: list = payload.get("scopes", [])
    
    return User(
        username=username,
        user_id=user_id,
        scopes=scopes
    )


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Получить текущего администратора
    Проверяет наличие прав write/delete
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        Объект User (если это админ)
        
    Raises:
        HTTPException: Если пользователь не админ
    """
    if "write" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    
    return current_user


# Функции для работы с пользователями
def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Аутентифицировать пользователя
    
    Args:
        username: Имя пользователя
        password: Пароль
        
    Returns:
        Данные пользователя или None
    """
    user = FAKE_USERS_DB.get(username)
    
    if not user:
        return None
    
    # В production: использовать bcrypt или другой алгоритм хеширования
    if user["hashed_password"] != password:
        return None
    
    if not user["active"]:
        return None
    
    return user


if __name__ == "__main__":
    # Пример использования
    print("\n" + "="*60)
    print("🔐 JWT Authentication Manager")
    print("="*60)
    
    # Создать менеджер
    manager = JWTManager()
    
    # Вход
    print("\n[1] Login Test")
    try:
        token_response = manager.login("admin", "admin")
        print(f"✅ Login successful")
        print(f"   Token: {token_response.access_token[:50]}...")
        print(f"   Expires in: {token_response.expires_in} seconds")
    except HTTPException as e:
        print(f"❌ Login failed: {e.detail}")
    
    # Проверить токен
    print(f"\n[2] Token Verification Test")
    try:
        token = manager.create_access_token({"sub": "admin"})
        payload = manager.verify_token(token)
        print(f"✅ Token verified")
        print(f"   Username: {payload.get('sub')}")
        print(f"   Expires: {datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)}")
    except HTTPException as e:
        print(f"❌ Verification failed: {e.detail}")
    
    # Попытка с неверным паролем
    print(f"\n[3] Failed Login Test")
    try:
        token_response = manager.login("admin", "wrong_password")
    except HTTPException as e:
        print(f"✅ Correctly rejected: {e.detail}")
    
    print("\n" + "="*60)
    print("✅ JWT Authentication ready!")
    print("="*60)
