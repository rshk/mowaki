import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.lib.sql.table_helper import TableHelper
from app.lib.validation import normalize_email
from app.resources import get_database
from app.types.user import User, UserID, UserMetadata

from ._schema.user import UserTable

_crud = TableHelper[User](UserTable, model=User, get_engine=get_database)


async def get(user_id: UserID) -> User:
    return await get_by_id(user_id)


async def get_by_id(user_id: UserID) -> User:
    return await _crud.get_by_pk(user_id)


async def get_by_email(email: str) -> User:
    email = normalize_email(email)
    return await _crud.get_by(email=email)


async def create(email: str) -> UserID:
    user_id = UserID(uuid.uuid4())
    email = normalize_email(email)

    await _crud.insert(id=user_id, email=email)
    return user_id


# @asynccontextmanager
# async def for_update(user_id: UserID) -> AsyncGenerator[UpdateHelper[User]]:
#     # DANGER: this potentially allows updating *any* object
#     # attributes, which might be undesirable. Use carefully.
#     async with _crud.for_update(user_id) as upd:
#         yield upd


@asynccontextmanager
async def edit_metadata(user_id: UserID) -> AsyncGenerator[UserMetadata]:
    """
    Context manager to allow updating a user's metadata.
    """
    async with _crud.for_update(user_id) as upd:
        user = await upd.get()
        new_metadata = user.metadata.model_copy()
        yield new_metadata
        await upd.update(metadata=new_metadata)


async def deactivate(user_id: UserID):
    await _crud.update(user_id, is_active=False)


async def reactivate(user_id: UserID):
    await _crud.update(user_id, is_active=True)
