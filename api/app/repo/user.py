import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from email_validator import validate_email

from app.types.user import User, UserID, UserMetadata

from ._helpers.common import TableCrud, UpdaterFn
from ._schema.user import UserTable

_crud = TableCrud[User](UserTable, model=User)


async def get(user_id: UserID) -> User:
    return await get_by_id(user_id)


async def get_by_id(user_id: UserID) -> User:
    return await _crud.get_by_pk(user_id)


async def get_by_email(email: str) -> User:
    email = validate_email(email, check_deliverability=False).normalized
    return await _crud.get_by(email=email)


async def create(email: str) -> User:
    user_id = UserID(uuid.uuid4())
    email = validate_email(email).normalized

    tc = _crud.bind()  # Bind to current database
    await tc.insert(id=user_id, email=email)
    return await tc.get_by_pk(user_id)


@asynccontextmanager
async def update(user_id: UserID) -> AsyncIterator[tuple[User, UpdaterFn]]:
    # DANGER: this potentially allows updating *any* object
    # attributes, which might be undesirable. Use carefully.
    async with _crud.for_update(user_id) as res:
        yield res


@asynccontextmanager
async def update_metadata(user_id: UserID) -> AsyncIterator[UserMetadata]:
    """
    Context manager to allow updating a user's metadata.
    """
    async with _crud.for_update(user_id) as (user, update):
        metadata = user.metadata.model_copy()
        yield metadata
        await update(metadata=metadata)


async def deactivate(user_id: UserID):
    async with _crud.for_update(user_id) as (_, update):
        await update(is_active=False)


async def reactivate(user_id: UserID):
    async with _crud.for_update(user_id) as (_, update):
        await update(is_active=True)
