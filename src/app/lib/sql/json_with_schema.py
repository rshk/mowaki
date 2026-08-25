"""
SQLAlchemy column type to store a Pydantic model as JSON
"""

from __future__ import annotations

import json
from abc import ABCMeta, abstractmethod
from typing import Any

from pydantic import BaseModel, TypeAdapter
from sqlalchemy import JSON, Dialect, types
from sqlalchemy.dialects.postgresql import JSONB


class JsonWithSchema(types.TypeDecorator):
    impl = JSON
    cache_ok = False  # TODO: verify if we can / should cache
    _serializer: ModelSerializer

    def __init__(self, model_class: type[BaseModel] | TypeAdapter):
        super().__init__()
        self._model_class = model_class
        self._serializer = get_model_serializer(model_class)

    def load_dialect_impl(self, dialect: Dialect) -> types.TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return super().load_dialect_impl(dialect)

    def process_bind_param(self, value, dialect: Dialect):
        if value is None:
            return None
        return self._serializer.dump(value)

    def process_result_value(self, value: Any, dialect: Dialect):
        if value is None:
            return None
        if isinstance(value, str):
            # TODO: investigate why "value" is not a dict, as returned
            # by the JSONB type.
            value = json.loads(value)
        return self._serializer.load(value)

    def copy(self, **kw):
        return self.__class__(self._model_class)

    # def coerce_compared_value(self, op, value):
    #     return self.impl.coerce_compared_value(op, value)


class ModelSerializer(metaclass=ABCMeta):
    @abstractmethod
    def load(self, value) -> Any:
        pass  # pragma: nocover

    @abstractmethod
    def dump(self, value) -> Any:
        pass  # pragma: nocover


class PydanticModelSerializer(ModelSerializer):
    def __init__(self, model: type[BaseModel]):
        self._model = model

    def load(self, value: Any) -> Any:
        return self._model.model_validate(value)

    def dump(self, value: BaseModel | Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump_json()
        return value


class PydanticTypeAdapterSerializer(ModelSerializer):
    def __init__(self, model: TypeAdapter):
        self._model = model

    def load(self, value) -> Any:
        return self._model.validate_python(value)

    def dump(self, value) -> Any:
        return self._model.dump_python(value, mode="json")


def get_model_serializer(model: Any) -> ModelSerializer:
    if isinstance(model, type) and issubclass(model, BaseModel):
        return PydanticModelSerializer(model)

    if isinstance(model, TypeAdapter):
        return PydanticTypeAdapterSerializer(model)

    raise TypeError(f"Unsupported type for model_class: {model}")
