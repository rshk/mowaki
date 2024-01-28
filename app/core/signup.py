import logging
from app.lib.normalize import normalize_email_address

from .notifications.signup import compose_signup_email
from app.io.email import send_email
from .auth import issue_login_token_for_email

logger = logging.getLogger(__name__)


def send_signup_link(address: str):
    """
    Send email containing a signup link to the specified email address.
    """

    address = normalize_email_address(address)
    token = issue_login_token_for_email(address)
    message = compose_signup_email(recipient=address, signup_token=token)

    logger.debug(f"Sending signup email to {address}")
    send_email(message)
