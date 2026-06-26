"""
Authorization-related types
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from app.types.session import AuthGrant
from app.types.user import UserID


@dataclass
class AuthzResult:
    allowed: bool
    upgrade_paths: list[Any] = field(default_factory=list)

    @classmethod
    def allow(cls):
        return cls(allowed=True)

    @classmethod
    def deny(cls, upgrade_paths: list[Any] | None = None):
        if upgrade_paths is None:
            upgrade_paths = []
        return cls(allowed=False, upgrade_paths=upgrade_paths)


class AuthzSubject:
    user_id: UserID | None
    grants: list[AuthGrant]


class AuthzAction:
    # Leave it to the app to implement actions.
    # This can even be Union, or Protocol
    pass


class AuthzGrant(BaseModel):
    # Leave it to the app to implement grants.
    pass


class AuthzScope:
    """
    A scope represent a set of grants the authorization subject wants
    to obtain in order to perform an action.
    """
    # Leave it to the app to implement scopes.
    pass
