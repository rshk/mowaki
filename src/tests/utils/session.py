from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from app.core.authn.flows.actions import get_flow, get_flow_processor
from app.core.authn.flows.email_otp_auth import EmailOTPAuthFlowProcessor
from app.core.authn.session import get_session, get_session_from_token
from app.core.authz.subject import get_auth_subject_from_session
from app.core.context import RequestContext, request_context
from app.lib.context import scoped_context
from app.types.auth.session import SessionID, SessionToken
from fastapi.security.utils import get_authorization_scheme_param
from httpx2 import AsyncClient


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
