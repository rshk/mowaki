"""
Tests for app.svc.webapi.routes.auth
"""

from email.message import Message

import pytest
from fastapi.security.utils import get_authorization_scheme_param

from app.const import SESSION_TOKEN_HEADER
from app.core.authn.flows.login.states import (
    InitialState,
    OtpPendingState,
)
from app.core.authn.session import get_session_from_token
from app.svc.webapi.authn import flow_mgr, flow_registry
from app.types.auth.session import SessionToken
from tests.svc.webapi.conftest import AsyncTestClient
from tests.utils.session import set_request_context_from_session_id

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("database_schema"),
]


async def test_email_otp_flow_happy_path(
    testclient: AsyncTestClient,
    email_outbox: list[Message],
):

    # Configuration
    EMAIL = "user@example.com"

    # ----------------------------------------------------------------
    # Initiate a login flow
    # ----------------------------------------------------------------

    resp = await testclient.post("/auth/flow/init/login")

    # Validate response ----------------------------------------------
    assert resp.status_code == 200
    assert SESSION_TOKEN_HEADER in resp.headers  # New session

    obj = resp.json()
    assert set(obj.keys()) == {
        "flow_id",
        "created_at",
        "expires_at",
        "kind",
        "status",
        "challenge",
    }
    assert obj["flow_id"] is not None
    assert obj["created_at"] is not None
    assert obj["expires_at"] is not None
    assert obj["kind"] == "login"
    assert obj["status"] == "IN_PROGRESS"
    assert set(obj["challenge"].keys()) == {"kind", "actions"}
    assert obj["challenge"]["kind"] == "login-init"
    assert isinstance(obj["challenge"]["actions"], list)
    # TODO: make sure the correct action is listed

    # ----------------------------------------------------------------
    # Check that the test client is handling token-setting correctly
    # TODO: move this to a test *for the test client*
    # ----------------------------------------------------------------
    assert "Authorization" in testclient.headers
    scheme, credentials = get_authorization_scheme_param(
        testclient.headers["Authorization"]
    )
    assert scheme.lower() == "bearer"
    assert resp.headers[SESSION_TOKEN_HEADER] == credentials
    # ----------------------------------------------------------------

    # Inspect session ------------------------------------------------
    token = SessionToken(resp.headers[SESSION_TOKEN_HEADER])
    session = await get_session_from_token(token)
    session_id = session.session_id
    assert len(session.assertions) == 0

    # Store flow ID --------------------------------------------------
    flow_id = obj["flow_id"]

    # Inspect flow ---------------------------------------------------
    async with set_request_context_from_session_id(session_id):
        flow = await flow_mgr.get_info(flow_id)
        assert flow.kind == "login"
        assert flow.state["kind"] == "initial"
        assert flow.session_id is None

        flowp = await flow_registry[flow.kind].load(flow.state)
        assert isinstance(flowp, InitialState)

    # ----------------------------------------------------------------
    # Initiate email-based OTP
    # ----------------------------------------------------------------

    resp = await testclient.post(
        f"/auth/flow/{flow_id}",
        json={"kind": "start-email-otp", "email": "user@example.com"},
    )

    # Validate response
    assert resp.status_code == 200
    assert SESSION_TOKEN_HEADER not in resp.headers  # No new session

    obj = resp.json()
    assert set(obj.keys()) == {
        "flow_id",
        "created_at",
        "expires_at",
        "kind",
        "status",
        "challenge",
    }
    assert obj["flow_id"] == flow_id
    assert obj["kind"] == "login"
    assert obj["status"] == "IN_PROGRESS"
    assert set(obj["challenge"].keys()) == {"kind", "actions"}
    assert obj["challenge"]["kind"] == "otp-verify"
    assert isinstance(obj["challenge"]["actions"], list)
    # TODO: inspect actions

    # Inspect flow ---------------------------------------------------
    async with set_request_context_from_session_id(session_id):
        flow = await flow_mgr.get_info(flow_id)
        assert flow.kind == "login"
        assert set(flow.state.keys()) == {"kind", "email", "otp", "retries_left"}
        assert flow.state["kind"] == "email-otp-pending"
        assert flow.state["email"] == EMAIL
        assert flow.session_id is None

        flowp = await flow_registry[flow.kind].load(flow.state)
        assert isinstance(flowp, OtpPendingState)

    # Check that the OTP email was sent ------------------------------
    assert len(email_outbox) == 1
    # TODO: inspect the sent email, make sure it contains the correct OTP

    async with set_request_context_from_session_id(session_id):
        flow = await flow_mgr.get_info(flow_id)
        assert flow.kind == "login"
        assert flow.state["kind"] == "email-otp-pending"

        flowp = await flow_registry[flow.kind].load(flow.state)
        assert isinstance(flowp, OtpPendingState)
        assert flowp.email == "user@example.com"
        assert flowp.otp is not None
