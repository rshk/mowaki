from __future__ import annotations

from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PostgresDsn,
    # RedisDsn,
)
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    database_url: PostgresDsn
    # redis_url: RedisDsn
    frontend_url: HttpUrl
    development_mode: bool = False
    dev: Annotated[DevConfig, Field(default_factory=lambda: DevConfig())]


class DevConfig(BaseModel):
    enable_unauthenticated_login: bool = False
    enable_custom_login_url: bool = False


def get_config_from_env() -> Config:
    # Workaround to make linters happy.
    #
    # Using Config() will complain that required constructor arguments
    # are not passed, but BaseSettings will actually load omitted
    # arguments from the environment.

    return Config.model_validate({})
