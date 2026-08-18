from abc import abstractmethod
from typing import Any, Protocol, Self


class FromDict(Protocol):
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        pass


class ToDict(Protocol):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass
