"""
Authentication challenges
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated, Literal, NewType

from pydantic import Discriminator, Field, TypeAdapter

from app.lib.models import BaseModel

ChallengeID = NewType("ChallengeID", uuid.UUID)


# Challenge State ----------------------------------------------------


class ChallengeState(BaseModel):
    challenge_id: ChallengeID = Field(default_factory=lambda: ChallengeID(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = Field(default=None)
    params: ChallengeStateParams = Field()


class EmailOTPChallengeStateParams(BaseModel):
    kind: Literal["email-otp"] = Field(default="email-otp")
    email_address: str
    otp_code: str


class PasskeyAuthChallengeStateParams(BaseModel):
    kind: Literal["passkey-auth"] = Field(default="passkey-auth")


class PasskeyEnrollChallengeStateParams(BaseModel):
    kind: Literal["passkey-enroll"] = Field(default="passkey-enroll")


ChallengeStateParams = Annotated[
    EmailOTPChallengeStateParams
    | PasskeyAuthChallengeStateParams
    | PasskeyEnrollChallengeStateParams,
    Discriminator("kind"),
]

ChallengeStateParamsTA = TypeAdapter(ChallengeStateParams)


# Challenge Request/Response -----------------------------------------


class EmailOTPChallengeRequest(BaseModel):
    kind: Literal["email-otp"] = Field(default="email-otp")
    challenge_id: ChallengeID


class EmailOTPChallengeResponse(BaseModel):
    kind: Literal["email-otp"] = Field(default="email-otp")
    challenge_id: ChallengeID
    otp_code: str


class PasskeyAuthChallengeRequest(BaseModel):
    kind: Literal["passkey-auth"] = Field(default="passkey-auth")
    challenge_id: ChallengeID


class PasskeyAuthChallengeResponse(BaseModel):
    kind: Literal["passkey-auth"] = Field(default="passkey-auth")
    challenge_id: ChallengeID


class PasskeyEnrollChallengeRequest(BaseModel):
    kind: Literal["passkey-enroll"] = Field(default="passkey-enroll")
    challenge_id: ChallengeID


class PasskeyEnrollChallengeResponse(BaseModel):
    kind: Literal["passkey-enroll"] = Field(default="passkey-enroll")
    challenge_id: ChallengeID


ChallengeRequest = Annotated[
    EmailOTPChallengeRequest
    | PasskeyAuthChallengeRequest
    | PasskeyEnrollChallengeRequest,
    Discriminator("kind"),
]

ChallengeResponse = Annotated[
    EmailOTPChallengeResponse
    | PasskeyAuthChallengeResponse
    | PasskeyEnrollChallengeResponse,
    Discriminator("kind"),
]
