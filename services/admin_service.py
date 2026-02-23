"""Admin business logic."""

from __future__ import annotations

import logging
from typing import List

from models.base import Role
from models.user import User
from repositories.user_repository import UserRepository
from utils.exceptions import AuthorizationError, NotFoundError

logger = logging.getLogger(__name__)


class AdminService:
    """Admin operations for user management."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def list_users(self, current_user: User) -> List[User]:
        self._require_admin(current_user)
        return self.user_repository.list_all()

    def block_user(self, current_user: User, user_id: int) -> User:
        self._require_admin(current_user)
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if user.role == Role.ADMIN:
            raise AuthorizationError("Admin user cannot be blocked")

        user.is_blocked = True
        logger.info("User id=%s blocked by admin '%s'", user.id, current_user.username)
        return user

    def unblock_user(self, current_user: User, user_id: int) -> User:
        self._require_admin(current_user)
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        user.is_blocked = False
        logger.info("User id=%s unblocked by admin '%s'", user.id, current_user.username)
        return user

    def delete_user(self, current_user: User, user_id: int) -> None:
        self._require_admin(current_user)
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if user.role == Role.ADMIN:
            raise AuthorizationError("Admin user cannot be deleted")

        self.user_repository.delete(user)
        logger.info("User id=%s deleted by admin '%s'", user.id, current_user.username)

    @staticmethod
    def _require_admin(user: User) -> None:
        if user.role != Role.ADMIN:
            raise AuthorizationError("Admin access required")
