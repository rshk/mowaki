from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from app import repo
from app.core.authn.exceptions import SessionNotFound
from app.core.authz.subject import get_auth_subject_from_session
from app.core.context import get_current_session as _get_current_session
from app.core.context import get_request_context
from app.exceptions import ObjectNotFound
from app.repo.auth.session import SessionUpdater
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

    session_id = get_current_session().session_id

    async with repo.auth.session.for_update(session_id) as upd:
        await _rotate_secret_if_needed(upd, force=force)

    await refresh_current_session()


async def add_session_assertion(
    params: BaseAssertionParams,
    expires_at: datetime | None = None,
):
    """
    Add an assertion to the current session.

    The session secret will also be rotated as needed.
    """

    assertion = Assertion(params=params, expires_at=expires_at)
    session_id = get_current_session().session_id

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.add_assertion(assertion)
        await _rotate_secret_if_needed(upd)

    await refresh_current_session()


async def set_current_user_id(user_id: UserID):
    """
    Change user_id associated with the current session.

    The session secret will also be rotated as needed.
    """

    session_id = get_current_session().session_id

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.set_current_user_id(user_id)
        await _rotate_secret_if_needed(upd)

    await refresh_current_session()


async def unset_current_user_id():
    """
    Unset the user_id associated with the current session.

    The session secret will also be rotated as needed.
    """

    session_id = get_current_session().session_id

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.unset_current_user_id()
        await _rotate_secret_if_needed(upd)

    await refresh_current_session()


@asynccontextmanager
async def edit_session_metadata() -> AsyncGenerator[AuthSessionMetadata]:
    """
    Context manager yielding an object that can be used to update the
    current session metadata.
    """

    session_id = get_current_session().session_id

    async with (
        repo.auth.session.for_update(session_id) as upd,
        upd.edit_metadata() as metadata,
    ):
        yield metadata

    await refresh_current_session()


async def _rotate_secret_if_needed(upd: SessionUpdater, force: bool = False):
    """
    Rotate secret and update context (if needed).

    This function is designed to use on an existing SessionUpdater
    instance, on an already-locked session, as opposed to
    rotate_current_session_secret() which creates a new transaction.
    """

    # *** SECURITY ***********************************************
    # Instead of calling rotate_current_session_secret(), we
    # do this atomically while the session object is locked
    # for update. This prevents a race condition which might
    # lead to a security issue: if an attacker is able to
    # issue a call to add an assertion at nearly the same time
    # a session-fixated user is issuing a similar request,
    # they might be able to still control the session with the
    # legitimate user's assertion added.
    # ************************************************************

    ctx = get_request_context()

    if (not force) and (ctx.new_session_token is not None):
        return  # already rotated

    session_id = ctx.auth_session.session_id
    new_secret = await upd.rotate_secret()
    new_token = format_session_token(session_id, new_secret)
    ctx.new_session_token = new_token
