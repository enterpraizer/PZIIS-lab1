"""Authentication and user management business logic."""

from __future__ import annotations

import logging

from models.base import Role
from models.user import User
from repositories.user_repository import UserRepository
from utils.exceptions import AuthenticationError, AuthorizationError, ConflictError
from utils.security import hash_password, verify_password
from utils.validators import validate_password, validate_username

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic for authentication/authorization."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register(self, username: str, password: str, role: str) -> User:
        """Register new user."""
        clean_username = validate_username(username)
        clean_password = validate_password(password)

        try:
            user_role = Role(role)
        except ValueError as exc:
            raise AuthorizationError("Invalid role") from exc

        if user_role == Role.ADMIN:
            raise AuthorizationError("Public registration for admin is not allowed")

        if self.user_repository.get_by_username(clean_username):
            raise ConflictError("Username already exists")

        user = User(
            username=clean_username,
            password_hash=hash_password(clean_password),
            role=user_role,
            is_blocked=False,
        )
        created = self.user_repository.create(user)
        logger.info("Registered user '%s' with role '%s'", created.username, created.role.value)
        return created

    def login(self, username: str, password: str) -> User:
        """Authenticate user."""
        clean_username = validate_username(username)
        user = self.user_repository.get_by_username(clean_username)
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid username or password")
        if user.is_blocked:
            raise AuthorizationError("User account is blocked")

        logger.info("User '%s' logged in", user.username)
        return user
