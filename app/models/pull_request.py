"""
Pull Request model for database.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class PRStatus(str, Enum):
    """Pull Request status enum."""
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class PRReviewStatus(str, Enum):
    """Pull Request review status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"
    DISMISSED = "dismissed"


class PullRequest(Base):
    """Pull Request database model."""

    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # GitHub PR info
    github_id = Column(Integer, unique=True, index=True, nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String(512), nullable=False)
    body = Column(Text, nullable=True)
    html_url = Column(Text, nullable=False)

    # Branch info
    head_branch = Column(String(255), nullable=False)
    head_sha = Column(String(40), nullable=True)
    base_branch = Column(String(255), nullable=False)
    base_sha = Column(String(40), nullable=True)

    # Status
    status = Column(SQLEnum(PRStatus), default=PRStatus.OPEN)
    review_status = Column(SQLEnum(PRReviewStatus), default=PRReviewStatus.PENDING)
    is_draft = Column(Boolean, default=False)
    is_mergeable = Column(Boolean, nullable=True)
    mergeable_state = Column(String(50), nullable=True)

    # Counts
    commits_count = Column(Integer, default=0)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    changed_files = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    review_comments_count = Column(Integer, default=0)

    # AI-generated content tracking
    ai_generated = Column(Boolean, default=False)
    ai_model_used = Column(String(100), nullable=True)
    ai_prompt = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    github_created_at = Column(DateTime, nullable=True)
    github_updated_at = Column(DateTime, nullable=True)
    merged_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    creator = relationship("User", back_populates="pull_requests")

    def __repr__(self) -> str:
        return f"<PullRequest(id={self.id}, number={self.number}, title={self.title})>"


class PRComment(Base):
    """Pull Request comment database model."""

    __tablename__ = "pr_comments"

    id = Column(Integer, primary_key=True, index=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    github_id = Column(Integer, unique=True, index=True, nullable=False)
    body = Column(Text, nullable=False)
    path = Column(Text, nullable=True)
    position = Column(Integer, nullable=True)
    line = Column(Integer, nullable=True)

    is_ai_generated = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PRComment(id={self.id}, pr_id={self.pull_request_id})>"
