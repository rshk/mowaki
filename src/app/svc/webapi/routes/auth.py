from datetime import datetime
from typing import Annotated, Iterable

from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.config import get_config
from app.core.authn.flows.docs import docs as flow_docs
from app.core.authn.flows.manager import get_flow_expiration_date
from app.core.context import get_current_session
from app.lib.flows.constants import FlowStatus
from app.lib.flows.docs import FlowObjectDocsRegistry
from app.lib.flows.flow import FlowStateBlock
from app.lib.flows.registry import FlowRegistry
from app.lib.flows.types import FlowAction, FlowChallenge, FlowKind, FlowParams
from app.lib.types import JSONObject
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


@router.post("/flow/init/{flow_kind}", summary="Start an authentication flow")
async def init_flow(
    flow_kind: FlowKind,
    params: Annotated[FlowParams, Body(default_factory=dict)],
) -> PublicFlowInfo:
    """Initiate an authentication flow of the specified kind.

    See the [flows documentation](/auth/docs.json) for more information on available flows.
    """

    flow_id = await flow_mgr.create(flow_kind, params=params)
    flow_info = await flow_mgr.get_info(flow_id)
    return await _build_public_flow_info(flow_info)


@router.get("/flow/{flow_id}", summary="Get info and next steps")
async def get_flow(flow_id: FlowID):
    flow_info = await flow_mgr.get_info(flow_id)
    return await _build_public_flow_info(flow_info)


@router.post("/flow/{flow_id}", summary="Execute an action")
async def post_flow_action(
    flow_id: FlowID,
    action: Annotated[FlowAction, Body(default_factory=dict)],
) -> PublicFlowInfo:

    await flow_mgr.execute(flow_id, action)

    flow_info = await flow_mgr.get_info(flow_id)
    return await _build_public_flow_info(flow_info)


@router.delete("/flow/{flow_id}", summary="Abort an in-progress flow")
async def cancel_flow(flow_id: FlowID):
    """Cancel / abort an in-progress flow"""
    await flow_mgr.delete(flow_id)


@router.get("/session", summary="Get current session information")
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


@router.get("/docs.json", summary="JSON documentation of available flows")
async def get_flows_docs_json():
    return list(_generate_all_flow_docs(flow_registry, flow_docs))


def _generate_all_flow_docs(
    registry: FlowRegistry, docs: FlowObjectDocsRegistry
) -> Iterable[JSONObject]:
    for kind in registry:
        yield {"kind": kind, **docs.generate_flow_docs(kind)}


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
