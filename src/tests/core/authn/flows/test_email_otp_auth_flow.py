import pytest

from app.core.authn.flows.email_otp_auth import (
    PROCESSOR as EMAIL_OTP_AUTH_FLOW_PROCESSOR,
)
from app.core.authn.flows.processor import FlowActionResult
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
        processor = EMAIL_OTP_AUTH_FLOW_PROCESSOR

        state = await processor.create()
        assert state == {"email": None, "code": None}

        challenge = processor.get_challenge(state)
        assert challenge == {"next_step": "EMAIL_REQUIRED"}

        result = await processor.process(
            state, FlowAction({"email": "user@example.com"})
        )

        assert isinstance(result, FlowActionResult)
        assert not result.is_completed()
        assert result.state is not None
        assert result.state["email"] == "user@example.com"
        assert result.state["code"] is not None

        # Obtain code to use later
        code = result.state["code"]

        result = await processor.process(result.state, FlowAction({"code": code}))
        assert isinstance(result, FlowActionResult)
        assert result.is_success()

        # Check that a new assertion has been added to the session
        session = await get_session(session_id)
        assert len(session.assertions) == 1
        assert isinstance(session.assertions[0].params, EmailAuth)
        assert session.assertions[0].params.email_address == "user@example.com"
        assert session.assertions[0].params.user_id is None
        assert session.current_user_id is None
