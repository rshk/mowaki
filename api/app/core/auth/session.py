import base64
import hashlib
import secrets
from datetime import timedelta

from app.core.auth.exceptions import SessionInvalid, SessionNotFound
from app.repo.session import hash_session_secret
from app.types.session import AuthSession, HashedSessionSecret, SessionID, SessionSecret, SessionToken
from app import repo

DUMMY_SESSION_DB: dict[SessionID, AuthSession] = {}

SOFT_SESSION_VALIDITY = timedelta(days=7)
HARD_SESSION_VALIDITY = timedelta(days=90)


async def create_session() -> tuple[AuthSession, SessionToken]:
    """
    Create a new (blank) session.

    Returns a tuple containing (session, token), where "token" is the
    session token (containing the clear-text secret) to be returned to
    the client, and used as Bearer token in subsequent requests.
    """

    session_id, session_secret = await repo.session.create()
    token = create_session_token(session_id, session_secret)
    session = await repo.session.get(session_id)
    return session, token


async def get_from_session_token(token: SessionToken) -> AuthSession:
    """
    Get an AuthSession from a Bearer token.

    The token secret is validated, and SessionNotFound raised if
    either the session doesn't exist, or the secret is invalid.
    """
    try:
        session_id, session_secret = parse_session_token(token)
    except Exception as exc:
        raise SessionNotFound("Invalid session token") from exc

    try:
        session = await repo.session.get_with_secret(session_id, session_secret)
    except Exception:
        raise SessionNotFound("Session not found for token")

    return session


async def get_session(session_id: SessionID) -> AuthSession:
    return await repo.session.get(session_id)


def create_session_token(session_id: SessionID, session_secret: SessionSecret) -> SessionToken:
    """Format a session token for returning to the client"""
    return SessionToken(f"{session_id}.{session_secret}")


def parse_session_token(token: SessionToken) -> tuple[SessionID, SessionSecret]:
    """Parse a session token into a a(id, secret) pair"""
    session_id, session_secret = token.split(".")
    return SessionID(session_id), SessionSecret(session_secret)


# async def recreate_session(session: AuthSession) -> AuthSession:
#     """
#     Invalidate a session and create a new one with a different id.

#     Used when adding authorization grants to a session, to preven
#     session fixation attacks.
#     """

#     # TODO: do this atomically instead?
#     if session.session_id is not None:
#         await invalidate_session(session.session_id)

#     new_session_id = generate_session_id()
#     new_session = deepcopy(session)
#     new_session.session_id = new_session_id
#     DUMMY_SESSION_DB[new_session_id] = new_session
#     return new_session


# async def duplicate_session(session: AuthSession) -> AuthSession:
#     """Create a new copy of this session"""

#     new_session_id = generate_session_id()
#     new_session = deepcopy(session)
#     new_session.session_id = new_session_id
#     DUMMY_SESSION_DB[new_session_id] = new_session
#     return new_session


async def invalidate_session(session_id: SessionID):
    """Delete this session from database"""
    await repo.session.invalidate(session_id)


# def generate_session_id() -> SessionID:
#     return SessionID(secrets.token_urlsafe(16))


# def generate_session_secret() -> SessionSecret:
#     return SessionSecret(secrets.token_urlsafe(16))
