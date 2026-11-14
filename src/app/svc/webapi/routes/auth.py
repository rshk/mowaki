from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.config import get_config
from app.core.authn.flows.repo import get_flow_expiration_date
from app.core.context import get_current_session
from app.lib.flows.constants import FlowStatus
from app.lib.flows.flow import FlowStateBlock
from app.lib.flows.types import FlowAction, FlowChallenge, FlowKind, FlowParams
from app.types.auth.auth_flow import AuthFlow, FlowID

from ..authn import flow_registry, flow_repo

router = APIRouter(tags=["authentication"])


class PublicFlowInfo(BaseModel):
    flow_id: FlowID
    created_at: datetime
    expires_at: datetime
    kind: FlowKind
    challenge: FlowChallenge
    status: Literal["in-progress", "expired", "completed", "canceled"]


@router.post("/flow/init/{flow_kind}")
async def init_flow(
    flow_kind: FlowKind,
    params: Annotated[FlowParams, Body(default_factory=dict)],
) -> PublicFlowInfo:
    """Initiate an authentication flow of the specified type"""

    flow_id = await flow_repo.create(flow_kind, params=params)
    flow_info = await flow_repo.get(flow_id)
    return await _build_public_flow_info(flow_info)


@router.get("/flow/{flow_id}")
async def get_flow(flow_id: FlowID):
    flow_info = await flow_repo.get(flow_id)
    return await _build_public_flow_info(flow_info)


class FlowActionResult(BaseModel):
    flow: PublicFlowInfo | None
    status: FlowStatus


@router.post("/flow/{flow_id}")
async def post_flow_action(
    flow_id: FlowID,
    action: Annotated[FlowAction, Body(default_factory=dict)],
) -> FlowActionResult:

    async with flow_repo.for_processing(flow_id) as flow:
        await flow.state.execute(action)
        status = flow.state.get_status()

    if status.is_ended():
        return FlowActionResult(flow=None, status=status)

    # TODO: avoid this call
    flow_info = await flow_repo.get(flow_id)
    public_flow_info = await _build_public_flow_info(flow_info)

    return FlowActionResult(flow=public_flow_info, status=status)


@router.delete("/flow/{flow_id}")
async def cancel_flow(flow_id: FlowID):
    """Cancel / abort an in-progress flow"""
    await flow_repo.delete(flow_id)


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


async def _build_public_flow_info(flow: AuthFlow) -> PublicFlowInfo:
    """
    Create a PublicFlowInfo instance from an AuthFlow (database) record
    """
    processor: FlowStateBlock = await flow_registry[flow.kind].load(flow.state)
    return PublicFlowInfo(
        flow_id=flow.flow_id,
        created_at=flow.created_at,
        expires_at=get_flow_expiration_date(flow),
        kind=flow.kind,
        challenge=processor.get_challenge(),
        status="in-progress",
    )
