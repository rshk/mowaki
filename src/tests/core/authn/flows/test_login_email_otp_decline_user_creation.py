import pytest

from app import repo
from app.core.authn.flows.login.factory import LoginFlowFactory
from app.core.authn.flows.login.states import (
    InitialState,
    OtpPendingState,
    SignupState,
)
from app.core.context import get_current_session
from app.exceptions import ObjectNotFound
from app.lib.flows.base import SuccessStateBlock
from app.lib.flows.types import FlowAction
from app.types.auth import assertions

pytestmark = [
    pytest.mark.usefixtures("database_schema", "request_ctx"),
    pytest.mark.asyncio,
]


async def test_decline_user_creation():
    """
    Signing up via email OTP with an address not tied to an existing
    user; client decides *not* to sign up.
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

    # Validate OTP
    action = FlowAction({"kind": "otp-response", "otp": state1.otp})
    state2 = await state1.execute(action)
    assert isinstance(state2, SignupState)
    assert state2.email == EMAIL

    # Session ID changed after OTP validation
    assert get_current_session().session_id != initial_session_id

    # Decline signup
    action = FlowAction({"kind": "signup-reject"})
    state3 = await state2.execute(action)
    assert isinstance(state3, SuccessStateBlock)

    # Session still contains assertion
    session = get_current_session()
    assert len(session.assertions) == 1
    assert isinstance(session.assertions[0].params, assertions.EmailAuth)
    assert session.assertions[0].params.email_address == EMAIL

    # User has *not* been created
    with pytest.raises(ObjectNotFound):
        await repo.user.get_by_email(EMAIL)
