"""
Convenience utilities for building email messages.
"""

from email.message import EmailMessage

from app.const import DEFAULT_EMAIL_SENDER


class EmailBuilder:
    subject: str | None
    sender: str | None
    recipients: list[str]
    text_content: str | None
    html_content: str | None

    def __init__(self):
        self.subject = None
        self.sender = DEFAULT_EMAIL_SENDER
        self.recipients = []
        self.text_content = None
        self.html_content = None

    def build(self) -> EmailMessage:
        msg = EmailMessage()

        msg["Subject"] = self.subject or ""

        if self.sender is None:
            raise ValueError("A sender must be provided")
        msg["From"] = self.sender

        if len(self.recipients) < 1:
            raise ValueError("At least one recipient must be provided")
        msg["To"] = ", ".join(self.recipients)

        # TODO: automatically convert HTML -> text, if a text variant
        # wasn't provided.
        msg.set_content(self.text_content or "")

        if self.html_content is not None:
            msg.add_alternative(self.html_content, subtype="html")

        return msg

    def set_subject(self, subject: str):
        self.subject = subject

    def set_sender(self, sender: str):
        self.sender = sender

    def add_recipient(self, recipient: str):
        self.recipients.append(recipient)

    def set_text_content(self, text: str):
        self.text_content = text

    def set_html_content(self, text: str):
        self.html_content = text
