from __future__ import annotations

import abc
from datetime import datetime
from typing import Annotated, Literal, NewType, Self
import uuid

from pydantic import BaseModel, Discriminator, TypeAdapter

ChallengeID = NewType("ChallengeID", uuid.UUID)


class Challenge[KIND](BaseModel):
    """Challenge state, stored in a flow"""

    challenge_id: ChallengeID

    # Discriminator
    kind: KIND

    created_at: datetime
    expires_at: datetime | None = None

    # Internal state of the challenge
    state: BaseChallengeState[KIND]

    # Response submitted by the user, if any
    result: BaseChallengeResult[KIND] | None = None


ListOfChallenges = TypeAdapter(list[Challenge])


# Base classes -------------------------------------------------------


class BaseChallengeState[KIND](BaseModel):
    """Internal state for the challenge, eg. OTP code to be verified"""

    kind: KIND


class BaseChallengeResult[KIND](BaseModel):
    """Outcome of verifying the user response"""

    kind: KIND
    is_success: bool
    # ... subclasses may add extra fields


class BaseChallengeRequest[KIND](BaseModel):
    """User-facing request"""

    challenge_id: ChallengeID
    kind: KIND

    @classmethod
    def from_challenge(cls, challenge: Challenge[KIND]) -> Self:
        return cls(challenge_id=challenge.challenge_id, kind=cls.kind)


class BaseChallengeResponse(BaseModel):
    """Response to the challenge submitted by the user"""

    challenge_id: ChallengeID
    # ... subclasses need to add extra fields


# Request email address ----------------------------------------------

# Ask for an email address, to be used for creating more challenges

class EmailAddrChallenge(Challenge):
    kind: Literal["email-addr"] = "email-addr"


class EmailAddrState(BaseChallengeState):
    kind: Literal["email-addr"] = "email-addr"


class EmailAddrResult(BaseChallengeResult):
    kind: Literal["email-addr"] = "email-addr"
    email: str


class EmailAddrRequest(BaseChallengeRequest):
    kind: Literal["email-addr"] = "email-addr"


class EmailAddrResponse(BaseChallengeResponse):
    kind: Literal["email-addr"] = "email-addr"
    email: str


# OTB-based email verification ---------------------------------------


class EmailOtpChallenge(Challenge):
    kind: Literal["email-otp"] = "email-otp"


class EmailOtpState(BaseChallengeState):
    kind: Literal["email-otp"] = "email-otp"
    email: str
    otp: str


class EmailOtpResult(BaseChallengeResult):
    kind: Literal["email-otp"] = "email-otp"


class EmailOtpRequest(BaseChallengeRequest):
    kind: Literal["email-otp"] = "email-otp"


class EmailOtpResponse(BaseChallengeResponse):
    kind: Literal["email-otp"] = "email-otp"
    otp: str


# WebAuthn -----------------------------------------------------------


class PasskeyChallenge(Challenge):
    kind: Literal["passkey"] = "passkey"


class PasskeyState(BaseChallengeState):
    kind: Literal["passkey"] = "passkey"
    # TODO: add webauthn parameters


class PasskeyResult(BaseChallengeResult):
    kind: Literal["passkey"] = "passkey"


class PasskeyRequest(BaseChallengeRequest):
    kind: Literal["passkey"] = "passkey"
    # TODO: add webauthn parameters


class PasskeyResponse(BaseChallengeResponse):
    kind: Literal["passkey"] = "passkey"


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


# AuthChallenge = Annotated[
#     EmailOtpChallenge | WebAuthnChallenge | TotpChallenge,
#     Discriminator("kind"),
# ]
# AuthChallengeState = Annotated[
#     EmailOtpState | WebAuthnState | TotpChallengeState,
#     Discriminator("kind"),
# ]
# AuthChallengeResponse = Annotated[
#     EmailOtpResponse | WebAuthnChallengeResponse | TotpChallengeResponse,
#     Discriminator("kind"),
# ]
