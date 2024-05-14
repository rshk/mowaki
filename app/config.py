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
from contextvars import ContextVar
from dataclasses import dataclass

from mowaki.config import create_config_from_env as _create_config_from_env


@dataclass
class AppConfig:
    secret_key: str
    database_url: str
    redis_url: str
    frontend_url: str
    email_server_url: str
    email_sender: str


config_context = ContextVar[AppConfig]("config_context")


def create_config_from_env() -> AppConfig:
    """Create configuration object from os.environ"""
    return _create_config_from_env(AppConfig, os.environ)


def get_config() -> AppConfig:
    return config_context.get()


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
