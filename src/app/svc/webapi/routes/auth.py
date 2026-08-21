from typing import Annotated

from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.config import get_config
from app.core.authn.flows.actions import create_flow, process_flow_action
from app.core.authn.flows.base import FlowStatus
from app.core.authn.flows.email_otp_auth import FLD_EMAIL
from app.core.context import get_current_session
from app.types.auth.auth_flow import FlowAction, FlowID

router = APIRouter(tags=["authentication"])


class InitEmailOtpInput(BaseModel):
    address: str


@router.post("/init/email-otp")
async def post_auth_init_email_otp(body: InitEmailOtpInput):
    # Create a flow and set an email address to it.
    # This will trigger the notification email containing the OTP code
    flow_id = await create_flow(kind="email-otp-auth")
    await process_flow_action(flow_id, FlowAction({FLD_EMAIL: body.address}))
    return {  # TODO: return some kind of standardized response
        "flow_id": flow_id,
        "msg": "Check your email",
    }


@router.post("/flow/{flow_id}")
async def post_flow_action(
    flow_id: FlowID,
    action: Annotated[FlowAction, Body(default_factory=dict)],
):
    result = await process_flow_action(flow_id, action)

    status = {
        FlowStatus.IN_PROGRESS: "in-progress",
        FlowStatus.SUCCESS: "success",
        FlowStatus.FAILED: "failed",
    }[result]

    return {
        "flow_id": flow_id,
        "action": action,
        "status": status,
    }


# @router.post("/initiate/email-otp")
# async def post_auth_initiate_email_otp(body: InitiateEmailOtpInput) -> ChallengeRequest:
#     """Initiate authentication using email OTP"""

#     return await initiate_with_email_otp(body.address)


# class UpgradeEmailOtpInput(BaseModel):
#     address: str | None


# @router.post("/upgrade/email-otp")
# async def post_auth_upgrade_email_top(body: UpgradeEmailOtpInput) -> ChallengeRequest:
#     """Upgrade authentication using email OTP"""

#     # TODO: in some cases, we already have an email address associated
#     # with this user, so upgrade doesn't necessarily need to specify
#     # one; in fact it might even be undesirable as it could lead to an
#     # inconsistent state challenge that will turn the session to an
#     # invalid state once solved.
#     #
#     # Instead, we could:
#     # - Check assertions for a previous EmailOTP or related challenge
#     # - Check assertions for a user_id, use it for email OTP
#     # To add a secondary email address, we could have a separate OTP
#     # verification method?

#     return await upgrade_with_email_otp(body.address)


# @router.post("/challenge/respond")
# async def post_challenge_respond(resp: ChallengeResponse):
#     print("CHALLENGE RESPOND", resp)
#     await process_challenge_response(resp)


# # /upgrade/... methods to add / refresh assertions


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


# @router.post("/session/invalidate", status_code=status.HTTP_204_NO_CONTENT)
# async def post_auth_session_invalidate():
#     """Invalidate current session"""

#     await invalidate_current_session()
