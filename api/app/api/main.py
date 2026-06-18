import secrets
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic.main import BaseModel

from app.api._utils.session_mgr import CurrentSessionManager
from app.config import load_config
from app.core.auth.exceptions import AuthorizationError
from app.types.session import AuthSession, SessionID

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


async def ensure_session(session_mgr: CurrentSessionManager):
    await session_mgr.ensure()


app.router.dependencies.append(Depends(ensure_session))

app.include_router(auth.router, prefix="/auth")


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


# Dev stuff ----------------------------------------------------------


@app.get("/_dev")
def get_dev(session_mgr: CurrentSessionManager):
    return {"session_id": session_mgr.current_session_id}


@app.post("/_dev/new-session")
async def post_dev_new_session(session_mgr: CurrentSessionManager):
    session = await session_mgr.invalidate()
    return {"session_id": session.session_id}


@app.post("/_dev/logout")
async def post_dev_logout(session_mgr: CurrentSessionManager):
    session = await session_mgr.invalidate()
    return {"session_id": session.session_id}


@app.post("/_dev/403")
def post_dev_403():
    raise AuthorizationError.definitive()


@app.post("/_dev/403-upgrade")
def post_dev_403_upgrade():
    raise AuthorizationError.require_upgrade(["scope1", ["scope2", "foobar"]])
