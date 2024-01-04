from contextlib import contextmanager
from contextvars import ContextVar

from .base import BaseMailer

_outbox = ContextVar("dummy_outbox")


class DummyMailer(BaseMailer):
    def __init__(self):
        pass

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
