from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from app import repo
from app.core.authn.exceptions import SessionNotFound
from app.core.context import get_current_session as _get_current_session
from app.core.context import get_request_context
from app.exceptions import ObjectNotFound
from app.repo.auth.session import SessionUpdater
from app.types.auth.assertions import Assertion
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
    token = format_session_token(session_id, session_secret)
    session = await repo.auth.session.get(session_id)
    return session, token


async def get_session_from_token(token: SessionToken) -> AuthSession:
    """
    Get an AuthSession from a Bearer token.

    The token secret is validated, and SessionNotFound raised if
    either the session doesn't exist, or the secret is invalid.

    Calling this function will also update the session last_used_at
    timestamp.
    """
    try:
        session_token = parse_session_token(token)
    except Exception as exc:
        raise SessionNotFound("Invalid session token") from exc

    try:
        session = await repo.auth.session.get_for_token(session_token)
    except ObjectNotFound as exc:
        raise SessionNotFound("Session not found for token") from exc

    # Update "last used" timestamp
    now = datetime.now(UTC)
    await repo.auth.session.set_last_used_at(session.session_id, now)
    session.last_used_at = now

    return session


async def get_session(session_id: SessionID) -> AuthSession:
    """
    Retrieve a session by ID.

    Does not update last_used_at.
    """
    return await repo.auth.session.get(session_id)


def format_session_token(
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
    await repo.auth.session.delete(session_id)


# Current session ----------------------------------------------------


def get_current_session() -> AuthSession:
    return _get_current_session()


@asynccontextmanager
async def edit_current_session() -> AsyncGenerator[SessionUpdater]:
    """
    Edit the current session.

    Editing a generic session (by id) is currently not supported, as
    we have no way to pass the newly-rotated token to the owner,
    basically rendering it useless.
    """

    ctx = get_request_context()
    session = ctx.auth_session
    async with repo.auth.session.for_update(session.session_id) as upd:
        try:
            yield upd

        finally:
            if upd.new_secret is not None:
                token = format_session_token(session.session_id, upd.new_secret)
                ctx.new_session_token = token


async def invalidate_current_session() -> AuthSession:
    """
    Delete the current session and create a new one.

    Returns the newly created session.
    """
    ctx = get_request_context()
    await invalidate_session(ctx.auth_session.session_id)
    new_session, new_token = await create_session()
    ctx.auth_session = new_session
    ctx.new_session_token = new_token
    return new_session


async def add_session_assertion(assertion: Assertion):
    """
    Grant a new assertion to the current session.

    Pre-existing assertions with the same text will be removed.
    """

    async with edit_current_session() as upd:
        session = await upd.get()
        assertions = _add_assertion_to_list(session.assertions, assertion)
        await upd.set_assertions(assertions)


def _add_assertion_to_list(assertions: list[Assertion], assertion: Assertion):
    key = assertion.get_assertion_text()
    return [
        *(x for x in assertions if x.get_assertion_text() != key),
        assertion,
    ]
