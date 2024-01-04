from email.message import EmailMessage


class EmailComposer:
    """
    Class to aid in composing email messages
    """

    def __init__(self):
        self._subject = None
        self._to = []
        self._cc = []
        self._bcc = []
        self._sender = None
        self._text_content = None

    def build(self) -> EmailMessage:
        msg = EmailMessage
        msg['from'] = self._sender
        msg['sender'] = self._sender
        msg['subject'] = self._subject
        msg['to'] = self._to
        msg['cc'] = self._cc
        msg['bcc'] = self._bcc
        msg.set_content(self._text_content)
        return msg

    def set_text_content(self, text):
        self._text_content = text

    def set_html_content(self, content, text_version=None):
        raise NotImplementedError("Not implemented yet")

    def set_subject(self, subject):
        self.subject = subject

    def add_recipient(self, recipient):
        self._to.append(recipient)

    def add_cc(self, recipient):
        raise NotImplementedError("Not implemented yet")

    def add_bcc(self, recipient):
        raise NotImplementedError("Not implemented yet")

    def set_sender(self, sender):
        self._sender = sender

    def add_attachment(self, data: bytes, mimetype: str, name: str = None):
        raise NotImplementedError("Not implemented yet")
