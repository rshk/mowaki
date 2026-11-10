import logging
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator, EmailStr, TypeAdapter

logger = logging.getLogger(__name__)


class LoginFlowState(BaseModel):
    email: EmailStr | None = None
    otp: str | None = None


StateModel = LoginFlowState


# Actions ------------------------------------------------------------


class EmailAddrAction(BaseModel):
    kind: Literal["email_address"] = "email_address"
    email: EmailStr


class OtpAction(BaseModel):
    kind: Literal["otp_response"] = "otp_response"
    otp: str


class WebauthnInitAction(BaseModel):
    kind: Literal["webauthn_init"] = "webauthn_init"


ActionType = Annotated[
    EmailAddrAction | OtpAction | WebauthnInitAction, Discriminator("kind")
]
ActionModel = TypeAdapter(ActionType)
ActionTypeAdapter = TypeAdapter(ActionType)


# Challenges ---------------------------------------------------------


class InitialChallenge(BaseModel):
    kind: Literal["init"] = "init"
    email_auth_available: bool
    webauthn_available: bool


class EmailOtpChallenge(BaseModel):
    kind: Literal["email_otp"] = "email_otp"


ChallengeType = Annotated[InitialChallenge | EmailOtpChallenge, Discriminator("kind")]
ChallengeModel = TypeAdapter(ChallengeType)
ChallengeTypeAdapter = TypeAdapter(ChallengeType)
