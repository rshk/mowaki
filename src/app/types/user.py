from __future__ import annotations

from typing import NewType
from uuid import UUID

from app.lib.models import BaseModel

UserID = NewType("UserID", UUID)


class User(BaseModel):
    id: UserID
    email: str
    metadata: UserMetadata
    is_active: bool


class UserMetadata(BaseModel):
    display_name: str | None = None
    bio: str | None = None
