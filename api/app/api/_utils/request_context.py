from typing import Annotated

from fastapi import Depends, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth.session import get_or_create_session_from_token
from app.core.context import RequestContext
from app.lib.context import scoped_context
from app.types.session import SessionToken
from app.core.context import request_context


BearerToken = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(HTTPBearer(auto_error=False)),
]


async def setup_request_context(bearer_token: BearerToken, response: Response):

    token = SessionToken(bearer_token.credentials) if bearer_token is not None else None
    session, new_token = await get_or_create_session_from_token(token)

    ctx = RequestContext(auth_session=session, new_session_token=new_token)
    with scoped_context(request_context, ctx):
        yield ctx

    # If a new session was created at any point, we want to return the
    # new token to the user.
    if ctx.new_session_token is not None:
        response.headers["X-Set-Session-Token"] = ctx.new_session_token
