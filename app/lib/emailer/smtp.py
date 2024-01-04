import smtplib

from .base import BaseMailer


class SMTPMailer(BaseMailer):
    def __init__(self, host, port=25, starttls=True, username=None, password=None):
        self._host = host
        self._port = port
        self._starttls = starttls
        self._username = username
        self._password = password

    def send_message(self, msg):
        with smtplib.SMTP(self._host, port=self._port) as smtp:
            if self._starttls:
                smtp.starttls()
            if self._username or self._password:
                smtp.login(self._username, self._password)
            smtp.send_message(msg)
