import secrets
from app.types.session import AuthSession, SessionID


def create_session() -> AuthSession:
    """Create a new session"""
    session_id = generate_session_id()
    pass


def duplicate_session(session: AuthSession) -> AuthSession:
    """Create a new copy of this session"""
    new_session_id = generate_session_id()
    pass


def get_session(session_id: SessionID) -> AuthSession:
    pass


def invalidate_session(session_id: SessionID):
    pass


def generate_session_id() -> SessionID:
    return SessionID(secrets.token_urlsafe(32))
