"""
User model for database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)

    # GitHub OAuth fields
    github_id = Column(Integer, unique=True, index=True, nullable=True)
    github_username = Column(String(255), nullable=True)
    github_access_token = Column(Text, nullable=True)
    github_refresh_token = Column(Text, nullable=True)
    github_token_expires_at = Column(DateTime, nullable=True)

    # Status fields
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    repositories = relationship("Repository", back_populates="owner")
    pull_requests = relationship("PullRequest", back_populates="creator")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
