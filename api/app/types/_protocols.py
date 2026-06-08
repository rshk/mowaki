from abc import abstractmethod
from typing import Any, Protocol, Self

import sqlalchemy


class FromRow(Protocol):
    @classmethod
    @abstractmethod
    def from_row(cls, row: sqlalchemy.Row) -> Self:
        pass


class JsonSerializable(Protocol):
    @classmethod
    @abstractmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        pass

    @abstractmethod
    def to_json(self) -> dict[str, Any]:
        pass
