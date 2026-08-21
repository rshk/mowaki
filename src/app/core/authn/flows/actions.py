from datetime import timedelta

from app import repo
from app.core.context import get_current_session
from app.types.auth.auth_flow import FlowAction, FlowID

from .base import FlowStatus
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


async def process_flow_action(flow_id: FlowID, action: FlowAction) -> FlowStatus:
    async with repo.auth.flow.for_update(flow_id) as upd:
        flow = upd.obj
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
    await repo.auth.flow.delete(flow_id)


async def cleanup_completed_flows():
    await repo.auth.flow.delete_completed()
