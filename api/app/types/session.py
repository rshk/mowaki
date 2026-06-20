from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Literal, NewType, Self

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    import sqlalchemy

    from app.types.challenges import AuthChallengeState
    from app.types.user import UserID

SessionID = NewType("SessionID", str)
SessionSecret = NewType("SessionSecret", str)
HashedSessionSecret = NewType("HashedSessionSecret", str)
SessionToken = NewType("SessionToken", str)


class AuthSession(BaseModel):
    """Authentication session"""

    # Used to identify the session in the database
    session_id: SessionID

    # Used to prevent session fixation attacks, eg. when adding grants.
    session_secret: HashedSessionSecret

    # Date this session was created. Immutable.
    creation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Date this session was last used.
    last_used_date: datetime | None = None

    # Expiration dates can be calculated on the fly

    # Metadata about the user / device / location where the session
    # was created. Mostly informative, can be used for advanced
    # security checks.
    metadata: AuthSessionMetadata = Field(
        default_factory=lambda: AuthSessionMetadata.empty()
    )

    # Auth data associated with the session.
    # Using a sub-field makes storage in the database easier.
    data: AuthSessionData = Field(default_factory=lambda: AuthSessionData.empty())

    @classmethod
    def from_row(cls, row: sqlalchemy.Row) -> Self:
        return cls.model_validate(row._asdict())


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

    # Authorization grants associated with this session.
    grants: list[AuthGrant] = Field(default_factory=list)

    # Authentication challenges associated with this session.
    challenges: list[AuthChallengeState] = Field(default_factory=list)

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
