from __future__ import annotations

from typing import Any, NewType, Self
from uuid import UUID

from pydantic import BaseModel

UserID = NewType("UserID", UUID)


class User(BaseModel):
    id: UserID
    email: str
    metadata: UserMetadata
    is_active: bool

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> Self:
        return cls.model_validate(row)

    @classmethod
    def from_json(cls, data: dict[str, Any]):
        return cls.model_validate(data)

    def to_json(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class UserMetadata(BaseModel):
    display_name: str | None = None
    bio: str | None = None
