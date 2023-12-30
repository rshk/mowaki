import os

import pytest

from app.config import AppConfig, config_context


@pytest.fixture(scope="session", autouse=True)
def setup_config_context():
    config = AppConfig(
        secret_key="this-is-not-a-secret",
        database_url=os.environ["TEST_DATABASE_URL"],
        redis_url=None,
        frontend_url="https://www.example.com",
    )
    with config_context(config):
        yield
