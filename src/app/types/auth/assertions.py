from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated, Literal, NewType

from pydantic import BaseModel, Discriminator, Field

from app.types.user import UserID

from .passkey_data import PasskeyID

# Assertions ---------------------------------------------------------

AssertionID = NewType("AssertionID", uuid.UUID)


class Assertion(BaseModel):
    """Authentication assertion"""

    id: AssertionID = Field(default_factory=lambda: AssertionID(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    params: AssertionParams = Field()


class EmailOTP(BaseModel):
    """Solved an email-based OTP challenge"""

    kind: Literal["email-otp"]
    email_address: str

    # If this email address was attached to a user, list it here
    user_id: UserID | None = None


class PasskeyAuth(BaseModel):
    """Authenticated using a passkey"""

    kind: Literal["passkey"]
    passkey_id: PasskeyID
    user_id: UserID


AssertionParams = Annotated[EmailOTP | PasskeyAuth, Discriminator("kind")]
