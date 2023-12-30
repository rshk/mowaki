"""
Resources context
"""


import dataclasses
import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Callable, Type, TypeVar

_resources_context = ContextVar("resources_context")


@contextmanager
def push_resource_context(ctx):
    token = _resources_context.set(ctx)
    try:
        yield ctx
    finally:
        _resources_context.reset(token)


def create_resources_from_config(config):
    pass


# ConfigObject = TypeVar("ConfigObject")
# LoaderType = Callable[[Type[ConfigObject]], ConfigObject]


# class ResourcesContextManager:
#     def __init__(
#         self,
#         cfg_type: Type[ConfigObject],
#         loader: LoaderType = None,
#     ):
#         self._cfg_type = cfg_type
#         self._loader = loader or create_config_from_env
#         self._context = ContextVar("config_context")

#     @contextmanager
#     def load_from_env(self):
#         config = self._loader(self._cfg_type)
#         token = self._context.set(config)
#         yield config
#         self._context.reset(token)

#     def get_config(self) -> ConfigObject:
#         return self._context.get()


# def create_config_from_env(
#     cfg_type: Type[ConfigObject],
#     env: dict[str, str] = None,
# ) -> ConfigObject:

#     if env is None:
#         env = os.environ

#     fields = dataclasses.fields(cfg_type)
#     kwargs = {}

#     for field in fields:
#         env_key = field.name.upper()

#         try:
#             value = env[env_key]
#         except KeyError:
#             if _is_required_field(field):
#                 raise
#             value = _get_field_default(field)

#         kwargs[field.name] = value

#     return cfg_type(**kwargs)


# def _is_required_field(field):
#     return (field.default is dataclasses._MISSING_TYPE) and (
#         field.default_factory is dataclasses._MISSING_TYPE
#     )


# def _get_field_default(field):
#     if field.default is not dataclasses._MISSING_TYPE:
#         return field.default
#     if field.default_factory is not dataclasses._MISSING_TYPE:
#         return field.default_factory()
