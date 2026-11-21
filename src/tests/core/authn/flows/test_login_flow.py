import pytest
from app import repo
from app.core.authn.flows.login.factory import LoginFlowFactory
from app.core.authn.flows.login.flow import (
    InitialState,
    OtpPendingState,
    SignupState,
)
from app.core.authn.flows.manager import FlowManager
from app.core.context import RequestContext, get_current_session
from app.exceptions import ObjectNotFound
from app.lib.flows.base import SuccessStateBlock
from app.lib.flows.registry import FlowRegistry
from app.lib.flows.types import FlowAction, FlowKind
from app.types.auth import assertions
from app.types.auth.assertions import Assertion
from app.types.auth.auth_flow import FlowID
from app.types.user import User

from tests.utils.session import (
    TestingRequestContextManager,
)

pytestmark = [
    pytest.mark.usefixtures("database_schema", "request_ctx"),
    pytest.mark.asyncio,
]


async def test_happy_path_through_standalone_login_flow():
    """
    Test that the "happy path" through the login flow works as
    intended, without storing the flow in the database.
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
    assert state1.email == EMAIL
    assert isinstance(state1.otp, str)
    assert state1.retries_left == 3

    # Correctly respond to OTP validation
    action = FlowAction({"kind": "otp-response", "otp": state1.otp})
    state2 = await state1.execute(action)
    assert (
        get_current_session().session_id != initial_session_id
    )  # A new session was created!
    assert isinstance(state2, SignupState)  # user does not exist yet
    assert state2.email == EMAIL

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


async def test_happy_path_through_stored_login_flow():
    """
    Test that the "happy path" through the login flow works as
    intended, using a flow stored in the database.
    """

    EMAIL = "user@example.com"

    # Use custom flow registry and repo to ensure we have the exact
    # configuration we want for testing, irrespective of what's
    # actually configured in the webapi settings.
    flow_registry = FlowRegistry()
    flow_registry[FlowKind("login")] = LoginFlowFactory()
    flow_mgr = FlowManager(registry=flow_registry)

    # ----------------------------------------------------------------
    # Create login flow
    # ----------------------------------------------------------------

    flow_id: FlowID = await flow_mgr.create(FlowKind("login"))

    # Get and check stored flow state
    flow_info = await flow_mgr.get_info(flow_id)
    assert flow_info.flow_id == flow_id
    assert flow_info.created_at is not None
    assert flow_info.expires_at is None
    assert flow_info.session_id is None
    assert flow_info.kind == "login"
    assert flow_info.state == {"kind": "initial"}
    assert flow_info.is_ended is False

    # Store initial session ID to check it's changed later
    initial_session_id = get_current_session().session_id

    # ----------------------------------------------------------------
    # Start email-based OTP validation
    # ----------------------------------------------------------------

    action = FlowAction({"kind": "start-email-otp", "email": EMAIL})
    await flow_mgr.execute(flow_id, action)

    # Get and check stored flow state
    flow_info = await flow_mgr.get_info(flow_id)
    assert flow_info.flow_id == flow_id
    assert flow_info.created_at is not None
    assert flow_info.expires_at is None
    assert flow_info.session_id is None
    assert flow_info.kind == "login"
    assert set(flow_info.state.keys()) == {"kind", "email", "otp", "retries_left"}
    assert flow_info.state["kind"] == "email-otp-pending"
    assert flow_info.state["email"] == EMAIL
    assert flow_info.state["otp"] is not None
    assert flow_info.state["retries_left"] == 3
    assert flow_info.is_ended is False

    otp = flow_info.state["otp"]  # we need it later

    # ----------------------------------------------------------------
    # Correctly respond to OTP validation
    # ----------------------------------------------------------------

    action = FlowAction({"kind": "otp-response", "otp": otp})
    await flow_mgr.execute(flow_id, action)

    # Get and check stored flow state
    flow_info = await flow_mgr.get_info(flow_id)
    assert flow_info.flow_id == flow_id
    assert flow_info.created_at is not None
    assert flow_info.expires_at is None
    assert flow_info.session_id is None
    assert flow_info.kind == "login"
    assert set(flow_info.state.keys()) == {"kind", "email"}
    assert flow_info.state["kind"] == "signup"
    assert flow_info.state["email"] == EMAIL
    assert flow_info.is_ended is False

    # Ensure a new session was created, with the correct assertion
    session = get_current_session()
    assert session.session_id != initial_session_id  # New session
    assert session.current_user_id is None  # No user yet

    assert len(session.assertions) == 1
    [email_assertion] = session.assertions
    assert isinstance(email_assertion, Assertion)
    assert isinstance(email_assertion.params, assertions.EmailAuth)
    assert email_assertion.params.email_address == EMAIL

    # ----------------------------------------------------------------
    # Confirm account creation
    # ----------------------------------------------------------------

    action = FlowAction({"kind": "signup-confirm", "display_name": "Test User"})
    await flow_mgr.execute(flow_id, action)

    # Completed flows get deleted automatically
    with pytest.raises(ObjectNotFound):
        await flow_mgr.get_info(flow_id)

    # Verify that the user was indeed created
    user = await repo.user.get_by_email(EMAIL)
    assert isinstance(user, User)

    # Verify that the new user is marked as "current" on the session
    session = get_current_session()
    assert session.current_user_id == user.id

    # Verify session assertions
    assert len(session.assertions) == 1
    [email_assertion] = session.assertions
    assert isinstance(email_assertion, Assertion)
    assert isinstance(email_assertion.params, assertions.EmailAuth)
    assert email_assertion.params.email_address == EMAIL
