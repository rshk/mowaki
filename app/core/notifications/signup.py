import html
from email.message import EmailMessage
from urllib.parse import urlencode, urljoin

from app.config import get_config
from app.io.email import compose_html_email

SIGNUP_EMAIL_SUBJECT = "My App Signup"

SIGNUP_EMAIL_TEXT_TEMPLATE = """\
Welcome! Click this link to login:

    {login_url}
"""


SIGNUP_EMAIL_HTML_TEMPLATE = """\
<p>Welcome! Click this link to login:</p>
<p>
    <a href="{login_url}">Click here to login</a>
</p>
<p>If you prefer, copy-paste this URL in your browser instead:</p>
<p>{login_url}</p>
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

    login_url = make_login_url(signup_token)
    text_content = SIGNUP_EMAIL_TEXT_TEMPLATE.format(
        login_url=login_url,
    )
    # TODO: use an actual template engine like jinja
    html_content = SIGNUP_EMAIL_HTML_TEMPLATE.format(
        login_url=html.escape(login_url),
    )

    return compose_html_email(
        html_content=html_content,
        text_content=text_content,
        subject=SIGNUP_EMAIL_SUBJECT,
        to=recipient,
    )


def make_login_url(token):
    cfg = get_config()
    args = urlencode({"token": token})
    path = f"/login?{args}"
    return urljoin(cfg.frontend_url, path)
