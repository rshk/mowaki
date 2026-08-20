from fastapi import APIRouter, status

from app.core.authn.authn_email_otp import (
    initiate_with_email_otp,
    upgrade_with_email_otp,
)
from app.core.authn.session import invalidate_current_session
from app.types.auth.challenges import ChallengeRequest

router = APIRouter(tags=["authentication"])


@router.post("/initiate/email-otp")
async def post_auth_initiate_email_top(address: str) -> ChallengeRequest:
    """Initiate authentication using email OTP"""

    return await initiate_with_email_otp(address)


@router.post("/upgrade/email-otp")
async def post_auth_upgrade_email_top(address: str) -> ChallengeRequest:
    """Upgrade authentication using email OTP"""

    # TODO: in some cases, we already have an email address associated
    # with this user, so upgrade doesn't necessarily need to specify
    # one; in fact it might even be undesirable as it could lead to an
    # inconsistent state challenge that will turn the session to an
    # invalid state once solved.
    #
    # Instead, we could:
    # - Check assertions for a previous EmailOTP or related challenge
    # - Check assertions for a user_id, use it for email OTP
    # To add a secondary email address, we could have a separate OTP
    # verification method?

    return await upgrade_with_email_otp(address)


@router.post("/challenge/respond")
async def post_challenge_respond():
    pass


# /upgrade/... methods to add / refresh assertions


@router.get("/session")
async def get_session_info():
    """Get information about the current session"""


@router.post("/session/invalidate", status_code=status.HTTP_204_NO_CONTENT)
async def post_auth_session_invalidate():
    """Invalidate current session"""

    await invalidate_current_session()
