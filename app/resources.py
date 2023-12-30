from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import create_async_engine

from .config import AppConfig


@dataclass
class AppResources:
    database: None
    redis: None


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
        # TODO: initialize Redis client for redis
        redis=None,
    )
