from __future__ import annotations

from typing import Annotated

from pydantic import (
    BeforeValidator,
    Field,
    HttpUrl,
    PlainSerializer,
    PlainValidator,
    PostgresDsn,
    # RedisDsn,
)
from pydantic_settings import BaseSettings, NoDecode


class Config(BaseSettings):
    # Used to generate direct links to the application.
    frontend_url: HttpUrl
    database_url: PostgresDsn
    # redis_url: RedisDsn
    smtp_url: Annotated[str, Field(default="dummy://")]
    cors_origins: Annotated[
        list[str],
        Field(default_factory=list),
        NoDecode,
        BeforeValidator(lambda x: x.split()),
        PlainSerializer(lambda x: " ".join(x), return_type=str),
    ]


def get_config_from_env() -> Config:
    # Workaround to make linters happy.
    #
    # Using Config() will complain that required constructor arguments
    # are not passed, but BaseSettings will actually load omitted
    # arguments from the environment.

    return Config.model_validate({})
