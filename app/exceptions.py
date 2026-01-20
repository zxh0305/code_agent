"""
Custom exceptions for the application.
Provides structured error handling with error codes and messages.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for all application errors."""

    error_code: str = "INTERNAL_ERROR"
    status_code: int = 500
    message: str = "An internal error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        self.message = message or self.message
        self.details = details or {}
        if error_code:
            self.error_code = error_code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================

class AuthenticationError(AppException):
    """Raised when authentication fails."""
    error_code = "AUTHENTICATION_FAILED"
    status_code = 401
    message = "Authentication required"


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid or expired."""
    error_code = "INVALID_TOKEN"
    message = "Invalid or expired authentication token"


class TokenExpiredError(AuthenticationError):
    """Raised when token has expired."""
    error_code = "TOKEN_EXPIRED"
    message = "Authentication token has expired"


class AuthorizationError(AppException):
    """Raised when user lacks permission."""
    error_code = "AUTHORIZATION_FAILED"
    status_code = 403
    message = "You don't have permission to perform this action"


class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks specific permission."""
    error_code = "INSUFFICIENT_PERMISSIONS"


# ============================================================================
# Validation Exceptions
# ============================================================================

class ValidationError(AppException):
    """Raised when input validation fails."""
    error_code = "VALIDATION_ERROR"
    status_code = 422
    message = "Input validation failed"


class InvalidInputError(ValidationError):
    """Raised for invalid input data."""
    error_code = "INVALID_INPUT"


class MissingFieldError(ValidationError):
    """Raised when required field is missing."""
    error_code = "MISSING_FIELD"

    def __init__(self, field_name: str, **kwargs):
        super().__init__(
            message=f"Required field '{field_name}' is missing",
            details={"field": field_name},
            **kwargs
        )


class InvalidFormatError(ValidationError):
    """Raised when input format is invalid."""
    error_code = "INVALID_FORMAT"


# ============================================================================
# Resource Exceptions
# ============================================================================

class ResourceNotFoundError(AppException):
    """Raised when requested resource is not found."""
    error_code = "RESOURCE_NOT_FOUND"
    status_code = 404
    message = "Requested resource not found"

    def __init__(self, resource_type: str, resource_id: Any = None, **kwargs):
        details = {"resource_type": resource_type}
        if resource_id is not None:
            details["resource_id"] = str(resource_id)
        super().__init__(
            message=f"{resource_type} not found",
            details=details,
            **kwargs
        )


class ResourceAlreadyExistsError(AppException):
    """Raised when resource already exists."""
    error_code = "RESOURCE_EXISTS"
    status_code = 409
    message = "Resource already exists"


class ResourceConflictError(AppException):
    """Raised when resource conflict occurs."""
    error_code = "RESOURCE_CONFLICT"
    status_code = 409
    message = "Resource conflict detected"


# ============================================================================
# External Service Exceptions
# ============================================================================

class ExternalServiceError(AppException):
    """Base exception for external service errors."""
    error_code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502
    message = "External service error"


class GitHubAPIError(ExternalServiceError):
    """Raised when GitHub API call fails."""
    error_code = "GITHUB_API_ERROR"
    message = "GitHub API request failed"

    def __init__(self, message: str = None, github_status: int = None, **kwargs):
        details = {}
        if github_status:
            details["github_status_code"] = github_status
        super().__init__(message=message, details=details, **kwargs)


class GitHubAuthError(GitHubAPIError):
    """Raised when GitHub authentication fails."""
    error_code = "GITHUB_AUTH_ERROR"
    status_code = 401
    message = "GitHub authentication failed"


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub rate limit is exceeded."""
    error_code = "GITHUB_RATE_LIMIT"
    status_code = 429
    message = "GitHub API rate limit exceeded"


class OpenAIAPIError(ExternalServiceError):
    """Raised when OpenAI API call fails."""
    error_code = "OPENAI_API_ERROR"
    message = "OpenAI API request failed"


class OpenAIRateLimitError(OpenAIAPIError):
    """Raised when OpenAI rate limit is exceeded."""
    error_code = "OPENAI_RATE_LIMIT"
    status_code = 429
    message = "OpenAI API rate limit exceeded"


class OpenAIInvalidKeyError(OpenAIAPIError):
    """Raised when OpenAI API key is invalid."""
    error_code = "OPENAI_INVALID_KEY"
    status_code = 401
    message = "Invalid OpenAI API key"


# ============================================================================
# Database Exceptions
# ============================================================================

class DatabaseError(AppException):
    """Base exception for database errors."""
    error_code = "DATABASE_ERROR"
    status_code = 500
    message = "Database operation failed"


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    error_code = "DATABASE_CONNECTION_ERROR"
    message = "Failed to connect to database"


class TransactionError(DatabaseError):
    """Raised when database transaction fails."""
    error_code = "TRANSACTION_ERROR"
    message = "Database transaction failed"


# ============================================================================
# Rate Limiting Exceptions
# ============================================================================

class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""
    error_code = "RATE_LIMIT_EXCEEDED"
    status_code = 429
    message = "Too many requests. Please try again later."

    def __init__(self, retry_after: int = None, **kwargs):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(details=details, **kwargs)


# ============================================================================
# File Operation Exceptions
# ============================================================================

class FileOperationError(AppException):
    """Base exception for file operation errors."""
    error_code = "FILE_OPERATION_ERROR"
    status_code = 400
    message = "File operation failed"


class FileNotFoundError(FileOperationError):
    """Raised when file is not found."""
    error_code = "FILE_NOT_FOUND"
    status_code = 404
    message = "File not found"


class FileTooLargeError(FileOperationError):
    """Raised when file exceeds size limit."""
    error_code = "FILE_TOO_LARGE"
    status_code = 413
    message = "File size exceeds limit"


class InvalidFilePathError(FileOperationError):
    """Raised when file path is invalid or unsafe."""
    error_code = "INVALID_FILE_PATH"
    status_code = 400
    message = "Invalid or unsafe file path"


# ============================================================================
# Code Analysis Exceptions
# ============================================================================

class CodeAnalysisError(AppException):
    """Base exception for code analysis errors."""
    error_code = "CODE_ANALYSIS_ERROR"
    status_code = 400
    message = "Code analysis failed"


class SyntaxAnalysisError(CodeAnalysisError):
    """Raised when code has syntax errors."""
    error_code = "SYNTAX_ERROR"
    message = "Code contains syntax errors"


class UnsupportedLanguageError(CodeAnalysisError):
    """Raised when language is not supported."""
    error_code = "UNSUPPORTED_LANGUAGE"
    message = "Programming language not supported"


# ============================================================================
# Configuration Exceptions
# ============================================================================

class ConfigurationError(AppException):
    """Raised when configuration is invalid or missing."""
    error_code = "CONFIGURATION_ERROR"
    status_code = 500
    message = "Application configuration error"


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""
    error_code = "MISSING_CONFIGURATION"

    def __init__(self, config_key: str, **kwargs):
        super().__init__(
            message=f"Required configuration '{config_key}' is missing",
            details={"config_key": config_key},
            **kwargs
        )
