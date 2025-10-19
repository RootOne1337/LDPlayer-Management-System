"""
🔥 СУПЕР-ЛОГИРОВАНИЕ ВСЕХ ОПЕРАЦИЙ
Middleware для детального логирования всех HTTP запросов, WebSocket соединений и операций
"""

import time
import json
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..utils.logger import get_logger, LogCategory

logger = get_logger(__name__)


class Colors:
    """ANSI цвета для консоли"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SuperLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для детального логирования всех операций
    
    Логирует:
    - HTTP запросы (метод, путь, заголовки, тело)
    - HTTP ответы (статус, время выполнения, размер)
    - Ошибки и исключения
    - Производительность (время обработки)
    """
    
    def __init__(self, app: ASGIApp, log_request_body: bool = False, log_response_body: bool = False):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.request_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с логированием"""
        
        # Увеличиваем счетчик
        self.request_count += 1
        request_id = self.request_count
        
        # Время начала
        start_time = time.time()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Получаем данные запроса
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Определяем цвет по методу
        method_color = {
            "GET": Colors.CYAN,
            "POST": Colors.GREEN,
            "PUT": Colors.YELLOW,
            "DELETE": Colors.RED,
            "PATCH": Colors.YELLOW
        }.get(method, Colors.BLUE)
        
        # Логируем входящий запрос
        print(f"\n{Colors.BLUE}{'─' * 100}{Colors.ENDC}")
        print(f"{Colors.BOLD}[{timestamp}] 📥 ВХОДЯЩИЙ ЗАПРОС #{request_id}{Colors.ENDC}")
        print(f"{method_color}{Colors.BOLD}{method}{Colors.ENDC} {Colors.CYAN}{path}{Colors.ENDC}")
        print(f"  {Colors.CYAN}├─{Colors.ENDC} Клиент: {client_ip}")
        print(f"  {Colors.CYAN}├─{Colors.ENDC} User-Agent: {user_agent[:80]}")
        
        if query_params:
            print(f"  {Colors.CYAN}├─{Colors.ENDC} Query параметры: {Colors.YELLOW}{query_params}{Colors.ENDC}")
        
        # Логируем тело запроса (если включено)
        if self.log_request_body and method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    try:
                        body_json = json.loads(body.decode())
                        # Скрываем пароли
                        if "password" in body_json:
                            body_json["password"] = "***"
                        print(f"  {Colors.CYAN}├─{Colors.ENDC} Тело запроса: {Colors.YELLOW}{json.dumps(body_json, ensure_ascii=False)[:200]}{Colors.ENDC}")
                    except:
                        print(f"  {Colors.CYAN}├─{Colors.ENDC} Тело запроса: {len(body)} байт")
                
                # Восстанавливаем тело для дальнейшей обработки
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            except Exception as e:
                logger.warning(f"Не удалось прочитать тело запроса: {e}")
        
        # Обработка запроса
        try:
            response = await call_next(request)
            
            # Время выполнения
            duration = (time.time() - start_time) * 1000  # в миллисекундах
            
            # Определяем цвет статуса
            status_code = response.status_code
            if status_code < 300:
                status_color = Colors.GREEN
                status_icon = "✅"
            elif status_code < 400:
                status_color = Colors.CYAN
                status_icon = "↪️"
            elif status_code < 500:
                status_color = Colors.YELLOW
                status_icon = "⚠️"
            else:
                status_color = Colors.RED
                status_icon = "❌"
            
            # Логируем ответ
            print(f"  {Colors.CYAN}└─{Colors.ENDC} {status_icon} Статус: {status_color}{Colors.BOLD}{status_code}{Colors.ENDC}")
            print(f"  {Colors.CYAN}   {Colors.ENDC} ⏱️  Время: {Colors.BOLD}{duration:.2f}ms{Colors.ENDC}")
            
            # Производительность
            if duration < 100:
                perf_color = Colors.GREEN
                perf_text = "БЫСТРО"
            elif duration < 500:
                perf_color = Colors.YELLOW
                perf_text = "НОРМАЛЬНО"
            else:
                perf_color = Colors.RED
                perf_text = "МЕДЛЕННО"
            
            print(f"  {Colors.CYAN}   {Colors.ENDC} 🚀 Производительность: {perf_color}{perf_text}{Colors.ENDC}")
            
            # Добавляем заголовки для отладки
            response.headers["X-Request-ID"] = str(request_id)
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"
            
            return response
            
        except Exception as e:
            # Логируем ошибку
            duration = (time.time() - start_time) * 1000
            
            print(f"  {Colors.CYAN}└─{Colors.ENDC} {Colors.RED}❌ ОШИБКА{Colors.ENDC}")
            print(f"  {Colors.RED}   ├─{Colors.ENDC} Тип: {type(e).__name__}")
            print(f"  {Colors.RED}   ├─{Colors.ENDC} Сообщение: {str(e)}")
            print(f"  {Colors.RED}   └─{Colors.ENDC} Время до ошибки: {duration:.2f}ms")
            
            logger.error(f"Ошибка обработки запроса: {e}", extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "duration_ms": duration,
                "client_ip": client_ip
            })
            
            # Перебрасываем исключение
            raise


class WebSocketLoggingMiddleware:
    """Логирование WebSocket соединений"""
    
    @staticmethod
    def log_connection(client_id: str, action: str, details: str = ""):
        """Логирование WebSocket событий"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        action_icons = {
            "connect": "🔌",
            "disconnect": "🔚",
            "message": "💬",
            "error": "❌",
            "ping": "📡"
        }
        
        action_colors = {
            "connect": Colors.GREEN,
            "disconnect": Colors.YELLOW,
            "message": Colors.CYAN,
            "error": Colors.RED,
            "ping": Colors.BLUE
        }
        
        icon = action_icons.get(action, "📨")
        color = action_colors.get(action, Colors.CYAN)
        
        print(f"\n{Colors.BLUE}{'─' * 100}{Colors.ENDC}")
        print(f"{Colors.BOLD}[{timestamp}] {icon} WebSocket {action.upper()}{Colors.ENDC}")
        print(f"  {Colors.CYAN}├─{Colors.ENDC} Клиент: {color}{client_id}{Colors.ENDC}")
        if details:
            print(f"  {Colors.CYAN}└─{Colors.ENDC} Детали: {details}")


class OperationLoggingMiddleware:
    """Логирование операций с эмуляторами и станциями"""
    
    @staticmethod
    def log_operation(operation_type: str, target: str, status: str, duration: float = 0, details: str = ""):
        """Логирование операции"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        operation_icons = {
            "start": "▶️",
            "stop": "⏹️",
            "restart": "🔄",
            "connect": "🔗",
            "disconnect": "🔌",
            "check": "🔍",
            "update": "♻️"
        }
        
        status_colors = {
            "success": Colors.GREEN,
            "error": Colors.RED,
            "pending": Colors.YELLOW,
            "running": Colors.CYAN
        }
        
        icon = operation_icons.get(operation_type, "⚙️")
        color = status_colors.get(status, Colors.CYAN)
        
        print(f"\n{Colors.BLUE}{'─' * 100}{Colors.ENDC}")
        print(f"{Colors.BOLD}[{timestamp}] {icon} ОПЕРАЦИЯ: {operation_type.upper()}{Colors.ENDC}")
        print(f"  {Colors.CYAN}├─{Colors.ENDC} Цель: {Colors.BOLD}{target}{Colors.ENDC}")
        print(f"  {Colors.CYAN}├─{Colors.ENDC} Статус: {color}{status.upper()}{Colors.ENDC}")
        if duration > 0:
            print(f"  {Colors.CYAN}├─{Colors.ENDC} Длительность: {Colors.BOLD}{duration:.2f}ms{Colors.ENDC}")
        if details:
            print(f"  {Colors.CYAN}└─{Colors.ENDC} Детали: {details}")


class DatabaseLoggingMiddleware:
    """Логирование операций с базой данных"""
    
    @staticmethod
    def log_query(query_type: str, table: str, duration: float = 0, rows_affected: int = 0):
        """Логирование SQL запроса"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        query_icons = {
            "SELECT": "🔍",
            "INSERT": "➕",
            "UPDATE": "♻️",
            "DELETE": "➖"
        }
        
        icon = query_icons.get(query_type, "📊")
        
        print(f"  {Colors.CYAN}[{timestamp}]{Colors.ENDC} {icon} {Colors.YELLOW}SQL{Colors.ENDC}: {query_type} FROM {Colors.BOLD}{table}{Colors.ENDC}")
        if duration > 0:
            print(f"    {Colors.CYAN}├─{Colors.ENDC} Время: {duration:.2f}ms")
        if rows_affected > 0:
            print(f"    {Colors.CYAN}└─{Colors.ENDC} Строк затронуто: {rows_affected}")


# Экспорт всех middleware
__all__ = [
    'SuperLoggingMiddleware',
    'WebSocketLoggingMiddleware', 
    'OperationLoggingMiddleware',
    'DatabaseLoggingMiddleware'
]
