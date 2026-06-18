from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Annotated

from publicsuffixlist import PublicSuffixList
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
PUBLIC_SUFFIX_LIST = PublicSuffixList()


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
        Field(default_factory=lambda data: [str(data["frontend_url"])]),
        NoDecode,
        BeforeValidator(lambda x: (x.split() if isinstance(x, str) else x)),
        PlainSerializer(lambda x: " ".join(x), return_type=str),
    ]

    # Authentication options
    auth_relying_party_id: Annotated[
        str,
        Field(
            default_factory=lambda data: get_url_private_suffix(data["frontend_url"])
        ),
    ]
    auth_relying_party_name: Annotated[
        str, Field(default_factory=lambda data: data["auth_relying_party_id"])
    ]

    # Enable development features
    development_mode: bool = False


def get_url_private_suffix(url: HttpUrl) -> str:
    domain = url.host
    assert domain is not None, "FRONTEND_URL must include a domain name"

    result = PUBLIC_SUFFIX_LIST.privatesuffix(domain)
    if result is not None:
        return result

    # Default to the full domain
    return domain


def get_config_from_env() -> Config:
    # Workaround to make linters happy.
    #
    # Using Config() will complain that required constructor arguments
    # are not passed, but BaseSettings will actually load omitted
    # arguments from the environment.

    return Config.model_validate({})


config_context = ContextVar[Config]("config_context")


def load_config() -> Config:
    config = get_config_from_env()
    config_context.set(config)
    return config


def get_config() -> Config:
    """Get current application configuration"""
    return config_context.get()


def update_config(**updates) -> Token:
    config = get_config()
    new_config = config.model_copy()
    for key, value in updates.items():
        setattr(new_config, key, value)
    return config_context.set(new_config)
