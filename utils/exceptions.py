"""Custom application exceptions."""


class AppError(Exception):
    """Base application exception."""


class ValidationError(AppError):
    """Raised when user input is invalid."""


class AuthorizationError(AppError):
    """Raised when user has no access to an operation."""


class AuthenticationError(AppError):
    """Raised when authentication fails."""


class NotFoundError(AppError):
    """Raised when an entity is not found."""


class ConflictError(AppError):
    """Raised when an operation conflicts with existing data."""
