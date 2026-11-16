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
from app.core.context import get_current_session
from app.exceptions import ObjectNotFound
from app.lib.flows.base import SuccessStateBlock
from app.lib.flows.types import FlowAction
from app.types.auth import assertions
from app.types.auth.assertions import Assertion
from app.types.auth.auth_flow import FlowState
from app.types.auth.session import SessionID
from app.types.user import User
from tests.utils.session import TestingRequestSession, set_request_context_from_session_id

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
    pytest.mark.asyncio,
]


async def test_happy_path_through_standalone_login_flow():
    """
    Test that the "happy path" through the login flow works as
    intended, without storing the flow in the database.
    """

    request_ctx_mgr = TestingRequestSession()

    factory = LoginFlowFactory()

    # Create new login flow
    state0 = await factory.create()
    assert isinstance(state0, InitialState)

    # Start email-based OTP validation
    action = FlowAction({"kind": "start-email-otp", "email": "user@example.com"})
    async with request_ctx_mgr:
        state1 = await state0.execute(action)
    assert isinstance(state1, OtpPendingState)
    assert state1.email == "user@example.com"
    assert isinstance(state1.otp, str)
    assert state1.retries_left == 3

    # Correctly respond to OTP validation
    action = FlowAction({"kind": "otp-response", "otp": state1.otp})
    async with request_ctx_mgr:
        state2 = await state1.execute(action)
    assert isinstance(state2, SignupState)  # user does not exist yet
    assert state2.email == "user@example.com"

    # Confirm account creation
    action = FlowAction({"kind": "signup-confirm", "display_name": "Test User"})
    async with request_ctx_mgr:
        state3 = await state2.execute(action)
    assert isinstance(state3, SuccessStateBlock)

    # Verify that the user was indeed created
    user = await repo.user.get_by_email("user@example.com")
    assert isinstance(user, User)

    # Verify that the correct assertions have been added to the session
    async with request_ctx_mgr:
        session = get_current_session()
    assert session.current_user_id == user.id
    assert len(session.assertions) == 1
    [email_assertion] = session.assertions
    assert isinstance(email_assertion, Assertion)
    assert isinstance(email_assertion.params, assertions.EmailAuth)
    assert email_assertion.params.email_address == "user@example.com"
