from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

from app.exceptions import UninitializedResourceError
from app.lib.context import scoped_context
from app.lib.mailer import get_mailer_from_url
from app.lib.resources import ResourceID, ResourcesRegistry
from app.lib.sql.utils import create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

    from app.config import Config
    from app.lib.mailer import BaseMailer


class DatabaseID(ResourceID):
    pass


class MailerID(ResourceID):
    pass


DEFAULT_DB = DatabaseID()
DEFAULT_MAILER = MailerID()


resources_context = ContextVar[ResourcesRegistry]("resources_context")


def initialize_resources(config: Config, set_context=False) -> ResourcesRegistry:
    """
    Initialize resources from configuration.

    Args:

        config:
            Config object

        set_context:
            If set to True, expose resources in the global
            context as well.
    """

    resources = ResourcesRegistry()

    if config.database_url is not None:
        db = create_async_engine(str(config.database_url))
        resources.add(DEFAULT_DB, db)

    if config.smtp_url is not None:
        mailer = get_mailer_from_url(str(config.smtp_url))
        resources.add(DEFAULT_MAILER, mailer)

    if set_context:
        resources_context.set(resources)

    return resources


def get_resources() -> ResourcesRegistry:
    try:
        return resources_context.get()
    except LookupError:
        return ResourcesRegistry()


def get_database() -> AsyncEngine:
    try:
        return get_resources().require(DEFAULT_DB)
    except KeyError as exc:
        raise UninitializedResourceError("database is not initialized") from exc


def get_mailer() -> BaseMailer:
    try:
        return get_resources().require(DEFAULT_MAILER)
    except KeyError as exc:
        raise UninitializedResourceError("mailer is not initialized") from exc


@contextmanager
def override_resources(new: dict[ResourceID, Any]) -> Generator[None]:
    """Temporarily override some resources.

    Mainly useful for testing.
    """

    resources = get_resources().clone()
    for key, val in new.items():
        resources.add(key, val)
    with scoped_context(resources_context, resources):
        yield
