"""
Input validation utilities with enhanced security checks.
"""

import re
import os
from typing import Optional, List, Any
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================================================
# Validation Constants
# ============================================================================

# Maximum lengths
MAX_TITLE_LENGTH = 256
MAX_BODY_LENGTH = 65535
MAX_PATH_LENGTH = 4096
MAX_CODE_LENGTH = 1000000  # 1MB
MAX_FILE_SIZE_MB = 50
MAX_LIST_LENGTH = 100
MAX_FILENAME_LENGTH = 255

# Patterns
SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_\-./]+$')
GITHUB_REPO_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\.]+$')
BRANCH_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-./]+$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')

# Dangerous patterns for path traversal
DANGEROUS_PATH_PATTERNS = [
    '..',
    '~',
    '$',
    '`',
    '|',
    ';',
    '&',
    '\x00',
]


# ============================================================================
# Validation Functions
# ============================================================================

def validate_file_path(path: str, base_path: Optional[str] = None) -> str:
    """
    Validate and sanitize file path to prevent path traversal attacks.

    Args:
        path: File path to validate
        base_path: Optional base path that the file must be within

    Returns:
        Validated path

    Raises:
        ValueError: If path is invalid or unsafe
    """
    if not path:
        raise ValueError("Path cannot be empty")

    if len(path) > MAX_PATH_LENGTH:
        raise ValueError(f"Path exceeds maximum length of {MAX_PATH_LENGTH}")

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATH_PATTERNS:
        if pattern in path:
            raise ValueError(f"Path contains unsafe pattern: {pattern}")

    # Normalize path
    normalized = os.path.normpath(path)

    # If base_path is provided, ensure path is within it
    if base_path:
        base_resolved = os.path.realpath(base_path)
        path_resolved = os.path.realpath(os.path.join(base_path, normalized))

        if not path_resolved.startswith(base_resolved):
            raise ValueError("Path traversal detected")

    return normalized


def validate_repository_name(name: str) -> str:
    """Validate GitHub repository name (owner/repo format)."""
    if not name:
        raise ValueError("Repository name cannot be empty")

    if not GITHUB_REPO_PATTERN.match(name):
        raise ValueError("Invalid repository name format. Expected: owner/repo")

    return name


def validate_branch_name(name: str) -> str:
    """Validate Git branch name."""
    if not name:
        raise ValueError("Branch name cannot be empty")

    if len(name) > MAX_FILENAME_LENGTH:
        raise ValueError(f"Branch name exceeds maximum length of {MAX_FILENAME_LENGTH}")

    if not BRANCH_NAME_PATTERN.match(name):
        raise ValueError("Invalid branch name format")

    return name


def validate_username(username: str) -> str:
    """Validate GitHub username."""
    if not username:
        raise ValueError("Username cannot be empty")

    if len(username) > 39:  # GitHub's limit
        raise ValueError("Username exceeds maximum length")

    if not USERNAME_PATTERN.match(username):
        raise ValueError("Invalid username format")

    return username


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing potentially dangerous characters.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return value

    # Truncate to max length
    value = value[:max_length]

    # Remove null bytes
    value = value.replace('\x00', '')

    # Remove control characters except newline and tab
    value = ''.join(char for char in value if char == '\n' or char == '\t' or not char.iscontrol())

    return value.strip()


def validate_list_length(items: List[Any], max_length: int = MAX_LIST_LENGTH) -> List[Any]:
    """Validate list doesn't exceed maximum length."""
    if items and len(items) > max_length:
        raise ValueError(f"List exceeds maximum length of {max_length}")
    return items


# ============================================================================
# Enhanced Pydantic Base Models
# ============================================================================

class ValidatedBaseModel(BaseModel):
    """Base model with common validation rules."""

    class Config:
        str_strip_whitespace = True
        str_min_length = 0
        validate_assignment = True


class GitHubRepoRequest(ValidatedBaseModel):
    """Validated GitHub repository request."""
    owner: str = Field(..., min_length=1, max_length=39)
    repo: str = Field(..., min_length=1, max_length=100)

    @field_validator('owner', 'repo')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not USERNAME_PATTERN.match(v):
            raise ValueError("Invalid name format")
        return v


class CreatePRRequestValidated(ValidatedBaseModel):
    """Validated PR creation request."""
    repo_owner: str = Field(..., min_length=1, max_length=39)
    repo_name: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    body: str = Field(..., max_length=MAX_BODY_LENGTH)
    head_branch: str = Field(..., min_length=1, max_length=MAX_FILENAME_LENGTH)
    base_branch: str = Field(default="main", min_length=1, max_length=MAX_FILENAME_LENGTH)
    draft: bool = False
    reviewers: Optional[List[str]] = Field(default=None, max_length=20)
    labels: Optional[List[str]] = Field(default=None, max_length=50)
    issue_number: Optional[int] = Field(default=None, ge=1)

    @field_validator('head_branch', 'base_branch')
    @classmethod
    def validate_branch(cls, v: str) -> str:
        return validate_branch_name(v)

    @field_validator('reviewers')
    @classmethod
    def validate_reviewers(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            return [validate_username(u) for u in v]
        return v


class FilePathRequest(ValidatedBaseModel):
    """Validated file path request."""
    local_path: str = Field(..., min_length=1, max_length=MAX_PATH_LENGTH)
    file_path: str = Field(..., min_length=1, max_length=MAX_PATH_LENGTH)

    @field_validator('local_path', 'file_path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        return validate_file_path(v)


class CodeAnalysisRequest(ValidatedBaseModel):
    """Validated code analysis request."""
    source_code: str = Field(..., min_length=1, max_length=MAX_CODE_LENGTH)
    language: str = Field(default="python", min_length=1, max_length=50)

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        allowed_languages = {'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'cpp', 'c'}
        if v.lower() not in allowed_languages:
            raise ValueError(f"Unsupported language. Allowed: {', '.join(allowed_languages)}")
        return v.lower()


class LLMRequest(ValidatedBaseModel):
    """Validated LLM request."""
    requirements: str = Field(..., min_length=1, max_length=MAX_BODY_LENGTH)
    language: str = Field(default="python", min_length=1, max_length=50)
    context: Optional[str] = Field(default=None, max_length=MAX_CODE_LENGTH)
    use_local: bool = False


# ============================================================================
# Input Sanitization Middleware
# ============================================================================

def sanitize_request_data(data: dict) -> dict:
    """
    Recursively sanitize all string values in request data.

    Args:
        data: Request data dictionary

    Returns:
        Sanitized data dictionary
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item) if isinstance(item, str)
                else sanitize_request_data(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized
