import base64
import hashlib
import secrets
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from app.lib.sql.table_helper import TableHelper, UpdateHelper
from app.repo._schema.auth_session import SessionTable
from app.resources import get_database
from app.types.auth.assertions import Assertion, AssertionID
from app.types.auth.session import (
    AuthSession,
    AuthSessionMetadata,
    HashedSessionSecret,
    SessionID,
    SessionSecret,
    SessionTokenData,
)
from app.types.user import UserID

_crud = TableHelper[AuthSession](
    SessionTable,
    model=AuthSession,
    get_engine=get_database,
)


def generate_session_id() -> SessionID:
    return SessionID(secrets.token_urlsafe(16))


def generate_session_secret() -> SessionSecret:
    return SessionSecret(secrets.token_urlsafe(16))


def hash_session_secret(secret: SessionSecret) -> HashedSessionSecret:
    """Hash the session secret for storing in the database"""

    digest = hashlib.sha256(str(secret).encode()).digest()
    result = base64.urlsafe_b64encode(digest).decode("ascii")
    return HashedSessionSecret(result)


async def get(session_id: SessionID) -> AuthSession:
    return await _crud.get_by_pk(session_id)


async def get_for_token(token: SessionTokenData) -> AuthSession:
    """
    Get a session matching a user-provided token.

    Also automatically updates the "last_used_at", as we assume the
    user is using the session for this request.
    """
    hashed_secret = hash_session_secret(token.session_secret)
    session = await _crud.get_by(
        session_id=token.session_id, session_secret=hashed_secret
    )
    await set_last_used_at(session.session_id)
    return session


async def create(
    metadata: AuthSessionMetadata | None = None,
    assertions: list[Assertion] | None = None,
    current_user_id: UserID | None = None,
) -> tuple[SessionID, SessionSecret]:
    session_id = generate_session_id()
    session_secret = generate_session_secret()
    secret_hash = hash_session_secret(session_secret)

    if metadata is None:
        metadata = AuthSessionMetadata.empty()

    await _crud.insert(
        session_id=session_id,
        session_secret=secret_hash,
        created_at=datetime.now(UTC),
        last_used_at=None,
        metadata=metadata,
        assertions=assertions or [],
        current_user_id=current_user_id,
    )

    return session_id, session_secret


class SessionUpdater:
    """
    High-level methods for updating a session.

    Ensures that secrets are rotated as required.
    If the secret was rotated, the new plain-text value will be stored
    in the ``new_secret`` attribute.
    """

    __slots__ = ["_update_helper", "new_secret"]

    _update_helper: UpdateHelper[AuthSession]

    # If a new secret was set for the session, this will be populated
    new_secret: SessionSecret | None

    def __init__(self, update_helper: UpdateHelper[AuthSession]):
        self._update_helper = update_helper
        self.new_secret = None

    async def get(self):
        return await self._update_helper.get()

    async def _refresh(self):
        await self._update_helper.get()

    async def _update(self, **kw):
        await self._update_helper.update(**kw)
        await self._refresh()

    async def set_last_used_at(self, new_date: datetime | None = None):
        if new_date is None:
            new_date = datetime.now(UTC)
        await self._update(last_used_at=new_date)

    async def rotate_secret(self) -> SessionSecret:
        new_secret = generate_session_secret()
        self.new_secret = new_secret
        hashed_secret = hash_session_secret(new_secret)
        await self._update(session_secret=hashed_secret)
        return new_secret

    @asynccontextmanager
    async def edit_metadata(self) -> AsyncGenerator[AuthSessionMetadata]:
        session = await self.get()
        new_metadata = session.metadata.model_copy()
        yield new_metadata
        await self._update(metadata=new_metadata)

    # Assertions -----------------------------------------------------

    async def add_assertion(self, assertion: Assertion):
        session = await self.get()
        await self._update(assertions=[*session.assertions, assertion])

    async def set_assertions(self, assertions: list[Assertion]):
        await self._update(assertions=assertions)

    async def remove_assertion(self, assertion_id: AssertionID):
        session = await self.get()
        assertions = [x for x in session.assertions if x.id != assertion_id]
        await self._update(assertions=assertions)

    # Current user ID ------------------------------------------------

    async def set_current_user_id(self, user_id: UserID):
        await self._update(current_user_ud=user_id)

    async def unset_current_user_id(self, user_id: UserID):
        await self._update(current_user_ud=None)


@asynccontextmanager
async def for_update(session_id: SessionID) -> AsyncGenerator[SessionUpdater]:
    """Lock a session for atomic update"""
    async with _crud.for_update(session_id) as update_helper:
        updater = SessionUpdater(update_helper)
        yield updater


async def set_last_used_at(session_id: SessionID, new_date: datetime | None = None):
    if new_date is None:
        new_date = datetime.now(UTC)
    await _crud.update(session_id, last_used_at=new_date)


async def set_current_user_id(session_id: SessionID, user_id: UserID | None):
    await _crud.update(session_id, user_id=user_id)


async def delete(session_id: SessionID):
    await _crud.delete(session_id)
