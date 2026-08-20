"""
Email OTP based authentication
"""

import secrets

from app.core.authn.challenge import create_challenge, lock_challenge_for_processing
from app.core.authn.session import add_session_assertion, invalidate_current_session
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

    # We're creating a new session from now on!
    await invalidate_current_session()

    params = EmailOTPChallengeStateParams(
        email_address=address,
        otp_code=generate_otp_code(),
    )

    challenge_id = await create_challenge(params)

    return EmailOTPChallengeRequest(challenge_id=challenge_id)


async def process_email_otp_challenge_response(
    response: EmailOTPChallengeResponse,
) -> bool:

    async with lock_challenge_for_processing(response.challenge_id) as challenge:
        params = challenge.params

        if not isinstance(params, EmailOTPChallengeStateParams):
            # User might tamper with this.
            # We should probably log this with a "potential tampering" tag of some sort.
            return False

        if response.otp_code == params.otp_code:
            params = assertions.EmailOTP(email_address=params.email_address)
            assertion = assertions.Assertion.from_params(params)
            await add_session_assertion(assertion)
            return True  # success

    return False


def generate_otp_code(length: int = 6) -> str:
    """
    Generate a secure random number of ``length`` digits
    """
    return format(secrets.randbelow(10**length)).rjust(length, "0")
