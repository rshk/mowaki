"""
Context to hold clients to various I/O resources.

Initialized from configuration at setup time.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING

# import redis.asyncio as redis
# from mowaki.emailer import get_mailer_from_url
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import Config

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


@dataclass
class Resources:
    database: AsyncEngine
    # redis: redis.Redis
    # mailer: BaseMailer


resources_context = ContextVar[Resources]("resources_context")


def initialize_resources(config: Config) -> Resources:
    """
    Initialize resources from configuration.
    """

    return Resources(
        database=create_async_engine(str(config.database_url)),
        # redis=redis.from_url(config.redis_url),
        # mailer=get_mailer_from_url(config.email_server_url),
    )


def get_resources():
    return resources_context.get()
