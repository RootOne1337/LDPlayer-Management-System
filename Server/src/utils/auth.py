"""
JWT Authentication Module for LDPlayer Management System

Features:
- JWT token generation and validation
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Token refresh mechanism
- User management (in-memory, can be extended to DB)

Security:
- Passwords hashed with bcrypt
- JWT tokens with expiration
- Refresh tokens for extended sessions
- Role-based permissions
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
import jwt
import os
from passlib.context import CryptContext
from fastapi import HTTPException, status
from ..core.models import User, UserInDB, UserRole, Token, TokenData
from ..utils.logger import get_logger, LogCategory


# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use defaults or fail if SECRET_KEY missing

# JWT Settings (from environment variables)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable not set! "
        "Please create a .env file with JWT_SECRET_KEY=<your-secret-key>"
    )

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Logger
logger = get_logger(LogCategory.API)


# ============================================================================
# IN-MEMORY USER DATABASE (для демонстрации)
# В production: заменить на PostgreSQL/MongoDB
# ============================================================================

USERS_DB: Dict[str, UserInDB] = {}

def init_default_users():
    """Инициализация пользователей по умолчанию."""
    default_users = [
        {
            "username": "admin",
            "password": "admin123",  # Будет хэширован
            "email": "admin@ldplayer.local",
            "full_name": "System Administrator",
            "role": UserRole.ADMIN
        },
        {
            "username": "operator",
            "password": "operator123",
            "email": "operator@ldplayer.local",
            "full_name": "System Operator",
            "role": UserRole.OPERATOR
        },
        {
            "username": "viewer",
            "password": "viewer123",
            "email": "viewer@ldplayer.local",
            "full_name": "System Viewer",
            "role": UserRole.VIEWER
        }
    ]
    
    for user_data in default_users:
        password = user_data.pop("password")
        create_user(
            username=user_data["username"],
            password=password,
            email=user_data.get("email"),
            full_name=user_data.get("full_name"),
            role=user_data["role"]
        )
    
    logger.logger.info(f"Initialized {len(default_users)} default users")


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль против хэша."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Получить хэш пароля."""
    return pwd_context.hash(password)


# ============================================================================
# USER MANAGEMENT
# ============================================================================

def get_user(username: str) -> Optional[UserInDB]:
    """Получить пользователя по имени."""
    return USERS_DB.get(username)


def create_user(
    username: str,
    password: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    role: UserRole = UserRole.VIEWER
) -> UserInDB:
    """Создать нового пользователя."""
    if username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{username}' already exists"
        )
    
    hashed_password = get_password_hash(password)
    user = UserInDB(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=hashed_password,
        created_at=datetime.now(),
        disabled=False
    )
    
    USERS_DB[username] = user
    logger.logger.info(f"User created: {username} (role: {role})")
    return user


def list_users() -> List[User]:
    """Получить список всех пользователей (без паролей)."""
    return [
        User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            disabled=user.disabled,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in USERS_DB.values()
    ]


def delete_user(username: str) -> bool:
    """Удалить пользователя."""
    if username not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    if username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin user"
        )
    
    del USERS_DB[username]
    logger.logger.info(f"User deleted: {username}")
    return True


def update_user_role(username: str, new_role: UserRole) -> UserInDB:
    """Обновить роль пользователя."""
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    user.role = new_role
    USERS_DB[username] = user
    logger.logger.info(f"User role updated: {username} -> {new_role}")
    return user


def disable_user(username: str, disabled: bool = True) -> UserInDB:
    """Отключить/включить пользователя."""
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    if username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot disable admin user"
        )
    
    user.disabled = disabled
    USERS_DB[username] = user
    status_text = "disabled" if disabled else "enabled"
    logger.logger.info(f"User {status_text}: {username}")
    return user


# ============================================================================
# AUTHENTICATION
# ============================================================================

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Аутентифицировать пользователя."""
    user = get_user(username)
    if not user:
        logger.logger.warning(f"Authentication failed: user not found - {username}")
        return None
    
    if user.disabled:
        logger.logger.warning(f"Authentication failed: user disabled - {username}")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.logger.warning(f"Authentication failed: invalid password - {username}")
        return None
    
    # Update last login
    user.last_login = datetime.now()
    USERS_DB[username] = user
    
    logger.logger.info(f"User authenticated: {username}")
    return user


# ============================================================================
# JWT TOKEN OPERATIONS
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создать JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создать JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Декодировать и валидировать JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing username",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(
            username=username,
            role=UserRole(role) if role else None,
            exp=exp
        )
    
    except jwt.ExpiredSignatureError:
        logger.logger.warning("Token validation failed: expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except jwt.PyJWTError as e:
        logger.logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_tokens(user: UserInDB) -> Token:
    """Генерировать access и refresh токены для пользователя."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": user.username,
        "role": user.role.value
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(data=token_data)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # В секундах
        refresh_token=refresh_token
    )


def refresh_access_token(refresh_token: str) -> Token:
    """Обновить access token используя refresh token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Проверить тип токена
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Проверить существование пользователя
        user = get_user(username)
        if not user or user.disabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Генерировать новые токены
        logger.logger.info(f"Token refreshed for user: {username}")
        return generate_tokens(user)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except jwt.PyJWTError as e:
        logger.logger.error(f"Refresh token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# AUTHORIZATION (RBAC)
# ============================================================================

def check_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """Проверить, есть ли у пользователя необходимые права."""
    role_hierarchy = {
        UserRole.ADMIN: 3,
        UserRole.OPERATOR: 2,
        UserRole.VIEWER: 1
    }
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


def require_role(user: UserInDB, required_role: UserRole):
    """Проверить роль пользователя, выбросить исключение если недостаточно прав."""
    if not check_permission(user.role, required_role):
        logger.logger.warning(
            f"Permission denied: {user.username} (role: {user.role}) "
            f"requires {required_role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {required_role}"
        )


# ============================================================================
# INITIALIZATION
# ============================================================================

# Инициализировать пользователей при импорте модуля
init_default_users()
