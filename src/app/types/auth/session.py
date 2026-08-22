from __future__ import annotations

from datetime import UTC, datetime
from typing import NewType

from pydantic import Field, TypeAdapter

from app.lib.models import BaseModel
from app.types.user import UserID

from .assertions import Assertion

SessionID = NewType("SessionID", str)
SessionSecret = NewType("SessionSecret", str)
HashedSessionSecret = NewType("HashedSessionSecret", str)
SessionToken = NewType("SessionToken", str)

AssertionsList = TypeAdapter(list[Assertion])


class AuthSession(BaseModel):
    """Authentication session"""

    # Session identifier
    session_id: SessionID

    # Session "secret". Stored in the database as SHA256 hash, so
    # session tokens cannot be guessed from read-only access to the
    # database. Can be rotated to prevent session fixation attacks
    # (eg. when a new assertion is added to a session).
    session_secret: HashedSessionSecret

    # Date this session was created. Immutable.
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Date this session was last used.
    last_used_at: datetime | None = None

    # Expiration dates can be calculated on the fly, based on
    # creation_date and last_used_date.
    # We could add another (shorter-lived) expiration date to the
    # session, if the need arises to have sessions with even shorter
    # validity.

    # Session metadata.
    # Contains information about the device that initiated the session
    # (IP address, user agent, etc.).
    # Mostly for informative and auditing purposes.
    metadata: AuthSessionMetadata = Field(
        default_factory=lambda: AuthSessionMetadata.empty()
    )

    # Assertions associated with this session
    assertions: list[Assertion] = Field(default_factory=list)

    # Current user ID
    current_user_id: UserID | None = None


class AuthSessionMetadata(BaseModel):
    user_agent: str | None = None
    ip_address: str | None = None
    device_id: str | None = None
    device_fingerprint: str | None = None

    @classmethod
    def empty(cls) -> AuthSessionMetadata:
        return AuthSessionMetadata()


class SessionTokenData(BaseModel):
    __slots__ = ["session_id", "session_secret"]

    session_id: SessionID
    session_secret: SessionSecret
