from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.core.authn.session import get_session
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
