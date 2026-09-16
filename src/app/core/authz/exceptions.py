from dataclasses import dataclass, field
from typing import Any

from app.exceptions import AppException
from app.types.auth.auth_flow import FlowKind


@dataclass(slots=True)
class AuthorizationError(AppException):
    """Used to indicate a user is not authorized to perform an action"""

    # Error message, mainly for logging and internal use
    message: str | None

    # ID (and arguments) of user-facing message
    msg_id: str | None = None
    msg_args: dict[str, str] = field(default_factory=dict)

    # List of "corrective actions" that the user can take in order to
    # gain privileges required to perform the action which was denied.
    fix_actions: list[BaseFixAction] = field(default_factory=list)

    # TODO: should we add some information about the action which was
    # denied? Or just log it in the authorization checker?


class BaseFixAction:
    pass


class FixActionFlow:
    __slots__ = ["flow_kind", "flow_params"]

    flow_kind: FlowKind
    flow_params: dict[str, Any]

    def __init__(self, kind: FlowKind | str, params: dict[str, Any] | None = None):
        self.flow_kind = FlowKind(kind)
        if params is None:
            params = {}
        self.flow_params = params
