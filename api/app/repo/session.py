from datetime import datetime, timezone
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from email_validator import validate_email

from app.types.session import (
    AuthSession,
    AuthSessionData,
    AuthSessionMetadata,
    HashedSessionSecret,
    SessionID,
)

from ._helpers.common import TableCrud, UpdaterFn
from ._schema.session import SessionTable

_crud = TableCrud[AuthSession](SessionTable, model=AuthSession)


async def get(session_id: SessionID) -> AuthSession:
    return await _crud.get_by_pk(session_id)


async def create(session_id: SessionID, secret_hash: HashedSessionSecret) -> None:
    await _crud.insert(session_id=session_id, session_secret=secret_hash)


# async def recreate(session: AuthSession, new_session_id: SessionID) -> AuthSession:
#     if session.session_id is not None:
#         await _crud.delete(session.session_id)

#     await _crud.insert(
#         session_id=new_session_id,
#         creation_date=session.creation_date,
#         soft_expiration_date=session.soft_expiration_date,
#         hard_expiration_date=session.hard_expiration_date,
#         authenticated_user_id=session.authenticated_user_id,
#         # metadata=session.metadata,
#         # data=session.data,
#     )
#     return await get(new_session_id)


async def update_soft_expiration_date(session_id: SessionID, new_date: datetime | None):
    await _crud.update(session_id, soft_expiration_date=new_date)


@asynccontextmanager
async def update_metadata(session_id: SessionID) -> AsyncIterator[AuthSessionMetadata]:
    async with _crud.for_update(session_id) as (session, update):
        metadata = session.metadata.model_copy()
        yield metadata
        await update(metadata=metadata)


@asynccontextmanager
async def update_data(session_id: SessionID) -> AsyncIterator[AuthSessionData]:
    async with _crud.for_update(session_id) as (session, update):
        data = session.data.model_copy()
        yield data
        await update(data=data)


async def invalidate(session_id: SessionID):
    await _crud.delete(session_id)
