from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any


@contextmanager
def contextvar_contextmanager(ctxvar: ContextVar, value: Any):
    """
    ContextVar context manager.

    Sets a ContextVar to a certain value and resets it at the end of
    the execution block, irrespective of whether an exception was
    raised or not.
    """

    token = ctxvar.set(value)
    try:
        yield
    finally:
        ctxvar.reset(token)
