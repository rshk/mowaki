from __future__ import annotations

import secrets
import uuid
from datetime import datetime
from typing import Annotated, Literal, NewType

from pydantic import BaseModel, Field

from app.types.user import UserID

SessionID = NewType("SessionID", str)


class AuthSession(BaseModel):
    """Authentication session"""

    session_id: SessionID

    soft_expiration_date: datetime | None = None
    hard_expiration_date: datetime | None = None

    metadata: AuthSessionMetadata = Field(
        default_factory=lambda: AuthSessionMetadata.empty()
    )
    data: AuthSessionData = Field(default_factory=lambda: AuthSessionData.empty())


class AuthSessionMetadata(BaseModel):
    user_agent: str | None = None
    ip_address: str | None = None
    device_id: str | None = None
    device_fingerprint: str | None = None

    @classmethod
    def empty(cls) -> AuthSessionMetadata:
        return AuthSessionMetadata()


class AuthSessionData(BaseModel):
    grants: list[AuthGrant] = Field(default_factory=list)

    @classmethod
    def empty(cls) -> AuthSessionData:
        return AuthSessionData()


class BaseAuthGrant(BaseModel):
    """Base for auth grants"""

    id: uuid.UUID
    expires_at: datetime | None


class UserLoginGrant(BaseAuthGrant):
    kind: Literal["login"]
    user_id: UserID


class UserSudoModeGrant(BaseAuthGrant):
    kind: Literal["sudo"]
    user_id: UserID


# These can be added as needed by the application
AuthGrant = Annotated[UserLoginGrant | UserSudoModeGrant, Field(discriminator="kind")]
