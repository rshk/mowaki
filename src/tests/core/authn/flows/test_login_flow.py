from typing import cast

import pytest

from app import repo
from app.core.authn.flows.login.factory import LoginFlowFactory
from app.core.authn.flows.login.states import (
    InitialState,
    OtpPendingState,
    SignupState,
)
from app.core.context import get_current_session
from app.lib.flows.base import SuccessStateBlock
from app.lib.flows.types import FlowAction
from app.types.auth import assertions
from app.types.auth.assertions import Assertion
from app.types.user import User

pytestmark = [
    pytest.mark.usefixtures("database_schema", "request_ctx"),
    pytest.mark.asyncio,
]


async def test_email_otp_for_new_user():
    """
    Test that the "happy path" through the login flow works as
    intended, without storing the flow in the database.
    """

    EMAIL = "user@example.com"

    factory = LoginFlowFactory()

    # Create new login flow
    state0 = await factory.create()
    assert isinstance(state0, InitialState)

    challenge0 = state0.get_challenge()
    assert set(challenge0.keys()) == {"kind", "actions"}
    assert challenge0["kind"] == "login-init"
    actions0 = challenge0["actions"]
    assert isinstance(actions0, list)
    actions0_kinds = {x["properties"]["kind"]["const"] for x in cast(list, actions0)}
    assert "start-email-otp" in actions0_kinds
    assert "start-webauthn" in actions0_kinds

    # Start email-based OTP validation
    action = FlowAction({"kind": "start-email-otp", "email": EMAIL})
    state1 = await state0.execute(action)
    initial_session_id = get_current_session().session_id
    assert isinstance(state1, OtpPendingState)
    assert state1.email == EMAIL
    assert isinstance(state1.otp, str)
    assert state1.retries_left == 3

    challenge1 = state1.get_challenge()
    assert set(challenge1.keys()) == {"kind", "actions"}
    assert challenge1["kind"] == "otp-verify"
    actions1 = challenge1["actions"]
    assert isinstance(actions1, list)
    actions1_kinds = {x["properties"]["kind"]["const"] for x in cast(list, actions1)}
    assert "otp-response" in actions1_kinds

    # Correctly respond to OTP validation
    action = FlowAction({"kind": "otp-response", "otp": state1.otp})
    state2 = await state1.execute(action)
    assert (
        get_current_session().session_id != initial_session_id
    )  # A new session was created!
    assert isinstance(state2, SignupState)  # user does not exist yet
    assert state2.email == EMAIL

    challenge2 = state2.get_challenge()
    assert set(challenge2.keys()) == {"kind", "actions"}
    assert challenge2["kind"] == "signup"
    actions2 = challenge2["actions"]
    assert isinstance(actions2, list)
    actions2_kinds = {x["properties"]["kind"]["const"] for x in cast(list, actions2)}
    assert "signup-confirm" in actions2_kinds
    assert "signup-reject" in actions2_kinds

    # Confirm account creation
    action = FlowAction({"kind": "signup-confirm", "display_name": "Test User"})
    state3 = await state2.execute(action)
    assert isinstance(state3, SuccessStateBlock)

    # Verify that the user was indeed created
    user = await repo.user.get_by_email(EMAIL)
    assert isinstance(user, User)

    # Verify that the correct assertions have been added to the session
    session = get_current_session()
    assert session.current_user_id == user.id
    assert len(session.assertions) == 1
    [email_assertion] = session.assertions
    assert isinstance(email_assertion, Assertion)
    assert isinstance(email_assertion.params, assertions.EmailAuth)
    assert email_assertion.params.email_address == EMAIL
