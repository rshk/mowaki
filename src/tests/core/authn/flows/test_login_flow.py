import pytest
from app import repo
from app.core.authn.flows.login.factory import LoginFlowFactory
from app.core.authn.flows.login.flow import (
    InitialState,
    OtpPendingState,
    OtpResponseAction,
    SignupState,
)
from app.core.authn.session import create_session
from app.exceptions import ObjectNotFound
from app.lib.flows.base import SuccessStateBlock
from app.lib.flows.types import FlowAction
from app.types.auth.auth_flow import FlowState
from app.types.auth.session import SessionID
from tests.utils.session import set_request_context_from_session_id

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
    pytest.mark.asyncio,
]


async def test_happy_path_through_standalone_login_flow():
    """
    Test that the "happy path" through the login flow works as
    intended, without storing the flow in the database.
    """

    factory = LoginFlowFactory()
    session, _ = await create_session()
    session_id = session.session_id

    # Create new login flow
    state0 = await factory.create()
    assert isinstance(state0, InitialState)

    # Start email-based OTP validation
    action = FlowAction({"kind": "start-email-otp", "email": "user@example.com"})
    async with set_request_context_from_session_id(session_id):
        state1 = await state0.execute(action)
    assert isinstance(state1, OtpPendingState)
    assert state1.email == "user@example.com"
    assert isinstance(state1.otp, str)
    assert state1.retries_left == 3

    # Correctly respond to OTP validation
    action = FlowAction({"kind": "otp-response", "otp": state1.otp})
    async with set_request_context_from_session_id(session_id):
        state2 = await state1.execute(action)
    assert isinstance(state2, SignupState)  # user does not exist yet
    assert state2.email == "user@example.com"

    # Confirm account creation
    action = FlowAction({"kind": "signup-confirm", "display_name": "Test User"})
    async with set_request_context_from_session_id(session_id):
        state3 = await state2.execute(action)
    assert isinstance(state3, SuccessStateBlock)

    # TODO: verify that the user was indeed created

    pass
