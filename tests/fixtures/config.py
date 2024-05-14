import os

import pytest

from app.config import AppConfig, config_context
from mowaki.context import contextvar_contextmanager


@pytest.fixture(scope="session")
def config():
    return AppConfig(
        secret_key="this-is-not-a-secret",
        database_url=os.environ["TEST_DATABASE_URL"],
        redis_url="redis://redis:6379",
        frontend_url="https://www.example.com",
        email_sender="Default Sender <no-reply@example.com>",
        email_server_url="dummy://",
    )


@pytest.fixture(scope="session", autouse=True)
def setup_config_context(config):
    with contextvar_contextmanager(config_context, config):
        yield
