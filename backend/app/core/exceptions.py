"""Shared exception types for the API layer."""

from __future__ import annotations


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, *, code: str = "app_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="not_found")


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, code="unauthorized")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, code="forbidden")


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, code="conflict")


class ValidationAppError(AppError):
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message, code="validation_error")


class RateLimitError(AppError):
    def __init__(self, message: str = "Too many requests") -> None:
        super().__init__(message, code="rate_limited")
