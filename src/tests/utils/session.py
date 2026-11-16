from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.core.authn.session import create_session, get_session
from app.core.authz.subject import get_auth_subject_from_session
from app.core.context import RequestContext, request_context
from app.lib.context import scoped_context
from app.types.auth.session import SessionID


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


class TestingRequestSession:
    __test__ = False  # this is **not** a test case

    def __init__(self):
        self.session_id: SessionID | None = None
        self._context_token = None

    async def __aenter__(self):
        if self.session_id is None:
            session, _ = await create_session()
            self.session_id = session.session_id
        else:
            session = await get_session(self.session_id)

        auth_subject = await get_auth_subject_from_session(session)
        ctx = RequestContext(
            auth_session=session,
            new_session_token=None,
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
