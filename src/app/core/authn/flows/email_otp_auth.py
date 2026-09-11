import logging
import secrets
from typing import Self

from pydantic import BaseModel, EmailStr

from app.config import get_config
from app.core.authn.session import add_session_assertion
from app.exceptions import ItsABug
from app.lib.email_builder import EmailBuilder
from app.resources import get_mailer
from app.types.auth import assertions
from app.types.auth.auth_flow import FlowAction, FlowChallengeData

from .base import BaseFlowProcessor, FlowActionResultStatus, FlowState

logger = logging.getLogger(__name__)


class EmailOTPAuthFlowState(BaseModel):
    email: EmailStr | None = None
    code: str | None = None


class EmailOTPAuthFlowAction(BaseModel):
    email: EmailStr | None = None
    code: str | None = None


class EmailOTPAuthFlowProcessor(BaseFlowProcessor):
    __slots__ = ["state"]

    def __init__(self, state: EmailOTPAuthFlowState):
        self.state = state

    @classmethod
    def new(cls) -> Self:
        return cls(EmailOTPAuthFlowState())

    @classmethod
    def from_state(cls, state: FlowState) -> Self:
        _state = EmailOTPAuthFlowState.model_validate(state)
        return cls(_state)

    def dump_state(self) -> FlowState:
        _state = self.state.model_dump(mode="json")
        return FlowState(_state)

    def get_challenge_data(self) -> FlowChallengeData:
        # TODO: we should define a better schema for the "challenge data".
        # Right now, we just return a string indicating the flow state.

        if self.state.email is None:
            return FlowChallengeData({"state": "EMAIL_REQUIRED"})

        return FlowChallengeData({"state": "CODE_REQUIRED"})

    async def process(self, action: FlowAction) -> FlowActionResultStatus:
        _action = EmailOTPAuthFlowAction.model_validate(action)

        # STEP 1: get email address -> generate and send OTP code

        if self.state.email is None:
            if _action.email is not None:
                self.state.email = _action.email
                self.state.code = generate_otp_code()
                await compose_and_send_otp_challenge_email(
                    self.state.email, self.state.code
                )
            return FlowActionResultStatus.IN_PROGRESS

        # If an email address was provided (not required), it must
        # match the one we already have
        if _action.email is not None:  # noqa: SIM102
            if _action.email != self.state.email:
                raise ValueError("Specified email address does not match state")

        # STEP 2: verify OTP code

        if self.state.code is None:
            raise ItsABug("Missing OTP code")

        if _action.code is not None:
            # User provided an OTP code for verification
            if _action.code == self.state.code:
                # SUCCESS -> valid OTP code
                # Grant new assertion to the session
                await add_session_assertion(
                    assertions.Assertion.from_params(
                        assertions.EmailAuth(email_address=self.state.email)
                    )
                )
                return FlowActionResultStatus.SUCCESS

            else:
                # FAILED -> wrong OTP code
                return FlowActionResultStatus.FAILED

        return FlowActionResultStatus.IN_PROGRESS


async def compose_and_send_otp_challenge_email(email: str, code: str):
    # TODO: get language from session for translations.
    # TODO: Email composing logic needs some refactoring overall.
    # TODO: We should also send an HTML variant with a link.

    cfg = get_config()
    if cfg.development_mode:
        # For convenience, write the code to the logs.
        # Just make sure this is disabled in production!
        logger.info("Sending OTP to %s: %s", email, code)

    bld = EmailBuilder()
    bld.set_subject("Verify your email address")
    bld.add_recipient(email)
    bld.set_text_content(f"Your OTP code is: {code}")
    msg = bld.build()

    mailer = get_mailer()
    await mailer.send_message(msg)


def generate_otp_code(length: int = 6) -> str:
    """
    Generate OTP code.

    Returns a zero-padded string containing a securely-generated
    random number of ``length`` digits.
    """
    return format(secrets.randbelow(10**length)).rjust(length, "0")
