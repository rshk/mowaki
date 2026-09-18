from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.types.auth.auth_flow import FlowKind


@dataclass(slots=True)
class AuthzResult:
    """Result of an authorization check"""

    allowed: bool
    fix_actions: list[BaseFixAction] = field(default_factory=list)

    @classmethod
    def allow(cls):
        return cls(allowed=True)

    @classmethod
    def deny(cls, fix_actions: list[Any] | None = None):
        if fix_actions is None:
            fix_actions = []
        return cls(allowed=False, fix_actions=fix_actions)


class BaseFixAction:
    pass


class FixActionFlow(BaseFixAction):
    __slots__ = ["flow_kind", "flow_params"]

    flow_kind: FlowKind
    flow_params: dict[str, Any]

    def __init__(self, kind: FlowKind | str, params: dict[str, Any] | None = None):
        self.flow_kind = FlowKind(kind)
        if params is None:
            params = {}
        self.flow_params = params
