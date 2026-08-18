from fastapi import APIRouter

from app.core.auth.exceptions import AuthorizationError
from app.core.auth.session import (
    edit_current_session,
    get_current_session,
    invalidate_current_session,
)

router = APIRouter(tags=["development"])


@router.get("")
def get_dev():
    session = get_current_session()
    return {"session_id": session.session_id}


@router.post("logout")
async def post_dev_logout():
    await invalidate_current_session()
    session = get_current_session()
    return {"session_id": session.session_id}


@router.post("rotate")
async def post_dev_rotate_secret():
    async with edit_current_session() as upd:
        await upd.rotate_secret()

    session = get_current_session()
    return {"session_id": session.session_id}


@router.post("403")
def post_dev_403():
    raise AuthorizationError.definitive()


@router.post("403-upgrade")
def post_dev_403_upgrade():
    raise AuthorizationError.require_upgrade(["scope1", ["scope2", "foobar"]])
