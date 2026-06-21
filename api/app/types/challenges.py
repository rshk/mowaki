from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, NewType

from pydantic import BaseModel, Discriminator

ChallengeID = NewType("ChallengeID", str)


# *Challenge -> sent to the user
# *State -> stored in the session
# *Response -> sent by the client


class BaseChallengeState(BaseModel):
    challenge_id: ChallengeID
    created_at: datetime
    expires_at: datetime
    response: BaseChallengeResponse | None = None


class BaseChallengeRequest(BaseModel):
    challenge_id: ChallengeID


class BaseChallengeResponse(BaseModel):
    challenge_id: ChallengeID


# Email OTP challenge ------------------------------------------------


class EmailOtpChallenge(BaseChallengeRequest):
    challenge_id: ChallengeID
    kind: Literal["email"]


class EmailOtpState(BaseChallengeState):
    challenge_id: ChallengeID
    kind: Literal["email"]
    email: str
    otp: str


class EmailOtpResponse(BaseChallengeResponse):
    challenge_id: ChallengeID
    kind: Literal["email"]
    otp: str


# WebAuthn -----------------------------------------------------------


class WebAuthnChallenge(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["webauthn"]
    # TODO: add webauthn parameters


class WebAuthnState(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["webauthn"]
    expires_at: datetime
    # TODO: add webauthn parameters


class WebAuthnChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["webauthn"]
    # TODO: add webauthn fields


# Time-based OTP -----------------------------------------------------


class TotpChallenge(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["totp"]
    # TODO


class TotpChallengeState(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["totp"]
    expires_at: datetime
    # TODO


class TotpChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["totp"]
    code: str


# --------------------------------------------------------------------


AuthChallenge = Annotated[
    EmailOtpChallenge | WebAuthnChallenge | TotpChallenge,
    Discriminator("kind"),
]
AuthChallengeState = Annotated[
    EmailOtpState | WebAuthnState | TotpChallengeState,
    Discriminator("kind"),
]
AuthChallengeResponse = Annotated[
    EmailOtpResponse | WebAuthnChallengeResponse | TotpChallengeResponse,
    Discriminator("kind"),
]
