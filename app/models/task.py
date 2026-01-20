"""
Task model for code development tasks.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Task(Base):
    """Task model for tracking code development tasks."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    # Task info
    name = Column(String(255), nullable=False, default="新建任务")
    description = Column(Text, nullable=True)

    # GitHub context
    repository = Column(String(500), nullable=True)  # full_name: owner/repo
    branch = Column(String(255), nullable=True)

    # Task content
    requirement = Column(Text, nullable=True)  # User's code requirement
    generated_code = Column(Text, nullable=True)  # AI generated code
    language = Column(String(50), nullable=True)

    # Status
    status = Column(String(50), default="draft")  # draft, in_progress, completed
    is_archived = Column(Boolean, default=False)

    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional task data

    # User relationship (optional)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "repository": self.repository,
            "branch": self.branch,
            "requirement": self.requirement,
            "generated_code": self.generated_code,
            "language": self.language,
            "status": self.status,
            "is_archived": self.is_archived,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
