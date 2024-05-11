import asyncio

import pytest

from .fixtures.config import config, setup_config_context
from .fixtures.database import database, database_schema
from .fixtures.resources import setup_resources_context

__all__ = [
    "config",
    "database",
    "database_schema",
    "setup_config_context",
    "setup_resources_context",
]


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
