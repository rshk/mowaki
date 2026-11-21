from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Literal

from app import repo
from app.core.authn.session import create_session, get_session
from app.core.authz.subject import get_auth_subject_from_session
from app.core.context import RequestContext, request_context
from app.lib.context import scoped_context
from app.types.auth.assertions import Assertion, BaseAssertionParams
from app.types.auth.session import AuthSession, SessionID, SessionToken
from app.types.user import UserID


@asynccontextmanager
async def set_request_context_from_session_id(
    session_id: SessionID,
) -> AsyncGenerator[RequestContext]:
    session = await get_session(session_id)
    auth_subject = await get_auth_subject_from_session(session)
    ctx = RequestContext(
        auth_session=session,
        new_session_token=None,
        auth_subject=auth_subject,
    )
    with scoped_context(request_context, ctx):
        yield ctx


class TestingRequestContextManager:
    __test__ = False  # this is **not** a test case

    session_id: SessionID | None
    new_session_token: SessionToken | Literal[True] | None
    _new_session_assertions: list[Assertion]
    _new_session_current_user_id: UserID | bool | None
    _new_session_last_used_at: datetime | bool | None

    def __init__(
        self,
        session_id: SessionID | None = None,
        new_session_token: SessionToken | Literal[True] | None = None,
        assertions: list[Assertion | BaseAssertionParams] | None = None,
        current_user_id: UserID | bool | None = None,
        last_used_at: datetime | bool | None = None,
    ):
        """
        Context manager class to handle setting a RequestContext in a
        testing environment.

        Args:
            session_id:
                If set, the request context will be set to use a
                specific session. Otherwise, one will be created as
                needed.

            new_session_token:
                If set to a SessionToken, set it on the RequestContext.
                If set to True, when a new session is created, its
                token will be set on the RequestContext.

            assertion:
                List of Assertion (or assertion parameters) instances
                to be set on the newly created session.

            current_user_id:
                If set to a UserID, the new session will be attached
                to this user. If set to True, a new user will be
                created and attached to the session.

            last_used_at:
                If set to a datetime, the session's last_used_at will
                be set to this time. If set to True, the session's
                last_used_at will be set to the current time.
        """

        self.session_id = session_id
        self.new_session_token = new_session_token

        # Set parameters for new session creation
        self._new_session_assertions = self._prepare_assertions(assertions)
        self._new_session_current_user_id = current_user_id
        self._new_session_last_used_at = last_used_at

        self._context_token = None

    async def _create_session(self) -> tuple[AuthSession, SessionToken | None]:
        session, new_token = await create_session()

        if self._new_session_current_user_id is True:
            user_id = await repo.user.create(email="user@example.com")
            self._new_session_current_user_id = user_id
        else:
            user_id = self._new_session_current_user_id or None

        async with repo.auth.session.for_update(session.session_id) as upd:
            if self._new_session_last_used_at:
                last_used_at = self._new_session_last_used_at
                if not isinstance(last_used_at, datetime):
                    last_used_at = None  # Current time
                await upd.set_last_used_at(last_used_at)

            await upd.set_assertions(self._new_session_assertions)

            if user_id is not None:
                await upd.set_current_user_id(user_id)

        # If this is not supposed to look like a brand new session,
        # don not return a new token.
        if not self.new_session_token:
            new_token = None

        # Refresh session object with new updates
        session = await get_session(session.session_id)

        return session, new_token

    def _prepare_assertions(
        self, assertions: list[Assertion | BaseAssertionParams] | None
    ) -> list[Assertion]:
        if assertions is None:
            return []

        def _get_assertion(ass: Assertion | BaseAssertionParams):
            if isinstance(ass, Assertion):
                return ass
            return Assertion.from_params(ass)

        return [_get_assertion(x) for x in assertions]

    async def __aenter__(self):
        if self.session_id is None:
            # Ensure a session is attached to this context
            session, new_token = await self._create_session()
            self.session_id = session.session_id
        else:
            session = await get_session(self.session_id)
            new_token = None

        auth_subject = await get_auth_subject_from_session(session)
        ctx = RequestContext(
            auth_session=session,
            new_session_token=new_token,
            auth_subject=auth_subject,
        )

        self._context_token = request_context.set(ctx)

        return ctx

    async def __aexit__(self, exc_type, exc_value, traceback):
        ctx = request_context.get()
        if self._context_token is not None:
            request_context.reset(self._context_token)
            self._context_token = None

        # Preserve whatever session was current
        self.session_id = ctx.auth_session.session_id
