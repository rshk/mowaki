import logging
import secrets
from typing import Self

from app.core.authn.session import add_session_assertion
from app.lib.email_builder import EmailBuilder
from app.resources import get_mailer
from app.types.auth import assertions
from app.types.auth.auth_flow import FlowAction

from .base import BaseFlowProcessor, FlowState, FlowStatus

logger = logging.getLogger(__name__)


FLD_EMAIL = "email_address"
FLD_OTP_CODE = "otp_code"


class EmailOTPAuthFlowProcessor(BaseFlowProcessor):
    def __init__(
        self,
        email_address: str | None = None,
        otp_code: str | None = None,
    ):
        self.email_address = email_address
        self.otp_code = otp_code

    @classmethod
    def from_state(cls, state: FlowState) -> Self:
        kwargs = {
            FLD_EMAIL: state.get(FLD_EMAIL),
            FLD_OTP_CODE: state.get(FLD_OTP_CODE),
        }
        return cls(**kwargs)

    def dump_state(self) -> FlowState:
        return FlowState(
            {
                FLD_EMAIL: self.email_address,
                FLD_OTP_CODE: self.otp_code,
            }
        )

    def get_challenge_data(self) -> FlowState:
        # TODO: still return something along the lines of "check your email"?
        # We might want to define a schema for  this.
        return FlowState({})

    async def process(self, action: FlowAction) -> FlowStatus:
        if (email_addr := action.get(FLD_EMAIL)) is not None:
            if self.email_address is None:
                # User just provided an email address to send code to
                self.email_address = email_addr
                self.otp_code = generate_otp_code()
                await compose_and_send_otp_challenge_email(
                    self.email_address, self.otp_code
                )

            elif email_addr != self.email_address:
                raise ValueError("Mismatching email address specified")

        if (otp_code := action.get(FLD_OTP_CODE)) is not None:
            # User provided an OTP code for verification
            if self.email_address is None:
                raise ValueError(
                    "Cannot provide an OTP code without an email address first"
                )

            if self.otp_code == otp_code:
                # SUCCESS -> valid otp
                # Grant new assertion to the session
                await add_session_assertion(
                    assertions.Assertion.from_params(
                        assertions.EmailOTP(email_address=self.email_address)
                    )
                )

                return FlowStatus.SUCCESS

            else:
                # FAILED -> wrong OTP code
                return FlowStatus.FAILED

        return FlowStatus.IN_PROGRESS


async def compose_and_send_otp_challenge_email(address: str, otp_code: str):
    # TODO: get language from session for translations
    # TODO: we should probably have a non-blocking SMTP client instead!

    logger.info("Sending OTP challenge to %s with code %s", address, otp_code)

    bld = EmailBuilder()
    bld.set_subject("Verify your email address")
    bld.add_recipient(address)
    bld.set_text_content(f"Your OTP code is: {otp_code}")
    msg = bld.build()

    mailer = get_mailer()
    mailer.send_message(msg)


def generate_otp_code(length: int = 6) -> str:
    """
    Generate OTP code.

    Returns a zero-padded string containing a securely-generated
    random number of ``length`` digits.
    """
    return format(secrets.randbelow(10**length)).rjust(length, "0")
