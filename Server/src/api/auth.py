"""
Authentication Endpoints
Endpoints для входа и управления JWT токенами
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from ..utils.jwt_auth import (
    JWTManager, User, Token, UserLogin,
    get_current_user, get_current_admin
)
from ..utils.logger import get_logger

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)

jwt_manager = JWTManager()
logger = get_logger(__name__)


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Get JWT token with username and password"
)
async def login(credentials: UserLogin):
    """
    Вход и получение JWT токена
    
    **Требуемые поля:**
    - username: str (по умолчанию "admin")
    - password: str (по умолчанию "admin")
    
    **Response:**
    - access_token: JWT токен
    - token_type: "bearer"
    - expires_in: время жизни в секундах
    """
    try:
        token_response = jwt_manager.login(
            username=credentials.username,
            password=credentials.password
        )
        
        logger.log_operation(
            operation_type="auth",
            category="security",
            message=f"User '{credentials.username}' logged in successfully",
            additional_data={"username": credentials.username}
        )
        
        return token_response
        
    except HTTPException as e:
        logger.log_operation(
            operation_type="auth",
            category="security",
            message=f"Failed login attempt for user '{credentials.username}': {e.detail}",
            additional_data={"username": credentials.username, "error": e.detail},
            status="error"
        )
        raise


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh Token",
    description="Get new JWT token"
)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Обновить JWT токен
    
    **Security:** Требует действующий JWT токен
    """
    token_response = jwt_manager.login(
        username=current_user.username,
        scopes=current_user.scopes
    )
    
    logger.log_operation(
        operation_type="auth",
        category="security",
        message=f"User '{current_user.username}' refreshed token",
        additional_data={"user_id": current_user.user_id}
    )
    
    return token_response


@router.get(
    "/me",
    response_model=User,
    summary="Get Current User",
    description="Get information about the current authenticated user"
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Получить информацию о текущем пользователе
    
    **Security:** Требует JWT токен
    
    **Response:**
    - username: имя пользователя
    - user_id: уникальный идентификатор
    - active: статус активности
    - scopes: список разрешений
    """
    return current_user


@router.get(
    "/admin/check",
    response_model=dict,
    summary="Check Admin Rights",
    description="Check if current user has admin rights"
)
async def check_admin(current_user: User = Depends(get_current_admin)):
    """
    Проверить права администратора
    
    **Security:** Требует JWT токен с правами администратора
    
    **Response:**
    - is_admin: bool - есть ли права
    - username: имя пользователя
    - scopes: список разрешений
    """
    return {
        "is_admin": True,
        "username": current_user.username,
        "scopes": current_user.scopes
    }


@router.post(
    "/verify",
    response_model=dict,
    summary="Verify Token",
    description="Verify if JWT token is valid"
)
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    Проверить валидность токена
    
    **Security:** Требует JWT токен
    
    **Response:**
    - valid: bool - токен валиден
    - username: имя пользователя
    - expires_at: время истечения
    """
    return {
        "valid": True,
        "username": current_user.username,
        "user_id": current_user.user_id,
        "scopes": current_user.scopes,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    print("✅ Authentication endpoints module loaded")
