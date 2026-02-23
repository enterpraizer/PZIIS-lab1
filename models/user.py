"""User model."""

from __future__ import annotations

from flask_login import UserMixin
from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, Role, TimestampMixin


class User(UserMixin, Base, TimestampMixin):
    """System user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    articles = relationship("Article", back_populates="author", cascade="all")
    questions = relationship("Question", back_populates="author", cascade="all")
    answers = relationship("Answer", back_populates="author", cascade="all")

    @property
    def is_active(self) -> bool:
        """Flask-Login active flag."""
        return not self.is_blocked
