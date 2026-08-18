from __future__ import annotations

import dataclasses
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.exceptions import UninitializedResourceError
from app.lib.mailer import get_mailer_from_url
from app.lib.sql.utils import create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

    from app.config import Config
    from app.lib.mailer import BaseMailer


@dataclass
class Resources:
    database: AsyncEngine | None = None
    # redis: redis.Redis | None = None
    mailer: BaseMailer | None = None


resources_context = ContextVar[Resources]("resources_context")


def initialize_resources(config: Config, set_context=False) -> Resources:
    resources = Resources()

    if config.database_url is not None:
        resources.database = create_async_engine(str(config.database_url))

    if config.smtp_url is not None:
        resources.mailer = get_mailer_from_url(str(config.smtp_url))

    if set_context:
        resources_context.set(resources)

    return resources


def get_resources() -> Resources:
    try:
        return resources_context.get()
    except LookupError:
        return Resources()


def get_database() -> AsyncEngine:
    resources = get_resources()
    if (value := resources.database) is None:
        raise UninitializedResourceError("database is not initialized")
    return value


def get_mailer() -> BaseMailer:
    resources = get_resources()
    if (value := resources.mailer) is None:
        raise UninitializedResourceError("mailer is not initialized")
    return value


def update_resources(**updates) -> Token:
    resources = get_resources()
    new_resources = dataclasses.replace(resources, **updates)
    return resources_context.set(new_resources)
