from typing import Annotated

from fastapi import Depends, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth.session import create_session, get_session, invalidate_session
from app.exceptions import ObjectNotFound
from app.types.session import AuthSession, SessionID

BearerToken = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(HTTPBearer(auto_error=False)),
]


def get_current_session_id(token: BearerToken) -> SessionID | None:
    if token is None:
        return None
    return SessionID(token.credentials)


CurrentSessionID = Annotated[SessionID | None, Depends(get_current_session_id)]


class SessionManager:
    # SessionID that was passed with the request
    request_session_id: SessionID | None

    # SessionID passed with the request, or ID of a new session that was created
    current_session_id: SessionID | None

    # Response object, used to set headers when a new session is created
    _response: Response

    def __init__(self, session_id: SessionID | None, response: Response):
        self.request_session_id = session_id
        self.current_session_id = session_id
        self._response = response

    async def get(self) -> AuthSession:
        """Get the current session or create a new one"""

        if self.current_session_id is not None:
            try:
                return await get_session(self.current_session_id)
            except ObjectNotFound:
                # No valid session found; fall back to create a new one
                pass

        return await self._create()

    async def invalidate(self) -> AuthSession:
        """Delete the current session and create a new one"""

        if self.current_session_id is not None:
            await invalidate_session(self.current_session_id)

        return await self._create()

    async def _create(self) -> AuthSession:
        new_session = await create_session()
        session_id = new_session.session_id
        self.current_session_id = session_id
        self._response.headers["X-Set-Session-Id"] = session_id
        return new_session

    async def ensure(self) -> None:
        """Ensure that a session is active"""
        await self.get()


async def get_current_session_manager(
    session_id: CurrentSessionID, response: Response
) -> SessionManager:
    mgr = SessionManager(session_id=session_id, response=response)
    await mgr.ensure()
    return mgr


CurrentSessionManager = Annotated[SessionManager, Depends(get_current_session_manager)]
