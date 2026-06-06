import pytest
import sqlalchemy
from app.lib.context import scoped_context
from app.config import Config, config_context
from pydantic import AnyUrl, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TESTING_")

    # ----------------------------------------------------------------

    # Database to use for setting up test databases.
    # New users and databases will be set up and cleared on demand.
    admin_database_url: PostgresDsn


@pytest.fixture(scope="session")
def config(database_url: sqlalchemy.URL):
    return Config(
        # Database URL will be overwritten when a database is actually set up
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
