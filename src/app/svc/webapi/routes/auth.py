from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Self

from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.config import get_config
from app.core.authn.flows.actions import (
    create_flow,
    delete_flow,
    get_flow_expiration_date,
    get_flow_processor,
    process_flow_action,
)
from app.core.authn.flows.actions import get_flow as _get_flow
from app.core.context import get_current_session
from app.types.auth.auth_flow import (
    AuthFlow,
    FlowAction,
    FlowChallenge,
    FlowID,
    FlowKind,
)

router = APIRouter(tags=["authentication"])


class PublicFlowInfo(BaseModel):
    flow_id: FlowID
    created_at: datetime
    expires_at: datetime
    kind: FlowKind
    challenge: FlowChallenge
    status: Literal["in-progress", "expired", "completed", "canceled"]

    @classmethod
    def from_flow(cls, flow: AuthFlow) -> Self:
        return cls(
            flow_id=flow.flow_id,
            created_at=flow.created_at,
            expires_at=get_flow_expiration_date(flow),
            kind=flow.kind,
            challenge=FlowChallenge(
                get_flow_processor(flow.kind).get_challenge(flow.state)
            ),
            status="in-progress",  # Or it would have failed
        )


@router.post("/flow/init/{flow_kind}")
async def init_flow(flow_kind: FlowKind) -> PublicFlowInfo:
    """Initiate an authentication flow of the specified type"""
    flow_id = await create_flow(kind=flow_kind)
    flow = await _get_flow(flow_id)
    return PublicFlowInfo.from_flow(flow)


@router.get("/flow/{flow_id}")
async def get_flow(flow_id: FlowID):
    flow = await _get_flow(flow_id)
    return PublicFlowInfo.from_flow(flow)


class FlowStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"


class FlowActionResult(BaseModel):
    flow: PublicFlowInfo | None
    status: FlowStatus


@router.post("/flow/{flow_id}")
async def post_flow_action(
    flow_id: FlowID,
    action: Annotated[FlowAction, Body(default_factory=dict)],
) -> FlowActionResult:
    result = await process_flow_action(flow_id, action)
    if result.is_completed():
        return FlowActionResult(
            flow=None,
            status=FlowStatus.SUCCESS if result.result else FlowStatus.FAILED,
        )

    flow = await _get_flow(flow_id)
    return FlowActionResult(
        flow=PublicFlowInfo.from_flow(flow),
        status=FlowStatus.IN_PROGRESS,
    )


@router.delete("/flow/{flow_id}")
async def cancel_flow(flow_id: FlowID):
    """Cancel / abort an in-progress flow"""
    await delete_flow(flow_id)


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
