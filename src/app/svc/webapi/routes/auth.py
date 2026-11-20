from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.config import get_config
from app.core.authn.flows.manager import get_flow_expiration_date
from app.core.context import get_current_session
from app.lib.flows.constants import FlowStatus
from app.lib.flows.flow import FlowStateBlock
from app.lib.flows.types import FlowAction, FlowChallenge, FlowKind, FlowParams
from app.types.auth.auth_flow import AuthFlow, FlowID

from ..authn import flow_mgr, flow_registry

router = APIRouter(tags=["authentication"])


class PublicFlowInfo(BaseModel):
    flow_id: FlowID
    created_at: datetime
    expires_at: datetime
    kind: FlowKind
    challenge: FlowChallenge
    status: FlowStatus


@router.post("/flow/init/{flow_kind}")
async def init_flow(
    flow_kind: FlowKind,
    params: Annotated[FlowParams, Body(default_factory=dict)],
) -> PublicFlowInfo:
    """Initiate an authentication flow of the specified type"""

    flow_id = await flow_mgr.create(flow_kind, params=params)
    flow_info = await flow_mgr.get_info(flow_id)
    return await _build_public_flow_info(flow_info)


@router.get("/flow/{flow_id}")
async def get_flow(flow_id: FlowID):
    flow_info = await flow_mgr.get_info(flow_id)
    return await _build_public_flow_info(flow_info)


@router.post("/flow/{flow_id}")
async def post_flow_action(
    flow_id: FlowID,
    action: Annotated[FlowAction, Body(default_factory=dict)],
) -> PublicFlowInfo:

    await flow_mgr.execute(flow_id, action)

    flow_info = await flow_mgr.get_info(flow_id)
    return await _build_public_flow_info(flow_info)


@router.delete("/flow/{flow_id}")
async def cancel_flow(flow_id: FlowID):
    """Cancel / abort an in-progress flow"""
    await flow_mgr.delete(flow_id)


@router.get("/session")
async def get_session_info():
    """Get information about the current session"""

    session = get_current_session()

    config = get_config()

    # During development, return more information about the session.
    if config.development_mode:
        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "last_used_at": session.last_used_at,
            "metadata": session.metadata,
            "assertions": session.assertions,
        }

    return {"session_id": session.session_id}


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
        status=processor.get_status(),
    )
