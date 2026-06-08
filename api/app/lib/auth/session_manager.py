from contextlib import asynccontextmanager
import secrets
from typing import AsyncIterator

from api.app.lib.auth.storage.base import SessionStorage
from api.app.lib.auth.types.session import AuthSession, SessionID


class SessionManager:
    def __init__(self, storage: SessionStorage):
        self._storage = storage

    async def create(self) -> AuthSession:
        """Create a new session"""
        session_id = generate_session_id()
        await self._storage.create(session_id)
        return await self._storage.get(session_id)

    async def get(self, session_id: SessionID) -> AuthSession:
        return await self._storage.get(session_id)

    @asynccontextmanager
    async def update(self, session_id: str) -> AsyncIterator[AuthSession]:
        async with self._storage.update(session_id) as session:
            yield session

    async def invalidate(self, session_id: SessionID):
        await self._storage.invalidate(session_id)

    async def cleanup(self):
        """Cleanup expired sessions"""
        await self._storage.cleanup()


def generate_session_id() -> SessionID:
    token = secrets.token_urlsafe(32)
    return SessionID(f"SESS-{token}")
