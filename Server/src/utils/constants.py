"""
Constants - все магические строки и значения в одном месте

Используется для:
- Статусов эмуляторов и операций
- Типов операций
- Кодов ошибок
- Сообщений
"""

# ============================================================================
# EMULATOR STATUSES
# ============================================================================

class EmulatorStatus:
    """Статусы эмулятора"""
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    REBOOTING = "REBOOTING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"
    STARTING = "STARTING"
    STOPPING = "STOPPING"
    
    ALL = [RUNNING, STOPPED, REBOOTING, ERROR, UNKNOWN, STARTING, STOPPING]


class WorkstationStatus:
    """Статусы рабочей станции"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    UNREACHABLE = "UNREACHABLE"
    ERROR = "ERROR"
    
    ALL = [ONLINE, OFFLINE, UNREACHABLE, ERROR]


# ============================================================================
# OPERATION STATUSES
# ============================================================================

class OperationStatus:
    """Статусы операций"""
    PENDING = "PENDING"      # Ожидает выполнения
    RUNNING = "RUNNING"      # Выполняется
    SUCCESS = "SUCCESS"      # Успешно завершена
    FAILED = "FAILED"        # Ошибка
    CANCELLED = "CANCELLED"  # Отменена
    TIMEOUT = "TIMEOUT"      # Таймаут
    
    ALL = [PENDING, RUNNING, SUCCESS, FAILED, CANCELLED, TIMEOUT]
    
    IN_PROGRESS = [PENDING, RUNNING]
    FINISHED = [SUCCESS, FAILED, CANCELLED, TIMEOUT]


# ============================================================================
# OPERATION TYPES
# ============================================================================

class OperationType:
    """Типы операций"""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    DELETE = "delete"
    RENAME = "rename"
    CONFIG = "config"
    SCREENSHOT = "screenshot"
    
    ALL = [START, STOP, RESTART, DELETE, RENAME, CONFIG, SCREENSHOT]


# ============================================================================
# ERROR CODES
# ============================================================================

class ErrorCode:
    """Коды ошибок"""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    TIMEOUT = 408
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class ErrorMessage:
    """Сообщения об ошибках"""
    EMULATOR_NOT_FOUND = "Emulator not found"
    WORKSTATION_NOT_FOUND = "Workstation not found"
    OPERATION_NOT_FOUND = "Operation not found"
    
    EMULATOR_ALREADY_RUNNING = "Emulator is already running"
    EMULATOR_ALREADY_STOPPED = "Emulator is already stopped"
    EMULATOR_OPERATION_IN_PROGRESS = "Another operation is already in progress"
    
    INVALID_OPERATION_TYPE = "Invalid operation type"
    INVALID_STATUS = "Invalid status value"
    INVALID_NAME = "Invalid name format"
    INVALID_CONFIG = "Invalid configuration"
    
    WORKSTATION_UNREACHABLE = "Workstation is unreachable"
    LDPLAYER_NOT_INSTALLED = "LDPlayer is not installed on workstation"
    OPERATION_TIMEOUT = "Operation timed out"
    OPERATION_FAILED = "Operation failed"
    
    INVALID_REQUEST = "Invalid request parameters"
    MISSING_PARAMETER = "Missing required parameter: {}"
    INVALID_PARAMETER_TYPE = "Invalid parameter type: {}"
    
    INTERNAL_ERROR = "Internal server error"
    UNKNOWN_ERROR = "Unknown error occurred"


# ============================================================================
# API LIMITS AND DEFAULTS
# ============================================================================

class APIDefaults:
    """Значения по умолчанию для API"""
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 100
    MAX_LIMIT = 1000
    MIN_LIMIT = 1
    
    OPERATION_TIMEOUT_SECONDS = 300  # 5 минут
    OPERATION_CHECK_INTERVAL = 2      # Проверять каждые 2 секунды
    
    MAX_EMULATORS_PER_WORKSTATION = 10
    MAX_WORKSTATIONS = 50


# ============================================================================
# LOGGING MESSAGES
# ============================================================================

class LogMessage:
    """Сообщения для логирования"""
    # Операции
    OPERATION_STARTED = "Operation {} started: {}"
    OPERATION_COMPLETED = "Operation {} completed: {}"
    OPERATION_FAILED = "Operation {} failed: {}"
    OPERATION_TIMEOUT = "Operation {} timed out after {} seconds"
    
    # Эмуляторы
    EMULATOR_STARTED = "Emulator {} started successfully"
    EMULATOR_STOPPED = "Emulator {} stopped successfully"
    EMULATOR_RESTARTED = "Emulator {} restarted successfully"
    EMULATOR_DELETED = "Emulator {} deleted successfully"
    EMULATOR_NOT_RESPONDING = "Emulator {} is not responding"
    
    # Рабочие станции
    WORKSTATION_CONNECTED = "Workstation {} connected"
    WORKSTATION_DISCONNECTED = "Workstation {} disconnected"
    WORKSTATION_ERROR = "Workstation {} error: {}"
    
    # Аутентификация
    AUTH_SUCCESS = "User {} authenticated successfully"
    AUTH_FAILED = "Authentication failed for user {}"
    TOKEN_INVALID = "Invalid or expired token"
    
    # API
    API_REQUEST = "API Request: {} {}"
    API_RESPONSE = "API Response: {} {} ({}ms)"
    API_ERROR = "API Error: {} {}: {}"


# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationRules:
    """Правила валидации"""
    # Длины
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 50
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # Паттерны
    NAME_PATTERN = r"^[a-zA-Z0-9_-]+$"  # Только буквы, цифры, подчеркивание, дефис


# ============================================================================
# RESPONSE TEMPLATES
# ============================================================================

class ResponseTemplate:
    """Шаблоны ответов"""
    SUCCESS = {
        "success": True,
        "data": None,
        "message": "OK",
    }
    
    ERROR = {
        "success": False,
        "error": None,
        "message": "Error occurred",
        "details": None,
    }
    
    OPERATION_RESPONSE = {
        "operation_id": None,
        "type": None,
        "status": None,
        "created_at": None,
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
    }


# ============================================================================
# FILE PATHS AND CONFIGS
# ============================================================================

class FilePath:
    """Пути к файлам и конфигам"""
    CONFIG_DIR = "configs"
    LOG_DIR = "logs"
    BACKUP_DIR = "backups"
    TEMPLATES_DIR = "configs/templates"


# ============================================================================
# HEADERS AND CONTENT TYPES
# ============================================================================

class ContentType:
    """Content-Type значения"""
    JSON = "application/json"
    PLAIN_TEXT = "text/plain"
    HTML = "text/html"
    FORM_DATA = "application/x-www-form-urlencoded"


class Header:
    """HTTP headers"""
    AUTHORIZATION = "Authorization"
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"
    ACCEPT = "Accept"
    USER_AGENT = "User-Agent"
    X_REQUEST_ID = "X-Request-ID"
