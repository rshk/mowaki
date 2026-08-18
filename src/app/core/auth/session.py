from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app import repo
from app.core.auth.exceptions import SessionNotFound
from app.core.context import get_current_session as _get_current_session
from app.core.context import get_request_context
from app.exceptions import ObjectNotFound
from app.repo.auth.session import SessionUpdater
from app.types.auth.session import (
    AuthSession,
    SessionID,
    SessionSecret,
    SessionToken,
    SessionTokenData,
)


async def create_session() -> tuple[AuthSession, SessionToken]:
    """
    Create a new (blank) session.

    Returns a tuple containing (session, token), where "token" is the
    session token (containing the clear-text secret) to be returned to
    the client, and used as Bearer token in subsequent requests.
    """

    session_id, session_secret = await repo.auth.session.create()
    token = create_session_token(session_id, session_secret)
    session = await repo.auth.session.get(session_id)
    return session, token


async def get_session_from_token(token: SessionToken) -> AuthSession:
    """
    Get an AuthSession from a Bearer token.

    The token secret is validated, and SessionNotFound raised if
    either the session doesn't exist, or the secret is invalid.
    """
    try:
        session_token = parse_session_token(token)
    except Exception as exc:
        raise SessionNotFound("Invalid session token") from exc

    try:
        session = await repo.auth.session.get_for_token(session_token)
    except ObjectNotFound:
        raise SessionNotFound("Session not found for token")

    return session


async def get_or_create_session_from_token(
    token: SessionToken | None,
) -> tuple[AuthSession, SessionToken | None]:
    if token is not None:
        try:
            session = await get_session_from_token(token)
        except SessionNotFound:
            pass
        else:
            return session, None  # Existing session

    return await create_session()


async def get_session(session_id: SessionID) -> AuthSession:
    return await repo.auth.session.get(session_id)


def create_session_token(
    session_id: SessionID, session_secret: SessionSecret
) -> SessionToken:
    """Format a session token for returning to the client"""
    return SessionToken(f"{session_id}.{session_secret}")


def parse_session_token(token: SessionToken) -> SessionTokenData:
    """Parse a session token into a a(id, secret) pair"""
    session_id, session_secret = token.split(".")
    return SessionTokenData(
        session_id=SessionID(session_id),
        session_secret=SessionSecret(session_secret),
    )


async def invalidate_session(session_id: SessionID):
    """Delete this session from database"""
    await repo.auth.session.invalidate(session_id)


# Current session ----------------------------------------------------


def get_current_session() -> AuthSession:
    return _get_current_session()


@asynccontextmanager
async def current_session_updater() -> AsyncGenerator[SessionUpdater]:
    ctx = get_request_context()
    session = ctx.auth_session
    async with repo.auth.session.for_update(session.session_id) as upd:
        try:
            yield upd

        finally:
            if upd.new_secret is not None:
                token = create_session_token(session.session_id, upd.new_secret)
                ctx.new_session_token = token


async def invalidate_current_session():
    ctx = get_request_context()
    await invalidate_session(ctx.auth_session.session_id)
    new_session, new_token = await create_session()
    ctx.auth_session = new_session
    ctx.new_session_token = new_token
