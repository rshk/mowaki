import secrets
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic.main import BaseModel

from app.config import load_config

from . import auth

config = load_config()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=False,  # We don't use cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-set-session-id"],
)

bearer_token = HTTPBearer(auto_error=False)
BearerToken = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_token)]


class AuthSession(BaseModel):  # DUMMY
    session_id: str | None

    # Whether the session was created during this request.
    # Controls whether the X-Set-Session-Id header will be set.
    is_new_session: bool = False

    @classmethod
    def new(cls):
        return AuthSession(session_id=generate_session_id(), is_new_session=True)


def get_auth_session(credentials: BearerToken) -> AuthSession:
    if credentials is not None:
        # TODO: retrieve session from storage. If no valid session was
        # found, simply create a new one
        return AuthSession(session_id=credentials.credentials)
    return AuthSession.new()


AuthSessionDep = Annotated[AuthSession, Depends(get_auth_session)]


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


async def add_set_session_id_header(response: Response, session: AuthSessionDep):
    if session.is_new_session and (session.session_id is not None):
        response.headers["X-Set-Session-Id"] = session.session_id


app.router.dependencies.append(Depends(add_set_session_id_header))


# --------------------------------------------------------------------


app.include_router(auth.router, prefix="/auth")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


# Exception handling -------------------------------------------------


class AuthorizationError(Exception):
    upgrade_possible: bool
    require_scopes: list[Any]

    def __init__(
        self, upgrade_possible: bool = False, require_scopes: list[Any] | None = None
    ):
        self.upgrade_possible = upgrade_possible
        if require_scopes is None:
            require_scopes = []
        self.require_scopes = require_scopes

    @classmethod
    def definitive(cls):
        return AuthorizationError(upgrade_possible=False)

    @classmethod
    def require_upgrade(cls, require_scopes: list[Any]):
        return AuthorizationError(upgrade_possible=True, require_scopes=require_scopes)


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


# Dev stuff ----------------------------------------------------------

responses = {
    403: {
        "model": AuthorizationErrorResponse,
    }
}

app.router.responses[403] = {"model": AuthorizationErrorResponse}


@app.get("/_dev")
def get_dev(session: AuthSessionDep):
    return {"session_id": session.session_id}


@app.post("/_dev")
def post_dev(response: Response, session: AuthSessionDep):
    # if session.session_id is None:
    #     # Create new session
    #     response.headers["X-Set-Session-Id"] = generate_session_id()
    return {"session_id": session.session_id}


@app.post("/_dev/new-session")
def post_dev_new_session(response: Response, session: AuthSessionDep):
    # Create new session
    session_id = generate_session_id()
    response.headers["X-Set-Session-Id"] = session_id
    return {"session_id": session_id}


@app.post("/_dev/logout")
def post_dev_logout(response: Response, session: AuthSessionDep):
    if session.session_id is None:
        # Create new session
        response.headers["X-Set-Session-Id"] = ""
    return {"session_id": session.session_id}


@app.post("/_dev/403")
def post_dev_403(response: Response, session: AuthSessionDep):
    raise AuthorizationError.definitive()


@app.post("/_dev/403-upgrade")
def post_dev_403_upgrade(response: Response, session: AuthSessionDep):
    raise AuthorizationError.require_upgrade(["scope1", ["scope2", "foobar"]])
