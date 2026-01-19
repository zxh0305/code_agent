"""
Repository model for database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Repository(Base):
    """Repository database model."""

    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # GitHub repository info
    github_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(512), nullable=False)  # owner/repo
    description = Column(Text, nullable=True)
    html_url = Column(Text, nullable=False)
    clone_url = Column(Text, nullable=False)
    ssh_url = Column(Text, nullable=True)
    default_branch = Column(String(255), default="main")

    # Repository status
    is_private = Column(Boolean, default=False)
    is_fork = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Local storage info
    local_path = Column(Text, nullable=True)
    last_synced_at = Column(DateTime, nullable=True)

    # Statistics
    stars_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    watchers_count = Column(Integer, default=0)
    open_issues_count = Column(Integer, default=0)

    # Language info
    language = Column(String(100), nullable=True)
    languages = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    github_created_at = Column(DateTime, nullable=True)
    github_updated_at = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="repositories")
    pull_requests = relationship("PullRequest", back_populates="repository")
    code_analyses = relationship("CodeAnalysis", back_populates="repository")

    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, full_name={self.full_name})>"


class Branch(Base):
    """Branch database model."""

    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)

    name = Column(String(255), nullable=False)
    sha = Column(String(40), nullable=False)
    is_protected = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Branch(id={self.id}, name={self.name})>"
