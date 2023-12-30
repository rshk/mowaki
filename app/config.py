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
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from app.lib.config import create_config_from_env as _create_config_from_env


@dataclass
class AppConfig:
    secret_key: str
    database_url: str
    redis_url: str
    frontend_url: str
    port: int = 8080
    bind_host: str = "0.0.0.0"


_config_context_var = ContextVar("config_context")


@contextmanager
def config_context(cfg: AppConfig):
    """
    Context manager to push a configuration object onto the stack.
    """

    token = _config_context_var.set(cfg)
    try:
        yield cfg
    finally:
        _config_context_var.reset(token)


def override_config(**kwargs):
    """
    Context manager to override some configuration settings.

    Mostly useful for testing.
    """

    cfg = get_config()
    new_cfg = dataclasses.replace(cfg, **kwargs)
    return config_context(new_cfg)


def get_config() -> AppConfig:
    """Get the current configuration"""
    return _config_context_var.get()


def create_config_from_env() -> AppConfig:
    """Create configuration object from os.environ"""
    return _create_config_from_env(AppConfig, os.environ)
