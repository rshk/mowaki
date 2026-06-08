from __future__ import annotations
from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from pydantic import BaseModel

UserID = NewType("UserID", UUID)


@dataclass(slots=True)
class User:
    id: UserID
    email: str
    metadata: UserMetadata


class UserMetadata(BaseModel):
    display_name: str | None = None
    bio: str | None = None
