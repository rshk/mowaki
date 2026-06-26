from __future__ import annotations

from typing import Any, Callable, Type, TypeVar

import sqlalchemy
from pydantic import BaseModel

from app.lib.type_registry import TypeCallbackRegistry
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

    _loaders: TypeCallbackRegistry[LoaderFn]
    _dumpers: TypeCallbackRegistry[DumperFn]

    def __init__(self):
        self._loaders = TypeCallbackRegistry()
        self._dumpers = TypeCallbackRegistry()

    def set_loader(self, type_: Type, fn: LoaderFn):
        self._loaders.set(type_, fn)

    def set_dumper(self, type_: Type, fn: DumperFn):
        self._dumpers.set(type_, fn)

    def loader(self, type_: Type) -> Callable[[LoaderFn], None]:
        return self._loaders.declare(type_)

    def dumper(self, type_: Type) -> Callable[[DumperFn], None]:
        return self._dumpers.declare(type_)

    def load(self, model: Type, obj: sqlalchemy.Row) -> Any:
        loader = self._loaders.get(model)
        return loader(model, obj)

    def dump(self, obj: Any) -> dict[str, Any]:
        dumper = self._dumpers.get(type(obj))
        return dumper(type(obj), obj)


registry = ModelSerializationRegistry()


type ToDictFn = Callable[[Any], dict[str, Any]]

to_dict_registry = TypeCallbackRegistry[ToDictFn]()


@to_dict_registry.declare(sqlalchemy.Row)
def sqlalchemy_row_to_dict(row: sqlalchemy.Row):
    return row._asdict()


# Public interface ---------------------------------------------------


def load_model(model: type, obj: Any) -> Any:
    data = to_dict_registry.get(type(obj))(obj)
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
