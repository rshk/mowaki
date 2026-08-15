from __future__ import annotations


import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, NewType, Self

from pydantic import BaseModel, Field

from app.types.auth.authentication import Assertion

from .user import UserID

SessionID = NewType("SessionID", str)
SessionSecret = NewType("SessionSecret", str)
HashedSessionSecret = NewType("HashedSessionSecret", str)
SessionToken = NewType("SessionToken", str)


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
    creation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Date this session was last used.
    last_used_date: datetime | None = None

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

    # Authentication data associated to the session.
    # Stored in a separate object so it's easier to pass around on its
    # own.
    data: AuthSessionData = Field(default_factory=lambda: AuthSessionData.empty())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate(data)


class AuthSessionMetadata(BaseModel):
    user_agent: str | None = None
    ip_address: str | None = None
    device_id: str | None = None
    device_fingerprint: str | None = None

    @classmethod
    def empty(cls) -> AuthSessionMetadata:
        return AuthSessionMetadata()


class AuthSessionData(BaseModel):
    # User who performed the authentication for this session. Immutable.
    authenticated_user_id: UserID | None = None

    # Current user ID. Might differ from authenticated_user_id, eg. in
    # case of an admin impersonating a different user.
    current_user_id: UserID | None = None

    # Authorization assertions
    assertions: list[Assertion] = Field(default_factory=list)

    # # Authorization grants associated with this session.
    # grants: list[AuthGrant] = Field(default_factory=list)

    # challenges: ...

    @classmethod
    def empty(cls) -> AuthSessionData:
        return AuthSessionData()


class SessionTokenData(BaseModel):
    __slots__ = ["session_id", "session_secret"]

    session_id: SessionID
    session_secret: SessionSecret


AuthGrantId = NewType("AuthGrantId", uuid.UUID)


class BaseAuthGrant(BaseModel):
    """Base for auth grants"""

    id: AuthGrantId
    expires_at: datetime | None


class UserLoginGrant(BaseAuthGrant):
    kind: Literal["login"]
    user_id: UserID


class UserSudoModeGrant(BaseAuthGrant):
    kind: Literal["sudo"]
    user_id: UserID


# These can be added as needed by the application
AuthGrant = Annotated[UserLoginGrant | UserSudoModeGrant, Field(discriminator="kind")]
