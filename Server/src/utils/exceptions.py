"""Custom exceptions for the application."""


class LDPlayerManagementException(Exception):
    """Base exception for all application-specific exceptions."""
    pass


class EmulatorNotFoundError(LDPlayerManagementException):
    """Raised when emulator is not found."""
    def __init__(self, emulator_id: str):
        self.emulator_id = emulator_id
        super().__init__(f"Emulator '{emulator_id}' not found")


class WorkstationNotFoundError(LDPlayerManagementException):
    """Raised when workstation is not found."""
    def __init__(self, workstation_id: str):
        self.workstation_id = workstation_id
        super().__init__(f"Workstation '{workstation_id}' not found")


class EmulatorCreationError(LDPlayerManagementException):
    """Raised when emulator creation fails."""
    def __init__(self, name: str, reason: str):
        self.name = name
        self.reason = reason
        super().__init__(f"Failed to create emulator '{name}': {reason}")


class InvalidConfigError(LDPlayerManagementException):
    """Raised when configuration is invalid."""
    def __init__(self, config_field: str, reason: str):
        self.config_field = config_field
        self.reason = reason
        super().__init__(f"Invalid config field '{config_field}': {reason}")


class WorkstationConnectionError(LDPlayerManagementException):
    """Raised when unable to connect to workstation."""
    def __init__(self, workstation_id: str, reason: str):
        self.workstation_id = workstation_id
        self.reason = reason
        super().__init__(f"Failed to connect to workstation '{workstation_id}': {reason}")


class OperationTimeoutError(LDPlayerManagementException):
    """Raised when operation times out."""
    def __init__(self, operation: str, timeout_seconds: float):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Operation '{operation}' timed out after {timeout_seconds}s")


class OperationFailedError(LDPlayerManagementException):
    """Raised when operation fails."""
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"Operation '{operation}' failed: {reason}")


class InvalidInputError(LDPlayerManagementException):
    """Raised when input validation fails."""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Invalid input for '{field}': {reason}")


class ServiceNotInitializedError(LDPlayerManagementException):
    """Raised when service is not properly initialized."""
    def __init__(self, service_name: str):
        self.service_name = service_name
        super().__init__(f"Service '{service_name}' is not initialized")


class DependencyNotFoundError(LDPlayerManagementException):
    """Raised when dependency is not found in DI container."""
    def __init__(self, dependency_name: str):
        self.dependency_name = dependency_name
        super().__init__(f"Dependency '{dependency_name}' not found in DI container")


# ============================================================================
# ADDITIONAL EXCEPTION TYPES FOR PHASE 2 REFACTOR
# ============================================================================

class DatabaseConnectionError(LDPlayerManagementException):
    """Database connection failed."""
    def __init__(self, database_url: str, reason: str):
        self.database_url = database_url
        self.reason = reason
        super().__init__(f"Database connection failed: {reason}")


class ConfigurationLoadError(LDPlayerManagementException):
    """Configuration file loading failed."""
    def __init__(self, config_file: str, reason: str):
        self.config_file = config_file
        self.reason = reason
        super().__init__(f"Failed to load config from {config_file}: {reason}")


class RemoteProtocolError(LDPlayerManagementException):
    """Remote protocol (WinRM, SMB) error."""
    def __init__(self, protocol: str, reason: str):
        self.protocol = protocol
        self.reason = reason
        super().__init__(f"{protocol} protocol error: {reason}")


class BackupFailedError(LDPlayerManagementException):
    """Backup operation failed."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Backup failed: {reason}")


class MonitoringFailedError(LDPlayerManagementException):
    """Monitoring operation failed."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Monitoring failed: {reason}")


class AuthenticationError(LDPlayerManagementException):
    """Authentication failed."""
    def __init__(self, reason: str = "Invalid credentials"):
        self.reason = reason
        super().__init__(f"Authentication failed: {reason}")


class TokenExpiredError(LDPlayerManagementException):
    """JWT token has expired."""
    def __init__(self):
        super().__init__("Access token has expired")


class OperationAlreadyRunningError(LDPlayerManagementException):
    """Operation is already running."""
    def __init__(self, operation: str, resource_id: str):
        self.operation = operation
        self.resource_id = resource_id
        super().__init__(f"Another {operation} operation is already running on {resource_id}")

