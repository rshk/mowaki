import uuid
from datetime import UTC, datetime

from app.types.auth.assertions import Assertion, AssertionID, EmailAuth


def test_load_assertion():
    data = {
        "id": "ce1aac09-6ff7-4207-9f7b-b12de0d7eccd",
        "created_at": "2026-08-24T23:38:22Z",
        "params": {
            "kind": "email-auth",
            "email_address": "foo@example.com",
        },
    }

    # assertion = Assertion(**data)
    assertion = Assertion.model_validate(data)

    assert isinstance(assertion, Assertion)
    assert assertion.id == AssertionID(
        uuid.UUID("ce1aac09-6ff7-4207-9f7b-b12de0d7eccd")
    )
    assert assertion.created_at == datetime(2026, 8, 24, 23, 38, 22, tzinfo=UTC)
    assert isinstance(assertion.params, EmailAuth)
    assert assertion.params.email_address == "foo@example.com"


def test_dump_assertion():
    assertion = Assertion(
        id=AssertionID(uuid.UUID("ce1aac09-6ff7-4207-9f7b-b12de0d7eccd")),
        created_at=datetime(2026, 8, 24, 23, 38, 22, tzinfo=UTC),
        params=EmailAuth(email_address="foo@example.com"),
    )
    data = assertion.model_dump(mode="json")

    assert data == {
        "id": "ce1aac09-6ff7-4207-9f7b-b12de0d7eccd",
        "created_at": "2026-08-24T23:38:22Z",
        "expires_at": None,
        "params": {
            "kind": "email-auth",
            "email_address": "foo@example.com",
        },
    }
