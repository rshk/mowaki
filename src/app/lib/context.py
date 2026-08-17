from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TypeVar

T = TypeVar("T")


@contextmanager
def scoped_context[T](ctxvar: ContextVar[T], value: T) -> Generator[None]:
    """Context manager to temporarily set the value of a ContextVar.

    Sets a ContextVar to a certain value and resets it at the end of
    the execution block, irrespective of whether an exception was
    raised or not.
    """

    token = ctxvar.set(value)
    try:
        yield
    finally:
        ctxvar.reset(token)
