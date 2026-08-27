import logging
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from pydantic.main import BaseModel

from app.config import load_config
from app.const import CUSTOM_HEADERS, SESSION_TOKEN_HEADER
from app.core.authn.exceptions import SessionNotFound
from app.core.authn.session import create_session, get_or_create_session_from_token, get_session_from_token
from app.core.authz.exceptions import AuthorizationError
from app.core.context import RequestContext, request_context
from app.lib.context import scoped_context
from app.resources import initialize_resources
from app.types.auth.auth_subject import AuthSubject
from app.types.auth.session import AuthSession, SessionToken

from .routes import router

# Setup logging ------------------------------------------------------

# TODO: consider switching to something more modern, like logbook
# https://logbook.readthedocs.io/en/stable/

logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.addHandler(logging_handler)
root_logger.setLevel(logging.INFO)

app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)


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
async def request_context_middleware(request: Request, call_next):
    """
    Middlware function to add RequestContext during processing.

    - Parse session token from the request (Authorization: Bearer) and
      retrieve the associated session
    - If no valid session token was provided, create a new session
    - Create AuthSubject from assertions contained in the session
    - If a new session was created at any point, set a
      X-Set-Session-Token header on the response
    """

    if request.method == "OPTIONS":
        return await call_next(request)

    token = get_session_token_from_request(request)
    session = None
    new_token = None

    if token is not None:
        try:
            session = await get_session_from_token(token)
        except SessionNotFound:
            pass

    if session is None:
        # TODO: pass metadata from request into the new session
        session, new_token = await create_session()

    auth_subject = await get_auth_subject_from_session(session)

    ctx = RequestContext(
        auth_session=session,
        new_session_token=new_token,
        auth_subject=auth_subject,
    )

    with scoped_context(request_context, ctx):
        # Wrap the rest of the request processing
        response: Response = await call_next(request)

    # If a new session was created at any point during request
    # processing, return the new token to the user.
    if (value := ctx.new_session_token) is not None:
        response.headers[SESSION_TOKEN_HEADER] = value

    return response


def get_session_token_from_request(request: Request) -> SessionToken | None:
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


async def get_auth_subject_from_session(session: AuthSession) -> AuthSubject:
    """
    Create an AuthSubject() instance from a Session.
    """
    return AuthSubject()  # TODO: implement this


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


app.router.responses[403] = {"model": AuthorizationErrorResponse}

# Routes -------------------------------------------------------------

app.include_router(router)
