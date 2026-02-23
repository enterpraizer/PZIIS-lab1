"""Validation helpers."""

from __future__ import annotations

import re

from utils.exceptions import ValidationError


USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,50}$")


def validate_username(username: str) -> str:
    """Validate username format."""
    clean = username.strip()
    if not USERNAME_RE.fullmatch(clean):
        raise ValidationError(
            "Username must be 3-50 chars and contain only letters, digits, _, ., -"
        )
    return clean


def validate_password(password: str) -> str:
    """Validate password strength."""
    if len(password) < 8:
        raise ValidationError("Password must contain at least 8 characters")
    if password.islower() or password.isupper() or password.isdigit():
        raise ValidationError(
            "Password must include mixed character types (letters and digits/symbols)"
        )
    return password


def validate_non_empty(value: str, field_name: str, max_length: int = 5000) -> str:
    """Validate non-empty text with max length."""
    clean = value.strip()
    if not clean:
        raise ValidationError(f"{field_name} cannot be empty")
    if len(clean) > max_length:
        raise ValidationError(f"{field_name} exceeds maximum length ({max_length})")
    return clean
