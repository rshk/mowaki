from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AuthzResult:
    """Result of an authorization check"""

    allowed: bool
    corrective_actions: list[BaseCorrectiveAction] = field(default_factory=list)

    @classmethod
    def allow(cls):
        return cls(allowed=True)

    @classmethod
    def deny(cls, corrective_actions: list[Any] | None = None):
        if corrective_actions is None:
            corrective_actions = []
        return cls(allowed=False, corrective_actions=corrective_actions)


class BaseCorrectiveAction:
    """Base object for "corrective actions".

    Corrective actions represent actions that can be taken to remedy a
    failed authorization attempt.
    """
