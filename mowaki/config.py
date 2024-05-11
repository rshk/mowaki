"""
Configuration management utilities
"""

import dataclasses
from typing import Type, TypeVar

AppConfigType = TypeVar("AppConfigType")
T = TypeVar("T")


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

        kwargs[field.name] = _parse_value(value, field.type)

    return config_type(**kwargs)


def _is_required_field(field):
    """
    If the field doesn't have either a default value or default
    factory, then it must be supplied.
    """
    return (field.default is dataclasses.MISSING) and (
        field.default_factory is dataclasses.MISSING
    )


def _get_field_default(field):
    """Get the default value for a dataclass field"""

    if field.default is not dataclasses.MISSING:
        return field.default

    if field.default_factory is not dataclasses.MISSING:
        return field.default_factory()

    return None


def _parse_value(value: str, type_: Type[T]) -> T:
    if type_ is str:
        return value

    if type_ is int:
        return int(value)

    if type_ is float:
        return float(value)

    if type_ is bool:
        return _parse_bool(value)

    raise ValueError(f"Unsupported configuration variable type: {type_}")


def _parse_bool(value: str) -> bool:
    TRUTHY = {"true", "yes", "on", "1"}
    FALSEY = {"false", "no", "off", "0", ""}

    _value = value.lower()

    if _value in TRUTHY:
        return True

    if _value in FALSEY:
        return False

    raise ValueError(f"Unable to parse boolean value: {value}")
