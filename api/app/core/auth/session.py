import secrets
from copy import deepcopy

from app.exceptions import ObjectNotFound
from app.types.session import AuthSession, SessionID

DUMMY_SESSION_DB: dict[SessionID, AuthSession] = {}


async def create_session() -> AuthSession:
    """Create a new session"""

    session_id = generate_session_id()
    session = AuthSession(session_id=session_id)
    DUMMY_SESSION_DB[session_id] = session
    return deepcopy(session)


async def duplicate_session(session: AuthSession) -> AuthSession:
    """Create a new copy of this session"""

    new_session_id = generate_session_id()
    new_session = deepcopy(session)
    new_session.session_id = new_session_id
    DUMMY_SESSION_DB[new_session_id] = new_session
    return new_session


async def get_session(session_id: SessionID) -> AuthSession:
    try:
        return DUMMY_SESSION_DB[session_id]
    except KeyError as exc:
        raise ObjectNotFound("Session not found") from exc


async def invalidate_session(session_id: SessionID):
    """Delete this session from database"""

    DUMMY_SESSION_DB.pop(session_id, None)


def generate_session_id() -> SessionID:
    return SessionID(secrets.token_urlsafe(32))
