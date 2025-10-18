"""
Comprehensive Exception Hierarchy for LDPlayer Management System

This module defines all custom exceptions used throughout the application.
Specific exception types allow for better error handling and debugging.
"""

from typing import Optional, Any


# ============================================================================
# BASE EXCEPTIONS
# ============================================================================

class LDPlayerException(Exception):
    """Base exception for all LDPlayer Management System errors."""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", 
                 details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for API response."""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details
        }


# ============================================================================
# CONFIGURATION EXCEPTIONS
# ============================================================================

class ConfigException(LDPlayerException):
    """Exception raised for configuration errors."""
    code = "CONFIG_ERROR"


class ConfigLoadError(ConfigException):
    """Failed to load configuration file."""
    code = "CONFIG_LOAD_ERROR"


class ConfigValidationError(ConfigException):
    """Configuration validation failed."""
    code = "CONFIG_VALIDATION_ERROR"


class MissingConfigError(ConfigException):
    """Required configuration is missing."""
    code = "MISSING_CONFIG_ERROR"


class InvalidConfigValue(ConfigException):
    """Configuration value is invalid."""
    code = "INVALID_CONFIG_VALUE"


# ============================================================================
# WORKSTATION EXCEPTIONS
# ============================================================================

class WorkstationException(LDPlayerException):
    """Base exception for workstation-related errors."""
    code = "WORKSTATION_ERROR"


class WorkstationNotFoundError(WorkstationException):
    """Workstation not found."""
    code = "WORKSTATION_NOT_FOUND"


class WorkstationConnectionError(WorkstationException):
    """Failed to connect to workstation."""
    code = "WORKSTATION_CONNECTION_ERROR"


class WorkstationOfflineError(WorkstationException):
    """Workstation is offline or unreachable."""
    code = "WORKSTATION_OFFLINE"


class WorkstationAuthenticationError(WorkstationException):
    """Authentication failed for workstation."""
    code = "WORKSTATION_AUTH_ERROR"


class WorkstationCommandError(WorkstationException):
    """Failed to execute command on workstation."""
    code = "WORKSTATION_COMMAND_ERROR"


class WorkstationTimeoutError(WorkstationException):
    """Command on workstation timed out."""
    code = "WORKSTATION_TIMEOUT"


class InvalidWorkstationConfig(WorkstationException):
    """Invalid workstation configuration."""
    code = "INVALID_WORKSTATION_CONFIG"


# ============================================================================
# EMULATOR EXCEPTIONS
# ============================================================================

class EmulatorException(LDPlayerException):
    """Base exception for emulator-related errors."""
    code = "EMULATOR_ERROR"


class EmulatorNotFoundError(EmulatorException):
    """Emulator not found."""
    code = "EMULATOR_NOT_FOUND"


class EmulatorAlreadyExists(EmulatorException):
    """Emulator already exists."""
    code = "EMULATOR_ALREADY_EXISTS"


class EmulatorStartError(EmulatorException):
    """Failed to start emulator."""
    code = "EMULATOR_START_ERROR"


class EmulatorStopError(EmulatorException):
    """Failed to stop emulator."""
    code = "EMULATOR_STOP_ERROR"


class EmulatorDeleteError(EmulatorException):
    """Failed to delete emulator."""
    code = "EMULATOR_DELETE_ERROR"


class EmulatorRenameError(EmulatorException):
    """Failed to rename emulator."""
    code = "EMULATOR_RENAME_ERROR"


class EmulatorStatusError(EmulatorException):
    """Failed to get emulator status."""
    code = "EMULATOR_STATUS_ERROR"


class InvalidEmulatorConfig(EmulatorException):
    """Invalid emulator configuration."""
    code = "INVALID_EMULATOR_CONFIG"


class EmulatorScanError(EmulatorException):
    """Failed to scan for emulators."""
    code = "EMULATOR_SCAN_ERROR"


# ============================================================================
# OPERATION EXCEPTIONS
# ============================================================================

class OperationException(LDPlayerException):
    """Base exception for operation-related errors."""
    code = "OPERATION_ERROR"


class OperationNotFoundError(OperationException):
    """Operation not found."""
    code = "OPERATION_NOT_FOUND"


class OperationAlreadyRunning(OperationException):
    """Operation is already running."""
    code = "OPERATION_ALREADY_RUNNING"


class OperationFailedError(OperationException):
    """Operation failed."""
    code = "OPERATION_FAILED"


class OperationTimeoutError(OperationException):
    """Operation timed out."""
    code = "OPERATION_TIMEOUT"


class OperationCancelledError(OperationException):
    """Operation was cancelled."""
    code = "OPERATION_CANCELLED"


class InvalidOperationType(OperationException):
    """Invalid operation type."""
    code = "INVALID_OPERATION_TYPE"


# ============================================================================
# VALIDATION EXCEPTIONS
# ============================================================================

class ValidationException(LDPlayerException):
    """Base exception for validation errors."""
    code = "VALIDATION_ERROR"


class InvalidInputError(ValidationException):
    """Invalid input provided."""
    code = "INVALID_INPUT"


class InvalidEmailError(ValidationException):
    """Invalid email address."""
    code = "INVALID_EMAIL"


class InvalidIPAddressError(ValidationException):
    """Invalid IP address."""
    code = "INVALID_IP_ADDRESS"


class InvalidPortError(ValidationException):
    """Invalid port number."""
    code = "INVALID_PORT"


class InvalidPasswordError(ValidationException):
    """Invalid password (too weak, wrong format, etc)."""
    code = "INVALID_PASSWORD"


class MissingFieldError(ValidationException):
    """Required field is missing."""
    code = "MISSING_FIELD"


class FieldTypeError(ValidationException):
    """Field has invalid type."""
    code = "FIELD_TYPE_ERROR"


# ============================================================================
# AUTHENTICATION & AUTHORIZATION EXCEPTIONS
# ============================================================================

class AuthException(LDPlayerException):
    """Base exception for authentication/authorization errors."""
    code = "AUTH_ERROR"


class AuthenticationError(AuthException):
    """Authentication failed."""
    code = "AUTHENTICATION_ERROR"


class InvalidCredentialsError(AuthException):
    """Invalid username or password."""
    code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthException):
    """Authentication token has expired."""
    code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthException):
    """Token is invalid or malformed."""
    code = "INVALID_TOKEN"


class UnauthorizedError(AuthException):
    """User is not authorized for this action."""
    code = "UNAUTHORIZED"


class InsufficientPermissionsError(AuthException):
    """User doesn't have required permissions."""
    code = "INSUFFICIENT_PERMISSIONS"


# ============================================================================
# DATABASE EXCEPTIONS
# ============================================================================

class DatabaseException(LDPlayerException):
    """Base exception for database errors."""
    code = "DATABASE_ERROR"


class DatabaseConnectionError(DatabaseException):
    """Failed to connect to database."""
    code = "DATABASE_CONNECTION_ERROR"


class DatabaseQueryError(DatabaseException):
    """Database query failed."""
    code = "DATABASE_QUERY_ERROR"


class DatabaseIntegrityError(DatabaseException):
    """Database integrity constraint violation."""
    code = "DATABASE_INTEGRITY_ERROR"


class RecordNotFoundError(DatabaseException):
    """Record not found in database."""
    code = "RECORD_NOT_FOUND"


class DuplicateRecordError(DatabaseException):
    """Duplicate record already exists."""
    code = "DUPLICATE_RECORD"


# ============================================================================
# FILE SYSTEM EXCEPTIONS
# ============================================================================

class FileSystemException(LDPlayerException):
    """Base exception for file system errors."""
    code = "FILE_SYSTEM_ERROR"


class FileNotFoundError(FileSystemException):
    """File not found."""
    code = "FILE_NOT_FOUND"


class DirectoryNotFoundError(FileSystemException):
    """Directory not found."""
    code = "DIRECTORY_NOT_FOUND"


class FilePermissionError(FileSystemException):
    """Permission denied for file operation."""
    code = "FILE_PERMISSION_ERROR"


class FileReadError(FileSystemException):
    """Failed to read file."""
    code = "FILE_READ_ERROR"


class FileWriteError(FileSystemException):
    """Failed to write file."""
    code = "FILE_WRITE_ERROR"


class FileDeleteError(FileSystemException):
    """Failed to delete file."""
    code = "FILE_DELETE_ERROR"


class InvalidPathError(FileSystemException):
    """Invalid file path."""
    code = "INVALID_PATH"


# ============================================================================
# NETWORK EXCEPTIONS
# ============================================================================

class NetworkException(LDPlayerException):
    """Base exception for network-related errors."""
    code = "NETWORK_ERROR"


class ConnectionRefusedError(NetworkException):
    """Connection was refused."""
    code = "CONNECTION_REFUSED"


class ConnectionTimeoutError(NetworkException):
    """Connection timed out."""
    code = "CONNECTION_TIMEOUT"


class NetworkUnreachableError(NetworkException):
    """Network is unreachable."""
    code = "NETWORK_UNREACHABLE"


class DNSResolutionError(NetworkException):
    """DNS resolution failed."""
    code = "DNS_RESOLUTION_ERROR"


class PortInUseError(NetworkException):
    """Port is already in use."""
    code = "PORT_IN_USE"


# ============================================================================
# API & HTTP EXCEPTIONS
# ============================================================================

class APIException(LDPlayerException):
    """Base exception for API errors."""
    code = "API_ERROR"


class InvalidAPIRequestError(APIException):
    """Invalid API request."""
    code = "INVALID_API_REQUEST"


class APINotFoundError(APIException):
    """API endpoint not found."""
    code = "API_NOT_FOUND"


class APIMethodNotAllowedError(APIException):
    """HTTP method not allowed."""
    code = "METHOD_NOT_ALLOWED"


class RateLimitError(APIException):
    """Rate limit exceeded."""
    code = "RATE_LIMIT_EXCEEDED"


class ServiceUnavailableError(APIException):
    """Service is temporarily unavailable."""
    code = "SERVICE_UNAVAILABLE"


# ============================================================================
# SYSTEM EXCEPTIONS
# ============================================================================

class SystemException(LDPlayerException):
    """Base exception for system-level errors."""
    code = "SYSTEM_ERROR"


class ProcessError(SystemException):
    """Failed to execute system process."""
    code = "PROCESS_ERROR"


class ProcessTimeoutError(SystemException):
    """System process timed out."""
    code = "PROCESS_TIMEOUT"


class ProcessNotFoundError(SystemException):
    """System process not found."""
    code = "PROCESS_NOT_FOUND"


class MemoryError(SystemException):
    """Insufficient memory."""
    code = "MEMORY_ERROR"


class DiskSpaceError(SystemException):
    """Insufficient disk space."""
    code = "DISK_SPACE_ERROR"


class PermissionDeniedError(SystemException):
    """Permission denied."""
    code = "PERMISSION_DENIED"


# ============================================================================
# RESOURCE EXCEPTIONS
# ============================================================================

class ResourceException(LDPlayerException):
    """Base exception for resource-related errors."""
    code = "RESOURCE_ERROR"


class ResourceNotFoundError(ResourceException):
    """Resource not found."""
    code = "RESOURCE_NOT_FOUND"


class ResourceLocked(ResourceException):
    """Resource is locked by another process."""
    code = "RESOURCE_LOCKED"


class ResourceExhausted(ResourceException):
    """Resource quota exhausted."""
    code = "RESOURCE_EXHAUSTED"


class ResourceConflict(ResourceException):
    """Resource conflict occurred."""
    code = "RESOURCE_CONFLICT"


# ============================================================================
# LOGGING & DEBUG EXCEPTIONS
# ============================================================================

class LoggingException(LDPlayerException):
    """Base exception for logging errors."""
    code = "LOGGING_ERROR"


class LogFileError(LoggingException):
    """Failed to write to log file."""
    code = "LOG_FILE_ERROR"


class LogRotationError(LoggingException):
    """Failed to rotate log file."""
    code = "LOG_ROTATION_ERROR"


# ============================================================================
# UTILS & HELPERS
# ============================================================================

def create_error_response(exc: LDPlayerException, 
                          status_code: int = 400) -> tuple[dict, int]:
    """
    Convert exception to API error response.
    
    Args:
        exc: LDPlayerException instance
        status_code: HTTP status code
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    return exc.to_dict(), status_code


def get_exception_chain(exc: Exception) -> list[str]:
    """
    Get the chain of exceptions from an exception.
    
    Args:
        exc: Exception to analyze
    
    Returns:
        List of exception names in the chain
    """
    chain = []
    current = exc
    while current is not None:
        chain.append(f"{current.__class__.__module__}.{current.__class__.__name__}")
        current = exc.__cause__
    return chain


# ============================================================================
# EXCEPTION MAPPING
# ============================================================================

EXCEPTION_TO_STATUS_CODE = {
    # 400 Bad Request
    ValidationException: 400,
    InvalidInputError: 400,
    InvalidEmailError: 400,
    InvalidIPAddressError: 400,
    InvalidPortError: 400,
    InvalidPasswordError: 400,
    MissingFieldError: 400,
    FieldTypeError: 400,
    InvalidConfigValue: 400,
    
    # 401 Unauthorized
    AuthenticationError: 401,
    InvalidCredentialsError: 401,
    TokenExpiredError: 401,
    InvalidTokenError: 401,
    
    # 403 Forbidden
    UnauthorizedError: 403,
    InsufficientPermissionsError: 403,
    
    # 404 Not Found
    WorkstationNotFoundError: 404,
    EmulatorNotFoundError: 404,
    OperationNotFoundError: 404,
    RecordNotFoundError: 404,
    FileNotFoundError: 404,
    DirectoryNotFoundError: 404,
    APINotFoundError: 404,
    ResourceNotFoundError: 404,
    
    # 409 Conflict
    EmulatorAlreadyExists: 409,
    OperationAlreadyRunning: 409,
    DuplicateRecordError: 409,
    ResourceConflict: 409,
    
    # 500 Internal Server Error
    ConfigException: 500,
    WorkstationException: 500,
    EmulatorException: 500,
    OperationException: 500,
    DatabaseException: 500,
    FileSystemException: 500,
    NetworkException: 500,
    SystemException: 500,
    ResourceException: 500,
    LoggingException: 500,
}


def get_status_code_for_exception(exc: Exception) -> int:
    """
    Get appropriate HTTP status code for exception.
    
    Args:
        exc: Exception instance
    
    Returns:
        HTTP status code (default 500 for unknown exceptions)
    """
    exc_type = type(exc)
    return EXCEPTION_TO_STATUS_CODE.get(exc_type, 500)
