"""
Utilities for the Login Flow
"""

import logging
import secrets

from app.config import get_config
from app.core.authn.session import add_session_assertion
from app.lib.email_builder import EmailBuilder
from app.resources import get_mailer
from app.types.auth import assertions

logger = logging.getLogger(__name__)


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


def generate_otp(length: int = 6) -> str:
    """
    Generate OTP code.

    Returns a zero-padded string containing a securely-generated
    random number of ``length`` digits.
    """
    _number = secrets.randbelow(10**length)
    return format(_number).rjust(length, "0")


async def do_add_session_assertion(email: str):
    params = assertions.EmailAuth(email_address=email)
    assertion = assertions.Assertion.from_params(params)
    await add_session_assertion(assertion)
