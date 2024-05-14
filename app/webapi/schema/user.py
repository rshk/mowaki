from __future__ import annotations

import strawberry
from strawberry.types import Info


@strawberry.type
class User:
    id: int
    email: str

    @strawberry.field
    async def is_self(self, info: Info) -> bool:
        auth_info = info.context.auth_info

        if not auth_info.is_authenticated():
            return False

        return self.id == auth_info.user.id
