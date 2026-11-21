from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from app import repo
from app.core.authn.exceptions import SessionNotFound
from app.core.authz.subject import get_auth_subject_from_session
from app.core.context import get_current_session as _get_current_session
from app.core.context import get_request_context
from app.exceptions import ObjectNotFound
from app.types.auth.assertions import Assertion, BaseAssertionParams
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
    ctx.auth_subject = await get_auth_subject_from_session(ctx.auth_session)


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


async def rotate_current_session_secret(force: bool = False):
    """
    Rotate secret for the current session.

    This will create a new session token and return it to the client.
    """

    ctx = get_request_context()
    session = ctx.auth_session

    # Session secret was already rotated during this request (or a new
    # session was created), so we don't need to rotate it again.
    if (not force) and (ctx.new_session_token is not None):
        return

    async with repo.auth.session.for_update(session.session_id) as upd:
        new_secret = await upd.rotate_secret()

    new_token = format_session_token(session.session_id, new_secret)
    ctx.new_session_token = new_token

    await refresh_current_session()


async def add_session_assertion(
    params: BaseAssertionParams,
    expires_at: datetime | None = None,
):
    """
    Add a new assertion to the current session.

    The session secret will be rotated as a result.
    """

    assertion = Assertion(params=params, expires_at=expires_at)
    ctx = get_request_context()
    session_id = ctx.auth_session.session_id

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.add_assertion(assertion)

        if ctx.new_session_token is None:
            # Rotate secret and update context, if needed
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
        # FIXME: we might want to check that the session has a valid
        # assertion, if this method is to be exposed directly.

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

    await refresh_current_session()
