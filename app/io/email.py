from email.message import EmailMessage

from app.config import get_config
from app.resources import get_resources
from mowaki.email_composer import EmailComposer


def get_composer() -> EmailComposer:
    """Get an email composer with sender prepopulated from configuration"""

    cfg = get_config()
    composer = EmailComposer()
    composer.set_sender(cfg.email_sender)
    return composer


def send_email(msg: EmailMessage):
    """Send an email message using the configured mailer"""

    resources = get_resources()
    mailer = resources.mailer
    mailer.send_message(msg)
