"""
Base classes and types for API layer
"""

from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, List, Any
from enum import Enum


class StatusCode(Enum):
    """API response status codes"""
    SUCCESS = "success"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"


T = TypeVar("T")


@dataclass
class APIResponse(Generic[T]):
    """
    Standard API response wrapper.
    All API methods return this for consistent handling.
    """
    status: StatusCode
    data: Optional[T] = None
    message: str = ""
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    @property
    def success(self) -> bool:
        """Check if response is successful"""
        return self.status == StatusCode.SUCCESS

    @classmethod
    def ok(cls, data: T = None, message: str = "") -> "APIResponse[T]":
        """Create success response"""
        return cls(status=StatusCode.SUCCESS, data=data, message=message)

    @classmethod
    def error(cls, message: str, errors: List[str] = None) -> "APIResponse[T]":
        """Create error response"""
        return cls(status=StatusCode.ERROR, message=message, errors=errors or [])

    @classmethod
    def validation_error(cls, errors: List[str]) -> "APIResponse[T]":
        """Create validation error response"""
        return cls(
            status=StatusCode.VALIDATION_ERROR,
            message="Validation failed",
            errors=errors
        )

    @classmethod
    def not_found(cls, message: str = "Not found") -> "APIResponse[T]":
        """Create not found response"""
        return cls(status=StatusCode.NOT_FOUND, message=message)


class BaseAPI:
    """Base class for all API classes"""

    def __init__(self, container: "Container"):
        self._container = container

    @property
    def container(self) -> "Container":
        return self._container
