from dataclasses import dataclass, field
from typing import Any

from app.exceptions import AppException
from app.types.auth.auth_flow import FlowKind

from .result import BaseFixAction, FixActionFlow


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

    def set_user_message(self, msg: str, **kwargs: str):
        """Set user-facing message"""
        self.msg_id = msg
        self.msg_args = kwargs
        return self

    def add_fix_action(self, action: BaseFixAction):
        self.fix_actions.append(action)
        return self

    def add_fix_action_flow(self, kind: FlowKind | str, **params: Any):
        """Add a "flow" fix action to the exeception"""
        action = FixActionFlow(kind, params)
        self.fix_actions.append(action)
        return self
