from __future__ import annotations

from typing import Any, Callable, Type, TypeVar

import sqlalchemy
from pydantic import BaseModel

from app.types.session import AuthSession

type LoaderFn = Callable[[Type, sqlalchemy.Row], Any]
type DumperFn = Callable[[Type, Any], dict[str, Any]]


class ModelSerializationRegistry:
    """
    Conversion of models from/to database rows.

    - Loader functions take a sqlalchemy Row and convert it into a
      model instance.
    - Dumper functions take a model instance and convert it into a
      dictionary.
    """

    _loaders: dict[Type, LoaderFn]
    _dumpers: dict[Type, DumperFn]

    def __init__(self):
        self._loaders = {}
        self._dumpers = {}

    def set_loader(self, type_: Type, fn: LoaderFn):
        self._loaders[type_] = fn

    def set_dumper(self, type_: Type, fn: DumperFn):
        self._dumpers[type_] = fn

    def loader(self, type_: Type) -> Callable[[LoaderFn], None]:
        def decorator(fn: LoaderFn):
            self.set_loader(type_, fn)

        return decorator

    def dumper(self, type_: Type) -> Callable[[DumperFn], None]:
        def decorator(fn: DumperFn):
            self.set_dumper(type_, fn)

        return decorator

    def _find_loader(self, type_: Type) -> LoaderFn:
        for subtype in type_.mro():
            try:
                return self._loaders[subtype]
            except KeyError:
                pass
        raise KeyError(f"No loader found for {type_}")

    def _find_dumper(self, type_: Type) -> DumperFn:
        for subtype in type_.mro():
            try:
                return self._dumpers[subtype]
            except KeyError:
                pass
        raise KeyError(f"No dumper found for {type_}")

    def load(self, model: Type, obj: sqlalchemy.Row) -> Any:
        loader = self._find_loader(model)
        return loader(model, obj)

    def dump(self, obj: Any) -> dict[str, Any]:
        dumper = self._find_dumper(type(obj))
        return dumper(type(obj), obj)


registry = ModelSerializationRegistry()


type ToDictFn = Callable[[Any], dict[str, Any]]

# class DictSerializerRegistry:
#     _registry: dict[Type, ToDictFn]

#     def __init__(self):
#         self._registry = {}

#     def set_serializer(self, type_: Type, fn: ToDictFn):
#         self._registry[type_] = fn

#     def get_serializer(self, type_: Type) -> ToDictFn:
#         for subtype in type_.mro():
#             try:
#                 return self._registry()


# Public interface ---------------------------------------------------


def load_model(model: type, obj: sqlalchemy.Row) -> Any:
    return registry.load(model, obj)


def dump_model(obj: Any) -> dict[str, Any]:
    return registry.dump(obj)


# Model serializers --------------------------------------------------


@registry.loader(BaseModel)
def load_pydantic_model(model, row):
    return model.model_validate(row._asdict())


@registry.dumper(BaseModel)
def dump_pydantic_model(_, obj: BaseModel):
    return obj.model_dump(mode="python")
