from typing import Any


class SessionError(Exception):
    pass


class SessionExpired(SessionError):
    """Session was found, but it expired"""



class SessionNotFound(SessionError):
    """Session was not found"""



class SessionInvalid(SessionError):
    """Session was found but it's invalid for some reason"""



class AuthorizationError(Exception):
    """Used to indicate a user is not authorized to perform an action"""

    # User may upgrade the session to include extra scopes in order to
    # perform this action.
    upgrade_possible: bool

    # Scopes that may be requested in order to perform this action.
    # Only populated if upgrade_possible=True.
    require_scopes: list[Any]

    def __init__(
        self, upgrade_possible: bool = False, require_scopes: list[Any] | None = None
    ):
        self.upgrade_possible = upgrade_possible
        if require_scopes is None:
            require_scopes = []
        self.require_scopes = require_scopes

    @classmethod
    def definitive(cls):
        return AuthorizationError(upgrade_possible=False)

    @classmethod
    def require_upgrade(cls, require_scopes: list[Any]):
        return AuthorizationError(upgrade_possible=True, require_scopes=require_scopes)
