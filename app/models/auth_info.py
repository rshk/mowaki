from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


@dataclass
class AuthInfo:
    """
    Authentication information
    """

    @classmethod
    def for_anonymous(cls):
        return cls(is_authenticated=False)

    @classmethod
    def for_user(cls, user: User):
        return cls(is_authenticated=True, user=user)

    is_authenticated: bool = False
    user: User = None
