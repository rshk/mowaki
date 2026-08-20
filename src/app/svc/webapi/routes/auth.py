from fastapi import APIRouter, status
from pydantic import BaseModel

from app.config import get_config
from app.core.authn.authn_email_otp import (
    initiate_with_email_otp,
    upgrade_with_email_otp,
)
from app.core.authn.challenge import process_challenge_response
from app.core.authn.session import get_current_session, invalidate_current_session
from app.types.auth.challenges import ChallengeRequest, ChallengeResponse

router = APIRouter(tags=["authentication"])


class InitiateEmailOtpInput(BaseModel):
    address: str


@router.post("/initiate/email-otp")
async def post_auth_initiate_email_otp(body: InitiateEmailOtpInput) -> ChallengeRequest:
    """Initiate authentication using email OTP"""

    return await initiate_with_email_otp(body.address)


class UpgradeEmailOtpInput(BaseModel):
    address: str | None


@router.post("/upgrade/email-otp")
async def post_auth_upgrade_email_top(body: UpgradeEmailOtpInput) -> ChallengeRequest:
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

    return await upgrade_with_email_otp(body.address)


@router.post("/challenge/respond")
async def post_challenge_respond(resp: ChallengeResponse):
    print("CHALLENGE RESPOND", resp)
    await process_challenge_response(resp)


# /upgrade/... methods to add / refresh assertions


@router.get("/session")
async def get_session_info():
    """Get information about the current session"""

    session = get_current_session()

    config = get_config()
    if not config.development_mode:
        return {"session_id": session.session_id}

    # Allow inspecting session details, but only for development!
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "last_used_at": session.last_used_at,
        "metadata": session.metadata,
        "assertions": session.assertions,
    }


@router.post("/session/invalidate", status_code=status.HTTP_204_NO_CONTENT)
async def post_auth_session_invalidate():
    """Invalidate current session"""

    await invalidate_current_session()
