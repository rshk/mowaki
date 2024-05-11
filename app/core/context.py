"""The "core" context is used to pass around context about things like
the currently authenticated user, locale settings, etc.

This stuff usually comes from a http request, but we want to avoid
coupling our business logic to details about http.
"""

from __future__ import annotations

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


core_context = ContextVar[CoreContext]("core_context")


def get_core_context() -> CoreContext:
    return core_context.get()


def get_auth_info() -> AuthInfo:
    return get_core_context().auth_info
