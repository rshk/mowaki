from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from app.lib.emailer import get_mailer_from_url

from sqlalchemy.ext.asyncio import create_async_engine
from typing import TYPE_CHECKING

from .config import AppConfig

if TYPE_CHECKING:
    from sqlalchemy.exc.asyncio import AsyncEngine
    from app.lib.emailer.base import BaseMailer


@dataclass
class AppResources:
    database: AsyncEngine
    # redis: ...
    mailer: BaseMailer


_resources_context_var = ContextVar("resources_context")


@contextmanager
def resources_context(obj: AppResources):
    """
    Context manager to push a "resources" object onto the stack.
    """

    token = _resources_context_var.set(obj)
    try:
        yield obj
    finally:
        _resources_context_var.reset(token)


def get_resources() -> AppResources:
    """Get the current resources"""
    return _resources_context_var.get()


def initialize_resources(config: AppConfig) -> AppResources:
    """
    Initialize resources from configuration.
    """

    return AppResources(
        database=create_async_engine(config.database_url),
        mailer=get_mailer_from_url(config.email_server_url),
    )
