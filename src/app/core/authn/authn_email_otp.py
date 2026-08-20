"""
Email OTP based authentication
"""

import secrets

from app.core.authn.challenge import create_challenge
from app.core.authn.exceptions import (
    ChallengeResponseInvalid,
)
from app.core.authn.session import add_session_assertion, invalidate_current_session
from app.lib.email_builder import EmailBuilder
from app.resources import get_mailer
from app.types.auth import assertions
from app.types.auth.challenges import (
    EmailOTPChallengeRequest,
    EmailOTPChallengeResponse,
    EmailOTPChallengeStateParams,
)


async def initiate_with_email_otp(address: str) -> EmailOTPChallengeRequest:
    """
    Initiate authentication with an email OTP
    """

    await invalidate_current_session()
    return await upgrade_with_email_otp(address)


async def upgrade_with_email_otp(address: str) -> EmailOTPChallengeRequest:
    """
    Upgrade session with a new email OTP
    """

    otp_code = generate_otp_code()
    params = EmailOTPChallengeStateParams(email_address=address, otp_code=otp_code)

    challenge_id = await create_challenge(params)

    await compose_and_send_otp_challenge_email(address=address, otp_code=otp_code)

    return EmailOTPChallengeRequest(challenge_id=challenge_id)


async def process_email_otp_challenge_response(
    params: EmailOTPChallengeStateParams,
    response: EmailOTPChallengeResponse,
):

    if response.otp_code == params.otp_code:
        aparams = assertions.EmailOTP(email_address=params.email_address)
        assertion = assertions.Assertion.from_params(aparams)
        await add_session_assertion(assertion)
        return True  # success

    raise ChallengeResponseInvalid(f"Challenge ID: {response.challenge_id}")


def generate_otp_code(length: int = 6) -> str:
    """
    Generate a secure random number of ``length`` digits
    """
    return format(secrets.randbelow(10**length)).rjust(length, "0")


async def compose_and_send_otp_challenge_email(address: str, otp_code: str):
    # TODO: get language from session for translations
    # TODO: we should probably have a non-blocking SMTP client instead!

    bld = EmailBuilder()
    bld.set_subject("Verify your email address")
    bld.add_recipient(address)
    bld.set_text_content(f"Your OTP code is: {otp_code}")
    msg = bld.build()

    mailer = get_mailer()
    mailer.send_message(msg)
