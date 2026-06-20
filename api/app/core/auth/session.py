import base64
import hashlib
import secrets
from datetime import timedelta

from app.core.auth.exceptions import SessionInvalid, SessionNotFound
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

    session_id = generate_session_id()
    session_secret = generate_session_secret()
    secret_hash = hash_session_secret(session_secret)
    await repo.session.create(session_id=session_id, secret_hash=secret_hash)
    token = create_session_token(session_id, session_secret)
    session = await repo.session.get(session_id)
    return session, token


def create_session_token(session_id: SessionID, session_secret: SessionSecret) -> SessionToken:
    return SessionToken(f"{session_id}.{session_secret}")


async def get_from_session_token(token: SessionToken) -> AuthSession:
    try:
        session_id, session_secret = parse_session_token(token)
    except Exception as exc:
        raise SessionNotFound("Invalid session token") from exc

    try:
        session = await get_session(session_id)
        secret_hash = hash_session_secret(session_secret)
        if session.session_secret != secret_hash:
            # Hide this from the user, but we might want to log it as
            # a security event.
            raise SessionInvalid("Invalid session secret")
    except Exception:
        raise SessionNotFound("Session not found for token")

    return session


async def get_session(session_id: SessionID) -> AuthSession:
    return await repo.session.get(session_id)


def hash_session_secret(secret: SessionSecret) -> HashedSessionSecret:
    """Hash the session secret for storing in the database"""

    digest = hashlib.sha256(str(secret).encode()).digest()
    result = base64.urlsafe_b64encode(digest).decode("ascii")
    return HashedSessionSecret(result)


def parse_session_token(token: SessionToken) -> tuple[SessionID, SessionSecret]:
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

    DUMMY_SESSION_DB.pop(session_id, None)


async def refresh_soft_expiration_date(session_id: SessionID):
    pass


def generate_session_id() -> SessionID:
    return SessionID(secrets.token_urlsafe(16))


def generate_session_secret() -> SessionSecret:
    return SessionSecret(secrets.token_urlsafe(16))
