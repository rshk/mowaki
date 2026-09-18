import uuid
from datetime import UTC, datetime
from typing import NewType

from pydantic import Field

from app.lib.keygen import generate_uuid
from app.lib.models import BaseModel
from app.types.auth.session import SessionID

from ..base import JSONObject

FlowID = NewType("FlowID", uuid.UUID)
FlowKind = NewType("FlowKind", str)
FlowState = NewType("FlowState", JSONObject)
FlowAction = NewType("FlowAction", JSONObject)
FlowChallenge = NewType("FlowChallenge", JSONObject)


class AuthFlow(BaseModel):
    """Authentication flow"""

    flow_id: FlowID = Field(default_factory=lambda: FlowID(generate_uuid()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    session_id: SessionID | None = None
    kind: FlowKind
    state: FlowState
    is_completed: bool = False
