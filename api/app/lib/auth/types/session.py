"""
Session management
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, NewType
from uuid import UUID

from pydantic import BaseModel, Field


SessionID = NewType("SessionID", str)


class AuthSession(BaseModel):
    session_id: SessionID

    # Currently selected user ID.
    # The session might support authenticating as multiple users, but
    # only one will be "current" at the moment.
    current_user_id: UUID | None = None

    # This gets pushed forward every time credentials are used
    soft_expiration_date: datetime | None = None

    # This is a hard limit for session expiration; user will need to
    # reauthenticate past this date.
    # If set to None, session will never expire.
    hard_expiration_date: datetime | None = None


class AuthGrant(BaseModel):
    id: str
    kind: str
    expires: datetime | None = None
    params: dict[str, Any] = Field(default_factory=dict)
