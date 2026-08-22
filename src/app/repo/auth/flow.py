import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from app.lib.sql.table_helper import TableHelper, UpdateHelper
from app.repo._schema.auth_flow import FlowTable
from app.resources import get_database
from app.types.auth.auth_flow import AuthFlow, FlowID, FlowState
from app.types.auth.session import SessionID

_crud = TableHelper[AuthFlow](
    FlowTable,
    model=AuthFlow,
    get_engine=get_database,
)


async def create(
    kind: str,
    state: FlowState,
    expires_in: timedelta | None = None,
    session_id: SessionID | None = None,
) -> FlowID:

    flow_id = FlowID(uuid.uuid4())
    created_at = datetime.now(UTC)
    expires_at = None if expires_in is None else created_at + expires_in

    await _crud.insert(
        flow_id=flow_id,
        created_at=created_at,
        kind=kind,
        state=state,
        expires_at=expires_at,
        session_id=session_id,
        is_completed=False,
    )

    return flow_id


@asynccontextmanager
async def for_update(
    flow_id: FlowID, session_id: SessionID | None = None
) -> AsyncGenerator[UpdateHelper[AuthFlow]]:
    # ----------------------------------------------------------------
    # Use ``is_completed`` as logic deletion, since we cannot
    # immediately delete an object that's currently locked with
    # ``SELECT .. FOR UPDATE``.
    # ----------------------------------------------------------------

    query = (
        FlowTable.select()
        .filter_by(flow_id=flow_id, is_completed=False)
        .with_for_update()
    )

    if session_id is not None:
        query = query.filter_by(session_id=session_id)

    db = get_database()
    async with db.connect() as conn, conn.begin():
        result = await conn.execute(query)

        async def update_object(**updates):
            query = FlowTable.update().filter_by(flow_id=flow_id).values(**updates)
            await conn.execute(query)

        row = result.one()
        obj = AuthFlow.from_dict(row._asdict())
        yield UpdateHelper(obj=obj, update=update_object)


async def delete(flow_id: FlowID):
    await _crud.delete(flow_id)


async def delete_completed():
    """Delete completed flows"""
    db = get_database()
    query = FlowTable.delete().filter_by(is_completed=True)
    async with db.connect() as conn, conn.begin():
        await conn.execute(query)
