"""
Authorization-related types
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# from pydantic import BaseModel
# from app.types.session import AuthGrant
from app.types.user import UserID


class AuthSubject:
    """
    Authorization Subject

    Represents a user of the application.
    Can be associated with a "user" or some other entity.
    Can have associated permissions, usually derived from
    authentication assertions.
    """

    # If this subject is tied to an application user, this field will
    # contain its user ID
    user_id: UserID | None

    # Allow access to some restricted actions.
    # This usually requires stronger / more recent authentication.
    # Example actions requiring this: account management, payment,
    # other high-risk actions.
    allow_protected_actions: bool = False


# Authorization actions ----------------------------------------------


class AuthzAction:
    """Base for objects representing application actions.

    Used for authorization checks.  Subclasses are
    application-specific.
    """

    # Leave it to the app to implement actions.
    # This can even be Union, or Protocol


# Authorization result -----------------------------------------------


@dataclass
class AuthzResult:
    """Result of an authorization check"""

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


class CorrectiveActionBase:
    """Base object for "corrective actions".

    Corrective actions represent actions that can be taken to remedy a
    failed authorization attempt.
    """



class AuthzScope:
    """Base object for authorization scopes.

    A scope represent a set of grants the authorization subject wants
    to obtain in order to perform an action.

    They can be associated to a flow
    """

    # Leave it to the app to implement scopes.
