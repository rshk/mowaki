from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from pydantic.main import BaseModel

from app.config import load_config
from app.const import CUSTOM_HEADERS, SESSION_TOKEN_HEADER
from app.core.auth.exceptions import AuthorizationError
from app.core.auth.session import (
    edit_current_session,
    get_or_create_session_from_token,
    invalidate_current_session,
)
from app.core.context import RequestContext, get_current_session, request_context
from app.lib.context import scoped_context
from app.resources import initialize_resources
from app.types.auth.authorization import AuthSubject
from app.types.auth.session import SessionToken

# from . import auth

# Initialize configuration and resources -----------------------------

config = load_config()
resources = initialize_resources(config, set_context=True)


# Create FastAPI app -------------------------------------------------

app = FastAPI()


# CORS middleware ----------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=False,  # We don't use cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=CUSTOM_HEADERS,
)


# Middleware to setup context ----------------------------------------


@app.middleware("http")
async def setup_request_context_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    token = get_request_session_token(request)
    session, new_token = await get_or_create_session_from_token(token)

    # TODO: update session with metadata from the request, if new

    ctx = RequestContext(
        auth_session=session,
        new_session_token=new_token,
        auth_subject=AuthSubject(),
    )
    with scoped_context(request_context, ctx):
        response: Response = await call_next(request)

    # If a new session was created at any point during request
    # processing, return the new token to the user.
    if (value := ctx.new_session_token) is not None:
        response.headers[SESSION_TOKEN_HEADER] = value

    return response


def get_request_session_token(request: Request) -> SessionToken | None:
    authorization = request.headers.get("Authorization")
    scheme, credentials = get_authorization_scheme_param(authorization)
    if not (authorization and scheme and credentials):
        return None
    if scheme.lower() != "bearer":
        return None
    return SessionToken(credentials)


def get_client_ip_address(request: Request) -> str | None:
    # ****************************************************************
    # FIXME: get this from a header instead! But we want some
    # configuration around that, not just magically try to autoguess
    # which header contains the address, or we'd be vulnerable to
    # spoofing!
    # ****************************************************************
    if request.client is None:
        return None
    return request.client.host


def get_user_agent(request: Request) -> str | None:
    return request.headers.get("User-Agent")


# Exception handling -------------------------------------------------


class AuthorizationErrorResponse(BaseModel):
    upgrade_possible: bool
    require_scopes: list[Any]


@app.exception_handler(AuthorizationError)
async def handle_authorization_error(request: Request, exc: AuthorizationError):
    obj = AuthorizationErrorResponse(
        upgrade_possible=exc.upgrade_possible,
        require_scopes=exc.require_scopes,
    )
    return JSONResponse(
        status_code=403,
        content=obj.model_dump(),
    )


responses = {
    403: {
        "model": AuthorizationErrorResponse,
    }
}

app.router.responses[403] = {"model": AuthorizationErrorResponse}


# Include routers ----------------------------------------------------

# app.include_router(auth.router, prefix="/auth")


# Dev stuff ----------------------------------------------------------


@app.get("/_dev")
def get_dev():
    session = get_current_session()
    return {"session_id": session.session_id}


@app.post("/_dev/logout")
async def post_dev_logout():
    await invalidate_current_session()
    session = get_current_session()
    return {"session_id": session.session_id}


@app.post("/_dev/rotate")
async def post_dev_rotate_secret():
    async with edit_current_session() as upd:
        await upd.rotate_secret()

    session = get_current_session()
    return {"session_id": session.session_id}


@app.post("/_dev/403")
def post_dev_403():
    raise AuthorizationError.definitive()


@app.post("/_dev/403-upgrade")
def post_dev_403_upgrade():
    raise AuthorizationError.require_upgrade(["scope1", ["scope2", "foobar"]])
