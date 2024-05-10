"""
Configuration management.

Example usage::

    config = create_config_from_env()
    with config_context(config):

        # Code can now access the configuration using:
        config = get_config()

If you need to override some configuration during testing::

    with override_config(some_setting="new value"):
        # testing code here
"""

import dataclasses
import os
from dataclasses import dataclass

from mowaki.lib.config import create_config_from_env as _create_config_from_env
from mowaki.lib.context import TypedContextVar


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


config_context = TypedContextVar[AppConfig]("config_context")


def create_config_from_env() -> AppConfig:
    """Create configuration object from os.environ"""
    return _create_config_from_env(AppConfig, os.environ)


# Testing utilities --------------------------------------------------


def override_config(**kwargs):
    """
    Context manager to override some configuration settings.

    Mostly useful for testing.
    """

    cfg = config_context.get()
    new_cfg = dataclasses.replace(cfg, **kwargs)
    return config_context(new_cfg)
