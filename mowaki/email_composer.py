"""
High level functions to compose emails.

See https://docs.python.org/3/library/email.examples.html
"""

from email.utils import make_msgid
from email.message import EmailMessage
from typing import Iterable


def compose_text_email(
    text: str, *, subject: str, sender: str, to: str | Iterable[str]
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(text)
    return msg


def compose_html_email(
    html_content, *, subject: str, sender: str, to: str, text_content=None
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")
    return msg
