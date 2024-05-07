"""
Configuration management utilities
"""

import dataclasses
from typing import Type, TypeVar

AppConfigType = TypeVar("AppConfigType")


def create_config_from_env(
    config_type: Type[AppConfigType],
    env: dict[str, str],
) -> AppConfigType:
    """
    Create an instance of AppConfig from environment variables.

    Args:

        config_type:
            Class to be instantiated with the configuration.
            Usually a dataclass (fields names are obtained by calling
            dataclasses.fields() on the type).

        env:
            Dict of environment variables to read. Keys and values are
            expected to be strings.

        alt_prefixes:
            List of alternate prefixes to search configuration
            variables.  Most useful during testing, to allow
            overriding configuration with TEST_* variables.

    Returns:

        A configured instance of ``config_type``
    """

    fields = dataclasses.fields(config_type)
    kwargs = {}

    for field in fields:
        env_key = field.name.upper()

        try:
            value = env[env_key]
        except KeyError:
            if _is_required_field(field):
                raise
            value = _get_field_default(field)

        kwargs[field.name] = value

    return config_type(**kwargs)


def _is_required_field(field):
    """
    If the field doesn't have either a default value or default
    factory, then it must be supplied.
    """
    return (field.default is dataclasses._MISSING_TYPE) and (
        field.default_factory is dataclasses._MISSING_TYPE
    )


def _get_field_default(field):
    """Get the default value for a dataclass field"""

    if field.default is not dataclasses._MISSING_TYPE:
        return field.default

    if field.default_factory is not dataclasses._MISSING_TYPE:
        return field.default_factory()

    return None
