import pytest

from app import repo
from app.core.authn.flows.login.factory import LoginFlowFactory
from app.core.authn.flows.login.states import (
    InitialState,
    OtpPendingState,
)
from app.core.context import get_current_session
from app.lib.flows.base import SuccessStateBlock
from app.lib.flows.types import FlowAction
from app.types.auth import assertions
from app.types.auth.assertions import Assertion

pytestmark = [
    pytest.mark.usefixtures("database_schema", "request_ctx"),
    pytest.mark.asyncio,
]


async def test_email_otp_for_existing_user():
    """
    Email OTP authentication for an *existing* user
    """

    EMAIL = "user@example.com"

    user_id = await repo.user.create(email=EMAIL)

    factory = LoginFlowFactory()

    # Create new login flow
    state0 = await factory.create()
    assert isinstance(state0, InitialState)

    # Start email-based OTP validation
    action = FlowAction({"kind": "start-email-otp", "email": EMAIL})
    state1 = await state0.execute(action)
    initial_session_id = get_current_session().session_id
    assert isinstance(state1, OtpPendingState)
    assert state1.email == EMAIL

    # Correctly respond to OTP validation
    action = FlowAction({"kind": "otp-response", "otp": state1.otp})
    state2 = await state1.execute(action)
    assert get_current_session().session_id != initial_session_id
    assert isinstance(state2, SuccessStateBlock)  # user exists -> logged in

    # Verify that the correct assertions have been added to the session
    session = get_current_session()
    assert session.current_user_id == user_id
    assert len(session.assertions) == 1
    [email_assertion] = session.assertions
    assert isinstance(email_assertion, Assertion)
    assert isinstance(email_assertion.params, assertions.EmailAuth)
    assert email_assertion.params.email_address == EMAIL
