import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from app.types.auth.challenges import Challenge, ChallengeID
from app.types.auth.flow import AuthFlow, AuthFlowID
from app.types.session import SessionID

from .._helpers.common import TableCrud, UpdaterFn
from .._schema.auth_flow import AuthFlowTable

_crud = TableCrud[AuthFlow](AuthFlowTable, model=AuthFlow)


def generate_flow_id() -> AuthFlowID:
    return AuthFlowID(uuid.uuid4())


def generate_challenge_id() -> ChallengeID:
    return ChallengeID(uuid.uuid4())


async def get(flow_id: AuthFlowID) -> AuthFlow:
    return await _crud.get_by_pk(flow_id)


async def create(
    kind: str,
    session_id: str | None = None,
    challenges: list[Challenge] | None = None,
) -> AuthFlowID:
    flow_id = generate_flow_id()
    await _crud.insert(
        flow_id=flow_id,
        kind=kind,
        session_id=session_id,
        created_at=datetime.now(timezone.utc),
        challenges=challenges or [],
    )
    return flow_id


@asynccontextmanager
async def for_update(flow_id: AuthFlowID) -> AsyncIterator[tuple[AuthFlow, UpdaterFn]]:
    async with _crud.for_update(flow_id) as (flow, updater):
        yield flow, updater


async def delete(flow_id: AuthFlowID):
    await _crud.delete(flow_id)


async def invalidate_session_flows(
    session_id: SessionID,
    kinds: list[str] | None = None,
):
    """Delete all flows tied to a given session"""
    pass


async def cleanup_expired():
    """Delete all expired flows"""
    pass


async def cleanup_completed():
    """Delete all flows marked as completed"""
    pass
