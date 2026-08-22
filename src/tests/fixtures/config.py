import secrets

import pytest
import sqlalchemy
from pydantic import AnyUrl, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config import Config, config_context
from app.lib.context import scoped_context


class TestingConfig(BaseSettings):
    """
    Configuration for the testing machinery.
    """

    model_config = SettingsConfigDict(env_prefix="TESTING_")

    # ----------------------------------------------------------------

    # Database to use for setting up test databases.
    # New users and databases will be set up and cleared on demand.
    admin_database_url: PostgresDsn


@pytest.fixture(scope="session")
def config(testing_config: TestingConfig):
    database_url = get_database_url(testing_config)
    return Config(
        database_url=PostgresDsn(str(database_url)),
        frontend_url=HttpUrl("https://www.example.com"),
        email_sender="Test Sender <no-reply@example.com>",
        smtp_url=AnyUrl("dummy://"),
        cors_origins=["https://www.example.com"],
    )


@pytest.fixture(scope="session")
def testing_config():
    """Used by testing machinery to set things up"""
    return TestingConfig.model_validate({})


@pytest.fixture(scope="session", autouse=True)
def setup_config_context(config):
    with scoped_context(config_context, config):
        yield


def get_database_url(testing_config: TestingConfig) -> sqlalchemy.URL:
    role_name = f"test_user_{secrets.token_urlsafe(8)}"
    password = secrets.token_urlsafe(32)
    db_name = f"test_database_{secrets.token_urlsafe(8)}"

    # pydantic.PostgresDsn is wonky, use more reliable parsing
    admin_url = sqlalchemy.make_url(str(testing_config.admin_database_url))

    return sqlalchemy.URL.create(
        drivername="postgresql+asyncpg",
        username=role_name,
        password=password,
        host=admin_url.host,
        port=admin_url.port,
        database=db_name,
    )
