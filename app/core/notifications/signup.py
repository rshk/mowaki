from email.message import EmailMessage
from urllib.parse import urlencode, urljoin

from app.config import get_config
from app.io.email import get_composer

SIGNUP_EMAIL_TEXT_TEMPLATE = """\
Welcome! Click this link to login:

    {login_url}
"""


def compose_signup_email(*, recipient, signup_token) -> EmailMessage:
    """
    Compose a signup email, containing a "magic link" to login.

    Args:

        recipient:
            Email address of the recipient.

        signup_token:
            Signup token to be used to create the signup link.

    Returns:
        The generate email message.
    """

    composer = get_composer()
    composer.set_subject("My App Signup")
    composer.add_recipient(recipient)
    login_url = make_login_url(signup_token)
    composer.set_text_content(SIGNUP_EMAIL_TEXT_TEMPLATE.format(login_url=login_url))
    return composer.build()


def make_login_url(token):
    cfg = get_config()
    args = urlencode({"token": token})
    path = f"/login?{args}"
    return urljoin(cfg.frontend_url, path)
