from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app import repo
from app.core.authn.exceptions import ConflictingAssertion, SessionNotFound
from app.core.context import get_current_session as _get_current_session
from app.core.context import get_request_context
from app.exceptions import ObjectNotFound
from app.repo.auth.session import SessionUpdater
from app.types.auth import assertions
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
    """
    try:
        session_token = parse_session_token(token)
    except Exception as exc:
        raise SessionNotFound("Invalid session token") from exc

    try:
        session = await repo.auth.session.get_for_token(session_token)
    except ObjectNotFound as exc:
        raise SessionNotFound("Session not found for token") from exc

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


async def add_session_assertion(new_assertion: Assertion):
    """
    Grant a new assertion to the current session.

    Also does some processing:

    - Older identical assertions are removed
    - If there are incompatible existing assertions, the new one is dropped
    """

    async with edit_current_session() as upd:
        session = upd.session
        new_assertions = [*session.assertions]

        if isinstance(new_assertion, assertions.EmailOTP):
            for new_assertion in new_assertions:
                if isinstance(new_assertion, assertions.EmailOTP):
                    if new_assertion.email_address != new_assertion.email_address:
                        raise ConflictingAssertion(
                            "Conflicting EmailOTP assertions found in session"
                        )

            new_assertions = [
                x for x in new_assertions if not isinstance(x, assertions.EmailOTP)
            ]

        elif isinstance(new_assertion, assertions.PasskeyAuth):
            pass

        for new_assertion in session.assertions:
            pass

        # TODO: ensure assertion is compatible before adding it!
        # Eg. conflicting email / user_id assertions are not allowed.

        await upd.add_assertion(new_assertion)
