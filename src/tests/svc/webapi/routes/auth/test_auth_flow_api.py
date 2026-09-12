"""
Tests for app.svc.webapi.routes.auth
"""

import pytest
from fastapi.security.utils import get_authorization_scheme_param
from httpx2 import AsyncClient

from app.core.authn.flows.actions import get_flow, get_flow_processor
from app.core.authn.flows.email_otp_auth import EmailOTPAuthFlowProcessor
from app.core.authn.session import get_session, get_session_from_token
from app.types.auth.assertions import EmailAuth
from app.types.auth.session import SessionToken
from tests.utils.session import set_request_context_from_session_id

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("database_schema"),
]


async def test_email_otp_flow(subtests, testclient: AsyncClient, email_outbox):
    with subtests.test("Initialize flow"):
        resp = await testclient.post("/auth/flow/init/email-otp-auth")
        assert resp.status_code == 200

        obj = resp.json()
        assert obj["flow_id"] is not None
        assert obj["created_at"] is not None
        assert obj["expires_at"] is not None
        assert obj["kind"] == "email-otp-auth"
        assert obj["challenge"] == {"state": "EMAIL_REQUIRED"}
        assert obj["status"] == "in-progress"

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

    with subtests.test("Provide email address"):
        resp = await testclient.post(
            f"/auth/flow/{flow_id}", json={"email": "user@example.com"}
        )
        assert resp.status_code == 200

        obj = resp.json()
        assert obj["status"] == "IN_PROGRESS"
        assert obj["flow"]["flow_id"] == flow_id
        assert obj["flow"]["challenge"] == {"state": "CODE_REQUIRED"}
        assert obj["flow"]["status"] == "in-progress"

        # Check that the OTP email was sent
        assert len(email_outbox) == 1
        # TODO: inspect the sent email, make sure it contains a valid OTP

    async with set_request_context_from_session_id(session_id):
        flow = await get_flow(flow_id)
        flowp = get_flow_processor(flow)

        assert isinstance(flowp, EmailOTPAuthFlowProcessor)
        assert flowp.state.email == "user@example.com"
        otp = flowp.state.code
        assert otp is not None

    with subtests.test("Submit OTP"):
        resp = await testclient.post(f"/auth/flow/{flow_id}", json={"code": otp})
        assert resp.status_code == 200

        obj = resp.json()
        assert obj["status"] == "SUCCESS"
        assert obj["flow"] is None

        # Check that a new assertion has been added to the session
        session = await get_session(session_id)
        assert len(session.assertions) == 1
        [assertion] = session.assertions
        assert isinstance(assertion.params, EmailAuth)
        assert assertion.params.email_address == "user@example.com"
        assert assertion.params.user_id is None
        assert session.current_user_id is None
