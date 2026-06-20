import base64
from contextlib import asynccontextmanager
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from app.exceptions import ObjectNotFound
from app.types.challenges import AuthChallengeState, ChallengeID
from app.types.session import (
    AuthGrant,
    AuthGrantId,
    AuthSession,
    AuthSessionData,
    AuthSessionMetadata,
    HashedSessionSecret,
    SessionID,
    SessionSecret,
    SessionTokenData,
)
from app.types.user import UserID

from ._helpers.common import TableCrud, UpdaterFn
from ._schema.session import SessionTable

_crud = TableCrud[AuthSession](SessionTable, model=AuthSession)


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

    Also automatically updates the "last_used_date", as we assume the
    user is using the session for this request.
    """
    hashed_secret = hash_session_secret(token.session_secret)
    session = await _crud.get_by(session_id=token.session_id, session_secret=hashed_secret)
    await update_last_used_date(session.session_id)
    return session


async def create(
    metadata: AuthSessionMetadata | None = None,
    data: AuthSessionData | None = None,
) -> tuple[SessionID, SessionSecret]:
    session_id = generate_session_id()
    session_secret = generate_session_secret()
    secret_hash = hash_session_secret(session_secret)

    if metadata is None:
        metadata = AuthSessionMetadata.empty()

    if data is None:
        data = AuthSessionData.empty()

    await _crud.insert(
        session_id=session_id,
        session_secret=secret_hash,
        creation_date=datetime.now(timezone.utc),
        last_used_date=None,
        authenticated_user_id=data.authenticated_user_id,
        current_user_id=data.current_user_id,
        metadata=metadata,
        data=data,
    )

    return session_id, session_secret


async def update_last_used_date(
    session_id: SessionID, new_date: datetime | None = None
):
    if new_date is None:
        new_date = datetime.now(timezone.utc)
    await _crud.update(session_id, last_used_date=new_date)


class SessionUpdater:
    """
    High-level methods for updating a session.

    Typically not instantiated directly, but obtained through::

        async with repo.session.for_update(session_id) as updater:

            # Call various updater methods here...

            # Run the update query. The session stored in
            # updater.session is updated automatically.
            updater.run()

            if updater.new_secret is not None:
                # We need to provide a new token to the user
                pass
    """

    __slots__ = ["_session", "_updater", "_updates", "new_secret"]

    _session: AuthSession
    _updater: UpdaterFn
    _updates: dict[str, Any]
    new_secret: SessionSecret | None

    def __init__(self, session: AuthSession, updater: UpdaterFn):
        self._session = session
        self._updater = updater
        self._updates = {}
        self.new_secret = None

    @property  # read-only
    def session(self):
        return self._session

    # Methods that run queries ---------------------------------------

    async def run(self):
        """Execute the scheduled updates"""
        if len(self._updates) == 0:
            return  # Nothing to update
        await self._updater(**self._updates)
        self._updates = {}
        await self.refresh()

    async def refresh(self):
        """Update the stored session"""
        self._session = await get(self._session.session_id)

    # Updater methods ------------------------------------------------

    def rotate_secret(self):
        if self.new_secret is not None:
            # Only need to rotate once!
            return
        new_secret = generate_session_secret()
        hashed_secret = hash_session_secret(new_secret)
        self._updates["session_secret"] = hashed_secret
        self.new_secret = new_secret

    @property
    def _new_metadata(self) -> AuthSessionMetadata:
        if "metadata" not in self._updates:
            self._updates["metadata"] = AuthSessionMetadata.empty()
        return self._updates["metadata"]

    @property
    def _new_data(self) -> AuthSessionData:
        if "data" not in self._updates:
            self._updates["data"] = AuthSessionData.empty()
        return self._updates["data"]

    def cleanup(self):
        """Remove expired grants and challenges from the session data"""
        data = self._new_data
        now = datetime.now(timezone.utc)
        data.grants = [
            x for x in data.grants if x.expires_at is None or x.expires_at > now
        ]
        data.challenges = [
            x for x in data.challenges if x.expires_at is None or x.expires_at > now
        ]

    def set_authenticated_user_id(self, user_id: UserID | None = None):
        self.rotate_secret()

        self._new_data.authenticated_user_id = user_id
        self._updates["authenticated_user_id"] = user_id
        self._new_data.current_user_id = user_id
        self._updates["current_user_id"] = user_id

    def set_current_user_id(self, user_id: UserID | None = None):
        self._new_data.current_user_id = user_id
        self._updates["current_user_id"] = user_id

    def add_grant(self, grant: AuthGrant):
        self.rotate_secret()
        self._new_data.grants.append(grant)

    def remove_grant(self, grant_id: AuthGrantId):
        self.rotate_secret()
        self._new_data.grants = [
            x for x in self._new_data.grants if x.id != grant_id
        ]

    def get_editable_challange(self, challenge_id: ChallengeID) -> AuthChallengeState:
        """Get an authentication challenge so it can be updated"""
        for challenge in self._new_data.challenges:
            if challenge.challenge_id == challenge_id:
                return challenge
        raise ObjectNotFound(f"Challenge {challenge_id} on session {self.session.session_id}")

    def add_challenge(self, challenge: AuthChallengeState):
        self._new_data.challenges.append(challenge)

    def remove_challenge(self, challenge_id: ChallengeID):
        self._new_data.challenges = [
            x for x in self._new_data.challenges if x.challenge_id != challenge_id
        ]


@asynccontextmanager
async def for_update(session_id: SessionID) -> AsyncIterator[SessionUpdater]:
    """
    Lock a session for atomically updating.
    """
    async with _crud.for_update(session_id) as (session, updater):
        yield SessionUpdater(session, updater)


# async def update_secret(session_id: SessionID, new_secret_hash: HashedSessionSecret):
#     """Update the session secret wiht a new one"""
#     await _crud.update(session_id, session_secret=new_secret_hash)


# @asynccontextmanager
# async def update_metadata(session_id: SessionID) -> AsyncIterator[AuthSessionMetadata]:
#     async with _crud.for_update(session_id) as (session, update):
#         metadata = session.metadata.model_copy()
#         yield metadata
#         await update(metadata=metadata)


# @asynccontextmanager
# async def update_data(session_id: SessionID) -> AsyncIterator[AuthSessionData]:
#     async with _crud.for_update(session_id) as (session, update):
#         data = session.data.model_copy()
#         yield data
#         await update(
#             authenticated_user_id=data.authenticated_user_id,
#             current_user_id=data.current_user_id,
#             data=data,
#         )


async def invalidate(session_id: SessionID):
    await _crud.delete(session_id)
