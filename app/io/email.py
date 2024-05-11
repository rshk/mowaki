from email.message import EmailMessage

from app.config import get_config
from app.resources import get_resources
from mowaki.email_composer import compose_html_email as _compose_html_email


def send_email(msg: EmailMessage):
    """Send an email message using the configured mailer"""

    resources = get_resources()
    mailer = resources.mailer
    mailer.send_message(msg)


def compose_html_email(*args, **kwargs):
    cfg = get_config()
    kwargs.setdefault("sender", cfg.email_sender)
    return _compose_html_email(**kwargs)
