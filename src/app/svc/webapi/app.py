from typing import Any, Literal, Self

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from pydantic.main import BaseModel

from app.config import get_config
from app.const import CUSTOM_HEADERS, SESSION_TOKEN_HEADER
from app.core.authn.exceptions import SessionNotFound
from app.core.authn.session import create_session, get_session_from_token
from app.core.authz.exceptions import AuthorizationError, FixActionFlow
from app.core.authz.subject import get_auth_subject_from_session
from app.core.context import RequestContext, request_context
from app.lib.context import scoped_context
from app.types.auth.session import SessionToken

from .routes import router


def create_app():
    config = get_config()

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

    # Exception handling -------------------------------------------------

    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(request: Request, exc: AuthorizationError):
        obj = AuthorizationErrorResponse.from_exception(exc)
        return JSONResponse(status_code=403, content=obj.model_dump())

    app.router.responses[403] = {"model": AuthorizationErrorResponse}

    # Routes -------------------------------------------------------------

    app.include_router(router)

    return app


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


# Exception handling -------------------------------------------------


class AuthorizationErrorResponse(BaseModel):
    msg_id: str | None
    msg_args: dict[str, str]
    fix_actions: list[AuthzErrorFixAction]

    @classmethod
    def from_exception(cls, exc: AuthorizationError) -> Self:
        fix_actions = [_fix_action_from_obj(x) for x in exc.fix_actions]
        return cls(msg_id=exc.msg_id, msg_args=exc.msg_args, fix_actions=fix_actions)


def _fix_action_from_obj(obj: Any) -> AuthzErrorFixAction:
    if isinstance(obj, FixActionFlow):
        return AuthzErrorFixActionFlow(
            kind="flow",
            flow_kind=obj.flow_kind,
            flow_params=obj.flow_params,
        )
    raise TypeError(f"{type(obj)} cannot be converted into AuthzErrorFixAction")


type AuthzErrorFixAction = AuthzErrorFixActionFlow  # union


class AuthzErrorFixActionFlow(BaseModel):
    kind: Literal["flow"]
    flow_kind: str
    flow_params: dict[str, Any]
