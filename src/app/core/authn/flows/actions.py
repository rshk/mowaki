from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from app import repo
from app.const import AUTH_FLOW_HARD_VALIDITY
from app.core.authn.exceptions import (
    FlowAccessDenied,
    FlowAlreadyCompleted,
    FlowExpired,
)
from app.core.context import get_current_session
from app.lib.sql.table_helper import UpdateHelper
from app.types.auth.auth_flow import AuthFlow, FlowAction, FlowID

from .base import BaseFlowProcessor, FlowStatus
from .registry import get_flow_processor_class


async def create_flow(kind: str, expires_in: timedelta | None = None) -> FlowID:
    session = get_current_session()

    flow_class = get_flow_processor_class(kind)
    flow = flow_class.new()
    flow_state = flow.dump_state()

    flow_id = await repo.auth.flow.create(
        kind=kind,
        state=flow_state,
        expires_in=expires_in,
        session_id=session.session_id,
    )

    return flow_id


async def get_flow(flow_id: FlowID) -> AuthFlow:
    flow = await repo.auth.flow.get(flow_id)
    _ensure_flow_is_processable(flow)
    return flow


@asynccontextmanager
async def get_flow_for_update(
    flow_id: FlowID,
) -> AsyncGenerator[UpdateHelper[AuthFlow]]:
    session = get_current_session()
    async with repo.auth.flow.for_update(flow_id, session_id=session.session_id) as upd:
        flow = await upd.get()
        _ensure_flow_is_processable(flow)
        yield upd


def _ensure_flow_is_processable(flow: AuthFlow):

    # If the flow is tied to a session, make sure it matches the
    # current session.
    if flow.session_id is not None:
        session = get_current_session()
        if flow.session_id != session.session_id:
            raise FlowAccessDenied("This flow belongs to a different session")

    # If the flow is completed, reject the request.
    # This has a slim chance of happening due to a race condition
    # between flow completion and deletion from the database.
    if flow.is_completed:
        raise FlowAlreadyCompleted("This flow has already been completed")

    # If the flow has expired, it cannot be processed further.
    # We might want to give the user a convenient option to restart it!
    if is_flow_expired(flow):
        raise FlowExpired("This flow has expired")


async def process_flow_action(flow_id: FlowID, action: FlowAction) -> FlowStatus:
    async with get_flow_for_update(flow_id) as upd:
        flow = await upd.get()
        flow_class = get_flow_processor_class(flow.kind)
        flow = flow_class.from_state(flow.state)

        result = await flow.process(action)

        is_completed = result in (FlowStatus.SUCCESS, FlowStatus.FAILED)
        new_state = flow.dump_state()

        if is_completed:
            # Logical deletion, to prevent race conditions between the
            # end of this transaction and actually deleting the flow.
            await upd.update(is_completed=True)
        else:
            # Update stored flow state
            await upd.update(state=new_state)

    if is_completed:
        await repo.auth.flow.delete(flow_id)

    return result


async def delete_flow(flow_id: FlowID):
    # get_flow_for_update() also does appropriate authorization checks
    async with get_flow_for_update(flow_id) as upd:
        await upd.update(is_completed=True)  # Logical deletion
    await repo.auth.flow.delete(flow_id)


async def cleanup_completed_flows():
    await repo.auth.flow.delete_completed()


async def cleanup_expired_flows():
    await repo.auth.flow.delete_expired(max_validity=AUTH_FLOW_HARD_VALIDITY)


def get_flow_expiration_date(flow: AuthFlow) -> datetime:
    expiration_date = flow.created_at + AUTH_FLOW_HARD_VALIDITY
    if flow.expires_at and flow.expires_at < expiration_date:
        expiration_date = flow.expires_at
    return expiration_date


def is_flow_expired(flow: AuthFlow) -> bool:
    return get_flow_expiration_date(flow) <= datetime.now(UTC)


def get_flow_processor(flow: AuthFlow) -> BaseFlowProcessor:
    return get_flow_processor_class(flow.kind).from_state(flow.state)
