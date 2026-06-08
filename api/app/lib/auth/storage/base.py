from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncIterator

from api.app.lib.auth.types.session import AuthSession, SessionID


class SessionStorage(metaclass=ABCMeta):
    @abstractmethod
    async def get(self, session_id: SessionID) -> AuthSession:
        pass

    @abstractmethod
    async def create(self, session_id: SessionID) -> AuthSession:
        pass

    @asynccontextmanager
    @abstractmethod
    async def update(self, session_id: str) -> AsyncIterator[AuthSession]:
        yield AuthSession(session_id=SessionID(""))

    @abstractmethod
    async def invalidate(self, session_id: SessionID):
        pass

    @abstractmethod
    async def cleanup(self):
        pass
