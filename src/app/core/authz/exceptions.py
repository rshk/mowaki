from typing import Any

from app.exceptions import AppException


class AuthorizationError(AppException):
    """Used to indicate a user is not authorized to perform an action"""

    __slots__ = ["actions", "message"]

    # Error message
    message: str | None

    # Actions that can be taken to gain the required privileges, if any
    actions: list[Any] | None

    def __init__(
        self,
        message: str | None = None,
        actions: list[Any] | None = None,
    ):
        self.message = message
        self.actions = actions
        if self.actions is None:
            self.actions = []
