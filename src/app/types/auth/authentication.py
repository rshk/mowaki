from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated, Literal, NewType

from pydantic import BaseModel, Discriminator, Field

from app.types.user import UserID

AssertionID = NewType("AssertionID", uuid.UUID)


class AuthnLevel:
    pass


# Assertions ---------------------------------------------------------


class Assertion(BaseModel):
    """Authentication assertion"""

    id: AssertionID = Field(default_factory=lambda: AssertionID(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    params: AssertionParams = Field()


class EmailVerified(BaseModel):
    kind: Literal["email"]
    email_address: str

    # If this email address was attached to a user, list it here
    user_id: UserID | None = None


class PasskeyVerified(BaseModel):
    kind: Literal["passkey"]
    passkey_id: PasskeyID
    user_id: UserID


class IsUser(BaseModel):
    kind: Literal["user"]
    user_id: UserID


AssertionParams = Annotated[EmailVerified | PasskeyVerified, Discriminator("kind")]


# Passkey data -------------------------------------------------------

PasskeyID = NewType("PasskeyID", str)


class PasskeyData(BaseModel):
    credential_id: PasskeyID
    public_key: str
    sign_count: int
