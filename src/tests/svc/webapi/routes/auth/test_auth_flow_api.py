"""
Tests for app.svc.webapi.routes.auth
"""

import pytest
from httpx2 import AsyncClient

# from app.svc.webapi import app
# from fastapi.testclient import TestClient


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
        assert obj["challenge"] == {}
        assert obj["status"] == "in-progress"

        assert testclient.headers["Authorization"].startswith("Bearer ")

        flow_id = obj["flow_id"]

    with subtests.test("Provide email address"):
        resp = await testclient.post(
            f"/auth/flow/{flow_id}", json={"email_address": "user@example.com"}
        )
        assert resp.status_code == 200

        obj = resp.json()
        assert obj["status"] == "IN_PROGRESS"
        assert obj["flow"]["flow_id"] == flow_id
        assert obj["flow"]["challenge"] == {}
        assert obj["flow"]["status"] == "in-progress"

        assert len(email_outbox) == 1
        # TODO: inspect the sent email, make sure it contains a valid OTP

        # TODO: retrieve OTP from the database
