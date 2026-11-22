import pytest

from app.core.authn.flows.login.factory import LoginFlowFactory
from app.core.authn.flows.login.states import (
    InitialState,
    OtpPendingState,
)
from app.core.context import get_current_session
from app.lib.flows.base import FailureStateBlock
from app.lib.flows.types import FlowAction

pytestmark = [
    pytest.mark.usefixtures("database_schema", "request_ctx"),
    pytest.mark.asyncio,
]


async def test_exceed_otp_attempts():
    """
    Test that exceeding the OTP validation attempts invalidates the flow.
    """

    EMAIL = "user@example.com"

    factory = LoginFlowFactory()

    # Create new login flow
    state0 = await factory.create()
    assert isinstance(state0, InitialState)

    # Start email-based OTP validation
    action = FlowAction({"kind": "start-email-otp", "email": EMAIL})
    state1 = await state0.execute(action)
    initial_session_id = get_current_session().session_id
    assert isinstance(state1, OtpPendingState)
    assert state1.retries_left == 3

    # Incorrectly respond to OTP validation
    action = FlowAction({"kind": "otp-response", "otp": "invalid-1"})
    state2 = await state1.execute(action)
    assert isinstance(state2, OtpPendingState)
    assert state2.retries_left == 2

    action = FlowAction({"kind": "otp-response", "otp": "invalid-2"})
    state3 = await state2.execute(action)
    assert isinstance(state3, OtpPendingState)
    assert state3.retries_left == 1

    action = FlowAction({"kind": "otp-response", "otp": "invalid-3"})
    state4 = await state3.execute(action)
    assert isinstance(state4, FailureStateBlock)

    # Session ID is left unchanged
    assert get_current_session().session_id == initial_session_id
