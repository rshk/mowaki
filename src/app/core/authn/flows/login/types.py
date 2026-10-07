import logging
import secrets
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator, EmailStr, Field, TypeAdapter

from app.config import get_config
from app.core.authn.session import add_session_assertion
from app.exceptions import ItsABug
from app.lib.email_builder import EmailBuilder
from app.resources import get_mailer
from app.types.auth import assertions

from ..processor import FlowActionResult, FlowProcessor

logger = logging.getLogger(__name__)


class LoginFlowState(BaseModel):
    email: EmailStr | None = None
    otp: str | None = None


StateModel = LoginFlowState


# Actions ------------------------------------------------------------

class EmailAddrAction:
    # action: Annotated[Literal["email_address"], Field(default="email_address")]
    action: Literal["email_address"] = "email_address"


class WebauthnInitAction:
    action: Literal["webauthn_init"] = "webauthn_init"


ActionType = Annotated[EmailAddrAction | WebauthnInitAction, Discriminator("action")]
ActionModel = TypeAdapter(ActionType)


# Challenges ---------------------------------------------------------

class InitialChallenge:
    kind: Literal["init"] = "init"
    email_auth_available: bool
    webauthn_available: bool


class EmailOtpChallenge:
    kind: Literal["email_otp"] = "email_otp"


ChallengeType = Annotated[InitialChallenge | EmailOtpChallenge, Discriminator("kind")]
ChallengeModel = TypeAdapter(ChallengeType)
