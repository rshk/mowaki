from fastapi import APIRouter

from app.core.authn.session import (
    get_current_session,
    invalidate_current_session,
    rotate_current_session_secret,
)
from app.core.authz.exceptions import AuthorizationError

router = APIRouter(tags=["development"])


@router.get("/")
def get_dev():
    session = get_current_session()
    return {"session_id": session.session_id}


@router.post("/logout")
async def post_dev_logout():
    await invalidate_current_session()
    session = get_current_session()
    return {"session_id": session.session_id}


@router.post("/rotate")
async def post_dev_rotate_secret():
    await rotate_current_session_secret()
    session = get_current_session()
    return {"session_id": session.session_id}


@router.post("/403")
def post_dev_403():
    raise AuthorizationError("You cannot do this")


@router.post("/403-upgrade")
def post_dev_403_upgrade():
    raise (
        AuthorizationError("Need more authn")
        .set_user_message("LOGIN_REQUIRED")
        .add_fix_action_flow("email-otp-auth")
        .add_fix_action_flow("passkey-auth")
    )
