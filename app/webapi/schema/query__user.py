from __future__ import annotations

from typing import Optional

from strawberry.types import Info

from .user import User


async def resolve_query_user(info: Info) -> Optional[User]:
    auth_info = info.context.auth_info

    if not auth_info.is_authenticated():
        return None

    return auth_info.user
