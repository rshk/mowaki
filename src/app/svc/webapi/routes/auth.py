from fastapi import APIRouter, status

from app.core.auth.session import invalidate_current_session

router = APIRouter(tags=["authentication"])


@router.post("/initiate/email-otp")
async def post_auth_initiate_email_top(address: str):
    """Initiate authentication using email OTP"""


@router.get("/session")
async def get_session_info():
    """Get information about the current session"""


@router.post("/session/invalidate", status_code=status.HTTP_204_NO_CONTENT)
async def post_auth_session_invalidate():
    """Invalidate current session"""

    await invalidate_current_session()
