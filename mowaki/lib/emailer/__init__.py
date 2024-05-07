from urllib.parse import urlparse

from .base import BaseMailer
from .dummy import DummyMailer
from .smtp import SMTPMailer


def get_mailer_from_url(url: str) -> BaseMailer:
    """Create an appropriate Mailer instance from a URL

    Supported schemes:

    - smtp://username:password@host:port

        Send emails via an SMTP server.

    - dummy://

        Used for testing. Sent emails are instead stored in memory for
        further analysis.
    """

    parsed = urlparse(url)

    if parsed.scheme == "dummy":
        return DummyMailer()

    if parsed.scheme == "smtp":
        return SMTPMailer(
            host=parsed.hostname,
            port=parsed.port,
            username=parsed.username,
            password=parsed.password,
            starttls=True,
        )

    raise ValueError(f"Unsupported Mailer URL: {url}")
