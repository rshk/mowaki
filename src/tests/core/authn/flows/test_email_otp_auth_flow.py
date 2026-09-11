import pytest

from app.core.authn.flows.base import FlowActionResultStatus
from app.core.authn.flows.email_otp_auth import EmailOTPAuthFlowProcessor
from app.core.authn.session import create_session, get_session
from app.types.auth.assertions import EmailAuth
from app.types.auth.auth_flow import FlowAction
from tests.utils.session import set_request_context_from_session_id

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("database_schema"),
]

async def test_flow_happy_path(resources):
    session, _ = await create_session()
    session_id = session.session_id

    async with set_request_context_from_session_id(session_id):

        processor = EmailOTPAuthFlowProcessor.new()

        assert processor.get_challenge_data() == {"state": "EMAIL_REQUIRED"}
        assert processor.dump_state() == {"email": None, "code": None}

        result = await processor.process(FlowAction({"email": "user@example.com"}))
        assert result == FlowActionResultStatus.IN_PROGRESS
        assert processor.get_challenge_data() == {"state": "CODE_REQUIRED"}
        _state = processor.dump_state()
        assert set(_state.keys()) == {"email", "code"}
        assert _state["email"] == "user@example.com"
        assert _state["code"] is not None

        code = _state["code"]

        result = await processor.process(FlowAction({"code": code}))
        assert result == FlowActionResultStatus.SUCCESS

        # Check that a new assertion has been added to the session
        session = await get_session(session_id)
        assert len(session.assertions) == 1
        assert isinstance(session.assertions[0].params, EmailAuth)
        assert session.assertions[0].params.email_address == "user@example.com"
        assert session.assertions[0].params.user_id is None
        assert session.current_user_id is None

async def test_flow_happy_path_with_state_freezing(resources):
    # Same happy-path test, but dumping/restoring state at each step

    session, _ = await create_session()
    session_id = session.session_id

    async with set_request_context_from_session_id(session_id):

        processor = EmailOTPAuthFlowProcessor.new()

        assert processor.get_challenge_data() == {"state": "EMAIL_REQUIRED"}
        assert processor.dump_state() == {"email": None, "code": None}

        # Recreate processor from state
        processor = EmailOTPAuthFlowProcessor.from_state(processor.dump_state())

        result = await processor.process(FlowAction({"email": "user@example.com"}))
        assert result == FlowActionResultStatus.IN_PROGRESS
        assert processor.get_challenge_data() == {"state": "CODE_REQUIRED"}
        _state = processor.dump_state()
        assert set(_state.keys()) == {"email", "code"}
        assert _state["email"] == "user@example.com"
        assert _state["code"] is not None

        code = _state["code"]

        # Recreate processor from state
        processor = EmailOTPAuthFlowProcessor.from_state(processor.dump_state())

        result = await processor.process(FlowAction({"code": code}))
        assert result == FlowActionResultStatus.SUCCESS

        # Check that a new assertion has been added to the session
        session = await get_session(session_id)
        assert len(session.assertions) == 1
        assert isinstance(session.assertions[0].params, EmailAuth)
        assert session.assertions[0].params.email_address == "user@example.com"
        assert session.assertions[0].params.user_id is None
        assert session.current_user_id is None
