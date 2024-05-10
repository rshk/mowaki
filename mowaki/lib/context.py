"""
Utilities for context vars

Example:

    @dataclass
    class Config:
        FOO: str
        BAR: str

    mycontext = TypedContextVar[Config]("mycontext")

    cfg = Config(...)

    with mycontext.context(cfg):
        cfg2 = mycontext.get()

        assert cfg2 is cfg
"""

from contextlib import AbstractContextManager, contextmanager
from contextvars import ContextVar, Token
from typing import Any, Generic, Iterator, TypeVar

T = TypeVar("T")

NOTSET = object()


class TypedContextVar(Generic[T]):
    def __init__(self, name: str, default: Any = NOTSET):
        kw = {}
        if default is not NOTSET:
            kw["default"] = default
        self._var = ContextVar(name, **kw)
        self._default = default

    def get(self) -> T:
        return self._var.get()

    def set(self, value: T) -> Token:
        return self._var.set(value)

    def reset(self, token: Token):
        return self._var.reset(token)

    @contextmanager
    def context(self, value: T) -> Iterator[None]:
        token = self.set(value)
        try:
            yield
        finally:
            self.reset(token)

    def __call__(self, value: T) -> AbstractContextManager[None]:
        return self.context(value)
