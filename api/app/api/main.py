import secrets
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

print(f"CORS Allow Origins: {config.cors_origins}")

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
async def handle_authorization_error(request, exc: AuthorizationError):
    return JSONResponse(
        status_code=403,
        content=AuthorizationErrorResponse(
            upgrade_possible=exc.upgrade_possible,
            require_scopes=exc.require_scopes,
        ),
    )


# Dev stuff ----------------------------------------------------------


class AuthSession(BaseModel):  # DUMMY
    session_id: str | None


def get_auth_session(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthSession:  # DUMMY
    if authorization is not None:
        kind, token = authorization.split(" ", 1)
        if kind.lower() == "bearer":
            return AuthSession(session_id=token)
    return AuthSession(session_id=None)


AuthSessionDep = Annotated[AuthSession, Depends(get_auth_session)]


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


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
