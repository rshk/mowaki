from __future__ import annotations

from contextvars import ContextVar
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


class Config(BaseSettings):
    # Used to generate direct links to the application.
    frontend_url: HttpUrl
    database_url: PostgresDsn
    # redis_url: RedisDsn
    smtp_url: Annotated[AnyUrl, Field(default="dummy://")]
    cors_origins: Annotated[
        list[str],
        Field(default_factory=list),
        NoDecode,
        BeforeValidator(lambda x: (x.split() if isinstance(x, str) else x)),
        PlainSerializer(lambda x: " ".join(x), return_type=str),
    ]
    email_sender: Annotated[str, Field(default="Default Sender <no-reply@example.com>")]


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
