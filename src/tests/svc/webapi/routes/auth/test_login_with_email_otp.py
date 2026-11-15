"""
Tests for app.svc.webapi.routes.auth
"""

from typing import Annotated, Literal

import pytest
from pydantic import BaseModel, Discriminator, TypeAdapter

from app.core.authn.flows.login.flow import InitialState, OtpPendingState, StartOTPAction
from app.core.authn.session import get_session_from_token
from app.lib.flows.flow import FlowStateBlock
from app.lib.flows.types import FlowAction, FlowChallenge
from httpx2 import AsyncClient
from fastapi.security.utils import get_authorization_scheme_param

from app.types.auth.session import SessionToken
from tests.utils.session import set_request_context_from_session_id
from app.svc.webapi.authn import flow_registry, flow_repo

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("database_schema"),
]


async def test_email_otp_flow(subtests: pytest.Subtests, testclient: AsyncClient, email_outbox):
    resp = await testclient.post("/auth/flow/init/login")
    assert resp.status_code == 200

    obj = resp.json()
    assert obj["flow_id"] is not None
    assert obj["created_at"] is not None
    assert obj["expires_at"] is not None
    assert obj["kind"] == "login"
    assert obj["status"] == "IN_PROGRESS"
    assert set(obj["challenge"].keys()) == {"kind", "actions"}
    assert obj["challenge"]["kind"] == "login-init"
    assert isinstance(obj["challenge"]["actions"], list)
    # TODO: make sure the correct action is listed

    # Ensure a session token has been saved on the client.
    assert "Authorization" in testclient.headers

    # Extract session token from the header so we can retrieve the
    # current session for inspection.
    scheme, credentials = get_authorization_scheme_param(
        testclient.headers["Authorization"]
    )
    assert scheme.lower() == "bearer"
    token = SessionToken(credentials)
    session = await get_session_from_token(token)
    session_id = session.session_id

    flow_id = obj["flow_id"]

    # Make sure the flow has been created
    async with set_request_context_from_session_id(session_id):
        flow = await flow_repo.get(flow_id)
        assert flow.kind == "login"
        assert flow.state["kind"] == "initial"

        flowp = await flow_registry[flow.kind].load(flow.state)

        assert isinstance(flowp, InitialState)

    resp = await testclient.post(
        f"/auth/flow/{flow_id}", json={"kind": "start-email-otp", "email": "user@example.com"}
    )
    assert resp.status_code == 200

    obj = resp.json()
    assert obj["flow_id"] == flow_id
    assert obj["status"] == "IN_PROGRESS"
    assert set(obj["challenge"].keys()) == {"kind", "actions"}
    assert obj["challenge"]["kind"] == "otp-verify"

    # Check that the OTP email was sent
    assert len(email_outbox) == 1
    # TODO: inspect the sent email, make sure it contains the OTP

    async with set_request_context_from_session_id(session_id):
        flow = await flow_repo.get(flow_id)
        assert flow.kind == "login"
        assert flow.state["kind"] == "start-email-otp"

        flowp = await flow_registry[flow.kind].load(flow.state)
        assert isinstance(flowp, OtpPendingState)
        assert flowp.email == "user@example.com"
        assert flowp.otp is not None

#         state = flowp.dump()

#         assert state["email"] == "user@example.com"
#         assert state["code"] is not None

#         otp = state["code"]  # needed later...

#     with subtests.test("Submit OTP"):
#         resp = await testclient.post(f"/auth/flow/{flow_id}", json={"code": otp})
#         assert resp.status_code == 200

#         obj = resp.json()
#         assert obj["status"] == "SUCCESS"
#         assert obj["flow"] is None

#         # Check that a new assertion has been added to the session
#         session = await get_session(session_id)
#         assert len(session.assertions) == 1
#         [assertion] = session.assertions
#         assert isinstance(assertion.params, EmailAuth)
#         assert assertion.params.email_address == "user@example.com"
#         assert assertion.params.user_id is None
#         assert session.current_user_id is None


# async def test_email_otp_flow_with_params(
#     subtests, testclient: AsyncClient, email_outbox
# ):
#     EMAIL_ADDR = "user@example.com"

#     with subtests.test("Initialize flow"):
#         resp = await testclient.post(
#             "/auth/flow/init/email-otp-auth", json={"email": EMAIL_ADDR}
#         )
#         assert resp.status_code == 200

#         obj = resp.json()
#         assert obj["flow_id"] is not None
#         assert obj["created_at"] is not None
#         assert obj["expires_at"] is not None
#         assert obj["kind"] == "email-otp-auth"
#         assert obj["challenge"] == {"next_step": "CODE_REQUIRED"}
#         assert obj["status"] == "in-progress"

#         # Ensure a session token has been saved on the client.
#         assert "Authorization" in testclient.headers

#         # Extract session token from the header so we can retrieve the
#         # current session for inspection.
#         scheme, credentials = get_authorization_scheme_param(
#             testclient.headers["Authorization"]
#         )
#         assert scheme.lower() == "bearer"
#         token = SessionToken(credentials)
#         session = await get_session_from_token(token)
#         session_id = session.session_id

#         flow_id = obj["flow_id"]

#         # Check that the OTP email was sent
#         assert len(email_outbox) == 1
#         # TODO: inspect the sent email, make sure it contains a valid OTP

#     async with set_request_context_from_session_id(session_id):
#         flow = await get_flow(flow_id)
#         flowp = get_flow_processor(flow.kind)

#         assert flowp is EMAIL_OTP_AUTH_FLOW_PROCESSOR
#         assert isinstance(flowp, FlowProcessor)
#         state = flowp.state_model.model_validate(flow.state)
#         assert isinstance(state, EmailOTPAuthFlowState)

#         assert state.email == EMAIL_ADDR
#         otp = state.code
#         assert otp is not None

#     with subtests.test("Submit OTP"):
#         resp = await testclient.post(f"/auth/flow/{flow_id}", json={"code": otp})
#         assert resp.status_code == 200

#         obj = resp.json()
#         assert obj["status"] == "SUCCESS"
#         assert obj["flow"] is None

#         # Check that a new assertion has been added to the session
#         session = await get_session(session_id)
#         assert len(session.assertions) == 1
#         [assertion] = session.assertions
#         assert isinstance(assertion.params, EmailAuth)
#         assert assertion.params.email_address == EMAIL_ADDR
#         assert assertion.params.user_id is None
#         assert session.current_user_id is None
