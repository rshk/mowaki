import uuid
from datetime import UTC, datetime, timedelta

from app.lib.sql.table_helper import TableHelper
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
    state: FlowState,
    session_id: SessionID | None = None,
    validity: timedelta | None = None,
) -> FlowID:

    flow_id = uuid.uuid4()
    created_at = datetime.now(UTC)
    expires_at = None if validity is None else created_at + validity

    await _crud.insert(
        flow_id=flow_id,
        created_at=created_at,
        expires_at=expires_at,
        session_id=session_id,
        state=state,
        is_completed=False,
    )
    return FlowID(flow_id)


# async def create_flow(params: FlowStateParams) -> FlowID:
#     flow_id = FlowID(uuid.uuid4())
#     created_at = datetime.now(UTC)
#     await _crud.insert(
#         flow_id=flow_id,
#         created_at=created_at,
#         expires_at=None,
#         params=params,
#     )
#     return flow_id


# @asynccontextmanager
# async def lock_flow_for_processing(
#     flow_id: FlowID,
# ) -> AsyncGenerator[FlowState]:
#     """Lock a flow for processing, delete it at the end"""

#     db = get_database()

#     query = (
#         FlowTable.select()
#         .filter_by(flow_id=flow_id, processed=False)
#         .with_for_update()
#     )

#     async with db.connect() as conn, conn.begin():
#         result = await conn.execute(query)
#         row = result.one()._asdict()
#         flow = FlowState.from_dict(row)

#         await conn.execute(
#             FlowTable.update()
#             .filter_by(flow_id=flow_id)
#             .values(processed=True)
#         )

#     try:
#         yield flow
#     finally:
#         # Flows are one-time only!
#         await _crud.delete(flow_id)
