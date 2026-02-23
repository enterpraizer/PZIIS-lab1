"""Database initialization and session management."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from models.article import Article
from models.base import Base, Role
from models.category import Category
from models.question import Answer, Question
from models.user import User
from utils.config import config
from utils.security import hash_password


engine = create_engine(config.database_url, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
    expire_on_commit=False,
)


def init_db() -> None:
    """Create database schema and seed defaults."""
    Base.metadata.create_all(bind=engine)
    _seed_defaults()


def _seed_defaults() -> None:
    """Seed initial categories and admin user if missing."""
    default_categories = [
        "Налоги",
        "Регистрация бизнеса",
        "Маркетинг",
        "Финансы",
        "Юридические вопросы",
    ]

    with session_scope() as session:
        existing_categories = {c.name for c in session.query(Category).all()}
        for name in default_categories:
            if name not in existing_categories:
                session.add(Category(name=name))

        admin_exists = session.query(User).filter(User.role == Role.ADMIN).first()
        if not admin_exists:
            session.add(
                User(
                    username="admin",
                    password_hash=hash_password("Admin123!"),
                    role=Role.ADMIN,
                    is_blocked=False,
                )
            )


def get_session() -> Session:
    """Create a new session instance."""
    return SessionLocal()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional scope around operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def is_sqlite() -> bool:
    """Check if active DB is SQLite."""
    return config.database_url.startswith("sqlite")


def healthcheck() -> bool:
    """Quick DB availability check."""
    with session_scope() as session:
        session.execute(text("SELECT 1"))
    return True
