from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import AsyncGenerator

from app import repo
from app.core.authn.exceptions import SessionNotFound
from app.core.authz.exceptions import AuthorizationError
from app.core.context import get_current_session as _get_current_session
from app.core.context import get_request_context
from app.exceptions import ObjectNotFound
from app.types.auth.assertions import Assertion
from app.types.auth.session import (
    AuthSession,
    AuthSessionMetadata,
    SessionID,
    SessionSecret,
    SessionToken,
    SessionTokenData,
)
from app.types.user import UserID


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

    Calling this function will also update ``last_used_at``.
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
    """Get the current session, from context"""
    return _get_current_session()


async def refresh_current_session():
    """Refresh the current session contained in context"""
    ctx = get_request_context()
    session_id = ctx.auth_session.session_id
    ctx.auth_session = await get_session(session_id)


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


async def rotate_current_session_secret():
    ctx = get_request_context()
    session = ctx.auth_session

    async with repo.auth.session.for_update(session.session_id) as upd:
        new_secret = await upd.rotate_secret()

    new_token = format_session_token(session.session_id, new_secret)
    ctx.new_session_token = new_token

    await refresh_current_session()


async def add_session_assertion(assertion: Assertion):
    """Grant a new assertion to the current session.

    - Pre-existing assertions with the same text will be removed.
    - If session.current_user_id is not set, set it to the one
      provided by the new assertion (if any).
    - Rotate the session secret
    """

    ctx = get_request_context()
    session_id = ctx.auth_session.session_id

    async with repo.auth.session.for_update(session_id) as upd:
        session = await upd.get()

        await upd.add_assertion(assertion)

        # Make sure current_user_id is still valid, unset it
        # otherwise.
        session = await upd.get()
        if session.current_user_id not in _get_allowable_user_ids(session):
            await upd.unset_current_user_id()
            session.current_user_id = None

        # Set current_user_id, if not previously set
        if session.current_user_id is None:
            user_id = assertion.get_user_id()
            if user_id is not None:
                await upd.set_current_user_id(user_id)

        # Rotate secret and update context
        new_secret = await upd.rotate_secret()
        new_token = format_session_token(session_id, new_secret)
        ctx.new_session_token = new_token

    await refresh_current_session()


async def set_current_user_id(user_id: UserID):
    """
    Change user_id associated with the current session

    - Check that at least one assertion contains the selected user_id
    - Rotates the session secret
    """

    ctx = get_request_context()
    session_id = ctx.auth_session.session_id

    async with repo.auth.session.for_update(session_id) as upd:
        session = await upd.get()
        if (user_id is not None) and (user_id not in _get_allowable_user_ids(session)):
            raise AuthorizationError("Requested user id is not allowable")

        await upd.set_current_user_id(user_id)

        # Rotate secret and update context
        new_secret = await upd.rotate_secret()
        new_token = format_session_token(session_id, new_secret)
        ctx.new_session_token = new_token

    await refresh_current_session()


def _get_allowable_user_ids(session: AuthSession) -> set[UserID]:
    """Get a list of user IDs associated with this session"""
    result = set()
    for assertion in session.assertions:
        user_id = assertion.get_user_id()
        if user_id is not None:
            result.add(user_id)
    return result


async def unset_current_user_id():
    ctx = get_request_context()
    session_id = ctx.auth_session.session_id

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.unset_current_user_id()

        # Rotate secret and update context
        new_secret = await upd.rotate_secret()
        new_token = format_session_token(session_id, new_secret)
        ctx.new_session_token = new_token

    await refresh_current_session()


@asynccontextmanager
async def edit_session_metadata() -> AsyncGenerator[AuthSessionMetadata]:
    ctx = get_request_context()
    session_id = ctx.auth_session.session_id

    async with (
        repo.auth.session.for_update(session_id) as upd,
        upd.edit_metadata() as metadata,
    ):
        yield metadata
