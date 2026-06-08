from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Annotated

from pydantic import (
    AnyUrl,
    BeforeValidator,
    Field,
    HttpUrl,
    PlainSerializer,
    PostgresDsn,
    # RedisDsn,
)
from pydantic_settings import BaseSettings, NoDecode

DEFAULT_MAILER = "dummy://"
DEFAULT_EMAIL_SENDER = "Default Sender <no-reply@example.com>"


class Config(BaseSettings):
    # Used to generate direct links to the application.
    frontend_url: Annotated[HttpUrl, Field(default=None)]
    database_url: Annotated[PostgresDsn, Field(default=None)]
    # redis_url: RedisDsn
    smtp_url: Annotated[AnyUrl, Field(default=DEFAULT_MAILER)]
    email_sender: Annotated[str, Field(default=DEFAULT_EMAIL_SENDER)]

    # Allowed origins for CORS
    cors_origins: Annotated[
        list[str],
        Field(default_factory=list),
        NoDecode,
        BeforeValidator(lambda x: (x.split() if isinstance(x, str) else x)),
        PlainSerializer(lambda x: " ".join(x), return_type=str),
    ]

    # Enable development features
    development_mode: bool = False


def get_config_from_env() -> Config:
    # Workaround to make linters happy.
    #
    # Using Config() will complain that required constructor arguments
    # are not passed, but BaseSettings will actually load omitted
    # arguments from the environment.

    return Config.model_validate({})


config_context = ContextVar[Config]("config_context")


def get_config() -> Config:
    """Get current application configuration"""
    return config_context.get()


def update_config(**updates) -> Token:
    config = get_config()
    new_config = config.model_copy()
    for key, value in updates.items():
        setattr(new_config, key, value)
    return config_context.set(new_config)
