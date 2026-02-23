"""SQLAlchemy base and common types."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base class."""


class TimestampMixin:
    """Common timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )


class Role(str, enum.Enum):
    """User roles in the system."""

    ENTREPRENEUR = "entrepreneur"
    CONSULTANT = "consultant"
    ADMIN = "admin"
