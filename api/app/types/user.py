from __future__ import annotations

from typing import Any, NewType, Self, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    import sqlalchemy

UserID = NewType("UserID", UUID)


class User(BaseModel):
    id: UserID
    email: str
    metadata: UserMetadata
    is_active: bool

    @classmethod
    def from_row(cls, row: sqlalchemy.Row) -> Self:
        return cls.model_validate(row._asdict())

    @classmethod
    def from_json(cls, data: dict[str, Any]):
        return cls.model_validate(data)

    def to_json(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class UserMetadata(BaseModel):
    display_name: str | None = None
    bio: str | None = None
