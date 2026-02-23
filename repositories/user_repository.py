"""User repository."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    """Data access for users."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def list_all(self) -> List[User]:
        return self.session.query(User).order_by(User.id.asc()).all()

    def delete(self, user: User) -> None:
        self.session.delete(user)
