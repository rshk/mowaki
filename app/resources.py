from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine

from mowaki.lib.emailer import get_mailer_from_url

from .config import AppConfig

if TYPE_CHECKING:
    from sqlalchemy.exc.asyncio import AsyncEngine

    from mowaki.lib.emailer.base import BaseMailer


@dataclass
class AppResources:
    database: AsyncEngine
    redis: redis.Redis
    mailer: BaseMailer


resources_context = ContextVar[AppResources]("resources_context")


def initialize_resources(config: AppConfig) -> AppResources:
    """
    Initialize resources from configuration.
    """

    return AppResources(
        database=create_async_engine(config.database_url),
        redis=redis.from_url(config.redis_url),
        mailer=get_mailer_from_url(config.email_server_url),
    )
