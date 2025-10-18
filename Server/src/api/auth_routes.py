"""
Authentication API Endpoints

Endpoints:
- POST /auth/login - User login
- POST /auth/refresh - Refresh access token
- POST /auth/logout - User logout (client-side token removal)
- GET /auth/me - Get current user info
- POST /auth/register - Register new user (admin only)
- GET /auth/users - List all users (admin only)
- DELETE /auth/users/{username} - Delete user (admin only)
- PUT /auth/users/{username}/role - Update user role (admin only)
- PUT /auth/users/{username}/disable - Disable user (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List

from ..core.models import (
    User, UserCreate, UserLogin, Token, TokenRefresh,
    UserRole, UserInDB
)
from ..utils.auth import (
    authenticate_user, generate_tokens, decode_token,
    refresh_access_token, get_user, create_user,
    list_users, delete_user, update_user_role, disable_user,
    require_role
)
from ..utils.logger import get_logger, LogCategory
from ..utils.detailed_logging import log_authentication_attempt, log_permission_check
from ..utils.constants import ErrorMessage  # ✅ NEW
from ..utils.validators import validate_email, validate_string_length  # ✅ NEW


# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(LogCategory.API)

# ✅ FIX: OAuth2PasswordBearer должен содержать только PATH без /api префикса
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ============================================================================
# DEPENDENCY: GET CURRENT USER
# ============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Получить текущего аутентифицированного пользователя из JWT token.
    
    Используется как dependency в protected endpoints.
    """
    token_data = decode_token(token)
    user = get_user(token_data.username)
    
    if user is None:
        logger.logger.warning(f"User not found: {token_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.disabled:
        logger.logger.warning(f"User disabled: {token_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Alias для get_current_user (для совместимости).
    """
    return current_user


# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    **Вход пользователя в систему.**
    
    Принимает username и password, возвращает JWT токены.
    
    **Учётные записи по умолчанию:**
    - admin / admin123 (роль: admin)
    - operator / operator123 (роль: operator)
    - viewer / viewer123 (роль: viewer)
    
    **Возвращает:**
    - access_token: JWT токен для API запросов (срок: 30 минут)
    - refresh_token: Токен для обновления access_token (срок: 7 дней)
    - token_type: "bearer"
    - expires_in: Время жизни access_token в секундах
    
    **Errors:**
    - 401: Invalid credentials
    """
    # Попытка получить IP клиента и User-Agent для логирования
    # ✅ REMOVED: Неиспользуемый импорт Request
    client_ip = "unknown"
    user_agent = "unknown"
    
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        # Логируем FAILED попытку входа
        log_authentication_attempt({
            "username": credentials.username,
            "success": False,
            "ip": client_ip,
            "user_agent": user_agent,
            "reason": "Invalid username or password"
        })
        
        logger.logger.warning(f"❌ Login FAILED: {credentials.username} from {client_ip}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = generate_tokens(user)
    
    # Логируем SUCCESSFUL попытку входа
    log_authentication_attempt({
        "username": user.username,
        "success": True,
        "ip": client_ip,
        "user_agent": user_agent
    })
    
    logger.logger.info(f"✅ Login SUCCESS: {user.username} (role: {user.role}) from {client_ip}")
    
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """
    **Обновить access token используя refresh token.**
    
    Когда access token истекает (через 30 минут), используйте
    refresh token для получения нового access token без повторного ввода пароля.
    
    **Request Body:**
    ```json
    {
        "refresh_token": "your-refresh-token"
    }
    ```
    
    **Возвращает:** Новые access и refresh токены
    
    **Errors:**
    - 401: Invalid or expired refresh token
    """
    try:
        new_tokens = refresh_access_token(token_data.refresh_token)
        logger.logger.info("Access token refreshed")
        return new_tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_active_user)):
    """
    **Выход пользователя из системы.**
    
    В JWT-based authentication logout происходит на клиенте
    (удаление токена из storage). Сервер только логирует событие.
    
    **Требует:** Valid access token
    
    **Note:** Для полноценного logout нужно:
    1. Удалить access_token из client storage
    2. Удалить refresh_token из client storage
    3. (Опционально) Добавить токен в blacklist на сервере
    """
    logger.logger.info(f"User logged out: {current_user.username}")
    return {"message": "Successfully logged out"}


# ============================================================================
# PROTECTED ENDPOINTS (Authentication required)
# ============================================================================

@router.get("/me", response_model=User)
async def get_me(current_user: UserInDB = Depends(get_current_active_user)):
    """
    **Получить информацию о текущем пользователе.**
    
    Возвращает профиль аутентифицированного пользователя.
    
    **Требует:** Valid access token
    
    **Возвращает:**
    - username
    - email
    - full_name
    - role (admin/operator/viewer)
    - disabled
    - created_at
    - last_login
    """
    return User(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        disabled=current_user.disabled,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


# ============================================================================
# ADMIN-ONLY ENDPOINTS (Requires admin role)
# ============================================================================

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    **Зарегистрировать нового пользователя.**
    
    Только администраторы могут создавать новых пользователей.
    
    **Требует:** Admin role
    
    **Request Body:**
    ```json
    {
        "username": "newuser",
        "password": "password123",
        "email": "user@example.com",
        "full_name": "New User",
        "role": "viewer"
    }
    ```
    
    **Roles:**
    - admin: Полный доступ
    - operator: Управление эмуляторами
    - viewer: Только просмотр
    
    **Errors:**
    - 400: User already exists
    - 403: Insufficient permissions (not admin)
    """
    # Check admin permission
    require_role(current_user, UserRole.ADMIN)
    
    # Create user
    new_user = create_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    logger.logger.info(f"New user registered by {current_user.username}: {new_user.username}")
    
    return User(
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        disabled=new_user.disabled,
        created_at=new_user.created_at,
        last_login=new_user.last_login
    )


@router.get("/users", response_model=List[User])
async def get_users(current_user: UserInDB = Depends(get_current_active_user)):
    """
    **Получить список всех пользователей.**
    
    Только администраторы могут просматривать список пользователей.
    
    **Требует:** Admin role
    
    **Возвращает:** Список всех пользователей (без паролей)
    
    **Errors:**
    - 403: Insufficient permissions (not admin)
    """
    require_role(current_user, UserRole.ADMIN)
    return list_users()


@router.delete("/users/{username}")
async def remove_user(
    username: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    **Удалить пользователя.**
    
    Только администраторы могут удалять пользователей.
    Нельзя удалить пользователя 'admin'.
    
    **Требует:** Admin role
    
    **Errors:**
    - 403: Insufficient permissions or trying to delete admin
    - 404: User not found
    """
    require_role(current_user, UserRole.ADMIN)
    
    delete_user(username)
    logger.logger.info(f"User deleted by {current_user.username}: {username}")
    
    return {"message": f"User '{username}' deleted successfully"}


@router.put("/users/{username}/role", response_model=User)
async def change_user_role(
    username: str,
    new_role: UserRole,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    **Изменить роль пользователя.**
    
    Только администраторы могут менять роли.
    
    **Требует:** Admin role
    
    **Path Parameters:**
    - username: Имя пользователя
    
    **Query Parameters:**
    - new_role: admin | operator | viewer
    
    **Errors:**
    - 403: Insufficient permissions
    - 404: User not found
    """
    require_role(current_user, UserRole.ADMIN)
    
    updated_user = update_user_role(username, new_role)
    logger.logger.info(
        f"User role changed by {current_user.username}: "
        f"{username} -> {new_role}"
    )
    
    return User(
        username=updated_user.username,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role,
        disabled=updated_user.disabled,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login
    )


@router.put("/users/{username}/disable", response_model=User)
async def disable_user_account(
    username: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    **Отключить аккаунт пользователя.**
    
    Только администраторы могут отключать аккаунты.
    Нельзя отключить пользователя 'admin'.
    
    **Требует:** Admin role
    
    **Errors:**
    - 403: Insufficient permissions or trying to disable admin
    - 404: User not found
    """
    require_role(current_user, UserRole.ADMIN)
    
    updated_user = disable_user(username)
    logger.logger.info(f"User disabled by {current_user.username}: {username}")
    
    return User(
        username=updated_user.username,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role,
        disabled=updated_user.disabled,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login
    )
