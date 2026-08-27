import uuid
from datetime import UTC, datetime
from typing import Any, NewType

from pydantic import Field

from app.lib.keygen import generate_uuid
from app.lib.models import BaseModel
from app.types.auth.session import SessionID

FlowID = NewType("FlowID", uuid.UUID)
FlowKind = NewType("FlowKind", str)
FlowState = NewType("FlowState", dict[str, Any])
FlowAction = NewType("FlowAction", dict[str, Any])


class AuthFlow(BaseModel):
    """Authentication flow"""

    flow_id: FlowID = Field(default_factory=lambda: FlowID(generate_uuid()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    session_id: SessionID | None = None
    kind: FlowKind
    state: FlowState
    is_completed: bool = False
