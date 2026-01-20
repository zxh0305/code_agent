"""
Enhanced security utilities with authentication dependencies.
"""

from datetime import datetime, timedelta
from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    """Token payload data model."""
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    scopes: list[str] = []
    exp: Optional[datetime] = None


class UserContext(BaseModel):
    """Authenticated user context."""
    user_id: int
    username: Optional[str] = None
    email: Optional[str] = None
    scopes: list[str] = []
    is_authenticated: bool = True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_secret_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_secret_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string."""
    import secrets
    return secrets.token_urlsafe(length)


async def get_current_user(
    request: Request,
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials],
        Depends(bearer_scheme)
    ] = None,
) -> Optional[UserContext]:
    """
    Dependency to get the current authenticated user.

    Returns None if no valid token is provided.
    Use require_auth for endpoints that require authentication.
    """
    # Check if user was already set by middleware
    if hasattr(request.state, "user_id") and request.state.user_id:
        return UserContext(
            user_id=request.state.user_id,
            username=getattr(request.state, "username", None),
            scopes=getattr(request.state, "scopes", []),
        )

    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        return None

    return UserContext(
        user_id=payload.get("sub"),
        username=payload.get("username"),
        email=payload.get("email"),
        scopes=payload.get("scopes", []),
    )


async def require_auth(
    user: Annotated[Optional[UserContext], Depends(get_current_user)]
) -> UserContext:
    """
    Dependency that requires authentication.

    Raises HTTPException if user is not authenticated.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_scope(required_scope: str):
    """
    Factory for creating scope-checking dependencies.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_scope("admin"))])
    """
    async def check_scope(
        user: Annotated[UserContext, Depends(require_auth)]
    ) -> UserContext:
        if required_scope not in user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scope: {required_scope}",
            )
        return user

    return check_scope


class PermissionChecker:
    """
    Reusable permission checker for role-based access control.

    Usage:
        @router.get("/admin", dependencies=[Depends(PermissionChecker(["admin"]))])
    """

    def __init__(self, required_scopes: list[str]):
        self.required_scopes = required_scopes

    async def __call__(
        self,
        user: Annotated[UserContext, Depends(require_auth)]
    ) -> UserContext:
        for scope in self.required_scopes:
            if scope not in user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {scope}",
                )
        return user


# Optional user dependency (doesn't require auth but extracts if present)
OptionalUser = Annotated[Optional[UserContext], Depends(get_current_user)]

# Required user dependency
CurrentUser = Annotated[UserContext, Depends(require_auth)]
