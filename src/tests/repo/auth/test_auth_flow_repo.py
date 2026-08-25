import uuid
from datetime import UTC, datetime

import pytest

from app import repo
from app.core.authn.session import format_session_token, parse_session_token
from app.exceptions import ObjectNotFound
from app.repo.auth.session import hash_session_secret
from app.types.auth.assertions import Assertion, EmailAuth, PasskeyAuth
from app.types.auth.auth_flow import AuthFlow, FlowState
from app.types.auth.passkey_data import PasskeyID
from app.types.auth.session import SessionID
from app.types.user import UserID

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
    pytest.mark.asyncio,
]


async def test_create_and_update_flow(subtests):

    flow_state = FlowState({})

    with subtests.test("Create flow"):
        flow_id = await repo.auth.flow.create(kind="example", state=flow_state)

    with subtests.test("Update flow state"):
        async with repo.auth.flow.for_update(flow_id) as upd:
            await upd.update(state=FlowState({"state": 1}))

        flow = await repo.auth.flow.get(flow_id)
        assert flow.state == {"state": 1}

    with subtests.test("Update flow state again"):
        async with repo.auth.flow.for_update(flow_id) as upd:
            await upd.update(state=FlowState({"state": 2}))

        flow = await repo.auth.flow.get(flow_id)
        assert flow.state == {"state": 2}

    with subtests.test("Logically delete flow"):
        async with repo.auth.flow.for_update(flow_id) as upd:
            await upd.update(is_completed=True)

        with pytest.raises(ObjectNotFound):
            await repo.auth.flow.get(flow_id)


async def test_flow_with_associated_session_id(subtests):

    flow_state = FlowState({})
    session_id = SessionID("bb10f8f5-8c77-4305-b829-b3a0fed8acf7")

    with subtests.test("Create flow"):
        flow_id = await repo.auth.flow.create(kind="example", state=flow_state, session_id=session_id)

    with subtests.test("Retrieve flow with correct session ID"):
        flow = await repo.auth.flow.get(flow_id, session_id=session_id)
        assert flow.flow_id == flow_id

    with subtests.test("Retrieve flow with correct session ID"):  # noqa: SIM117
        flow = await repo.auth.flow.get(flow_id)

    with subtests.test("Retrieving flow with mismatched session ID fails"):  # noqa: SIM117
        with pytest.raises(ObjectNotFound):
            await repo.auth.flow.get(flow_id, session_id=SessionID("993c2a5f-9b6c-4cbf-b2f7-cf071aa42742"))
