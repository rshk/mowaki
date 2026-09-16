import logging
import secrets
from typing import Literal

from pydantic import BaseModel, EmailStr

from app.config import get_config
from app.core.authn.session import add_session_assertion
from app.exceptions import ItsABug
from app.lib.email_builder import EmailBuilder
from app.resources import get_mailer
from app.types.auth import assertions

from .processor import FlowActionResult, FlowProcessor

logger = logging.getLogger(__name__)


class EmailOTPAuthFlowState(BaseModel):
    email: EmailStr | None = None
    code: str | None = None


class EmailOTPAuthFlowAction(BaseModel):
    email: EmailStr | None = None
    code: str | None = None


class EmailOTPAuthFlowChallenge(BaseModel):
    next_step: Literal["EMAIL_REQUIRED", "CODE_REQUIRED"]


# Shortcut aliases
StateModel = EmailOTPAuthFlowState
ActionModel = EmailOTPAuthFlowAction
ChallengeModel = EmailOTPAuthFlowChallenge


PROCESSOR = FlowProcessor(
    state_model=StateModel,
    action_model=ActionModel,
    challenge_model=ChallengeModel,
)


@PROCESSOR.challenge_getter
def get_email_otp_auth_challenge(
    state: StateModel,
) -> ChallengeModel:
    if state.email is None:
        return ChallengeModel(next_step="EMAIL_REQUIRED")
    return ChallengeModel(next_step="CODE_REQUIRED")


@PROCESSOR.action_processor
async def process(
    state: StateModel, action: ActionModel
) -> FlowActionResult[StateModel]:

    # STEP 1: get email address -> generate and send OTP code

    if state.email is None:
        if action.email is not None:
            _email = action.email
            _code = generate_otp_code()
            await compose_and_send_otp_challenge_email(_email, _code)
            _state = StateModel(email=_email, code=_code)
            return FlowActionResult.new_state(_state)
        return FlowActionResult.new_state(state)  # unchanged

    # To prevent mistakes, if an email address (not required) was
    # provided in the response to a code challenge, make sure it
    # matches the stored one.
    if action.email is not None:  # noqa: SIM102
        if action.email != state.email:
            raise ValueError("Specified email address does not match state")

    # STEP 2: verify OTP code

    if state.code is None:
        raise ItsABug("Missing OTP code")

    if action.code is not None:
        # User provided an OTP for verification
        if action.code == state.code:
            # SUCCESS: user provided a valid OTP
            # Grant new assertion to the session
            await add_session_assertion(
                assertions.Assertion.from_params(
                    assertions.EmailAuth(email_address=state.email)
                )
            )
            return FlowActionResult.success()

        else:
            # FAILED -> wrong OTP code
            return FlowActionResult.failure()

    return FlowActionResult.new_state(state)  # unchanged


# --------------------------------------------------------------------


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
