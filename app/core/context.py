"""The "core" context is used to pass around context about things like
the currently authenticated user, locale settings, etc.

This stuff usually comes from a http request, but we want to avoid
coupling our business logic to details about http.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from app.models.auth_info import AuthInfo

DEFAULT_LOCALE = "en_US.UTF-8"


@dataclass
class CoreContext:  # TODO: can we find a better name for this class?
    # Authentication information for the current request
    auth_info: AuthInfo

    # Locale string for the user performing the request
    locale: str = DEFAULT_LOCALE

    # Other context info from the request can be added here, but don't
    # be tempted to start coupling things with the http / graphql
    # layer!


_core_context_var = ContextVar("core_context")


@contextmanager
def core_context(obj: CoreContext):
    """
    Context manager to push a "core context" object onto the stack.
    """

    token = _core_context_var.set(obj)
    try:
        yield obj
    finally:
        _core_context_var.reset(token)


def get_core_context() -> CoreContext:
    """Get the current core context instance"""
    return _core_context_var.get()
