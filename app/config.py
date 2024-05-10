"""Configuration management.

Example usage::

    config = create_config_from_env()
    token = config_context.set(config)

    try:

        # Code inside this block can access the configuration using:
        config = get_config()

    finally:
        config_context.reset(token)
"""

import os
from dataclasses import dataclass

from mowaki.lib.config import create_config_from_env as _create_config_from_env
from contextvars import ContextVar


@dataclass
class AppConfig:
    secret_key: str
    database_url: str
    redis_url: str
    frontend_url: str
    email_server_url: str
    email_sender: str
    port: int = 8080
    bind_host: str = "0.0.0.0"


config_context = ContextVar[AppConfig]("config_context")


def create_config_from_env() -> AppConfig:
    """Create configuration object from os.environ"""
    return _create_config_from_env(AppConfig, os.environ)


# Testing utilities --------------------------------------------------

# TODO: move to test fixtures

# def override_config(**kwargs):
#     """
#     Context manager to override some configuration settings.

#     Mostly useful for testing.
#     """

#     cfg = config_context.get()
#     new_cfg = dataclasses.replace(cfg, **kwargs)
#     return config_context(new_cfg)
