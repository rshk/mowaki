from __future__ import annotations

import abc
import smtplib
import typing
from contextlib import contextmanager
from contextvars import ContextVar
from urllib.parse import ParseResult, parse_qs, urlparse

# ********************************************************************
#                        TODO: async support
# ********************************************************************
# Add async support via aiosmtplib:
# - https://pypi.org/project/aiosmtplib/
# - https://aiosmtplib.readthedocs.io/en/stable/client.html
#
# This involves converting the base mailer class to async, but
# shouldn't be a big task.
# Also, make it the new default for smtp(s)://, move the old one to
# something like smtp+legacy:// ?
# Make sure to use start_tls (default) and NOT use_tls btw, or it will
# fail. Also test it with a few real world services.
# ********************************************************************

# ----------------------- SMTP only support? -------------------------
# We could simplify this whole code to only support SMTP, since we use
# the slurpmail for development, but the low-overhead "dummy" mailer
# is still useful for testing, without having to constantly resort to
# mailslurper.
# Also, people might want to use a 3rd party service via API instead.
# --------------------------------------------------------------------


def get_mailer_from_url(url: str) -> BaseMailer:
    """Create an appropriate Mailer instance from a URL

    Supported schemes:

    - smtp://username:password@host:port?tls=true

        Send emails via SMTP.

    - dummy://

        Used for testing. Store emails in memory for further analysis.
    """

    parsed = urlparse(url)

    if parsed.scheme == "dummy":
        return DummyMailer.from_url(parsed)

    if parsed.scheme in ("smtp", "smtps"):
        return SMTPMailer.from_url(parsed)

    raise ValueError(f"Unsupported Mailer URL: {url}")


if typing.TYPE_CHECKING:
    from email.message import Message


class BaseMailer(metaclass=abc.ABCMeta):
    """Base for mailer implementations"""

    @classmethod
    @abc.abstractmethod
    def from_url(cls, url: ParseResult) -> typing.Self:
        pass

    @abc.abstractmethod
    def send_message(self, msg: Message):
        pass


class SMTPMailer(BaseMailer):
    _host: str
    _port: int
    _starttls: bool
    _username: str | None
    _password: str | None

    def __init__(
        self,
        host: str,
        port: int | None = None,
        starttls: bool = True,
        username: str | None = None,
        password: str | None = None,
    ):
        self._host = host
        # Setting port to 0 will cause smtplib to use the default port
        self._port = port or 0
        self._starttls = starttls
        self._username = username
        self._password = password

    @classmethod
    def from_url(cls, url: ParseResult):
        query = parse_qs(url.query)
        starttls = (url.scheme == "smtps") or (query.get("tls") in ("1", "true"))

        if url.hostname is None:
            raise ValueError("Missing hostname")

        return SMTPMailer(
            host=url.hostname,
            port=url.port,
            username=url.username,
            password=url.password,
            starttls=starttls,
        )

    def send_message(self, msg):
        with smtplib.SMTP(self._host, port=self._port) as smtp:
            if self._starttls:
                smtp.starttls()
            if self._username or self._password:
                smtp.login(self._username or "", self._password or "")
            smtp.send_message(msg)


_outbox = ContextVar("dummy_outbox")


class DummyMailer(BaseMailer):
    """
    Dummy mailer class, for testing.

    Stores emails in a context-local variable, if set via
    record_sent_emails().
    """

    def __init__(self):
        pass

    @classmethod
    def from_url(cls, url: ParseResult):
        return DummyMailer()

    def send_message(self, msg):
        try:
            outbox = _outbox.get()
        except LookupError:
            pass
        else:
            outbox.append(msg)


@contextmanager
def record_sent_emails():
    """
    Context manager to record emails sent by dummy mailers.

    Most useful for testing. Will intercept all mail sent by dummy
    mailers in the current thread / execution context.
    """
    outbox = []
    token = _outbox.set(outbox)
    yield outbox
    _outbox.reset(token)
